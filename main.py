import aiohttp
import asyncio
import time
import json
import re
import lxml
import os
import aiofiles
from lxml import html
from urllib.parse import unquote, urlparse
import html2text
from pprint import pprint
from aiopg.sa import create_engine
from db import connection, domains_table, urls_table

from settings import auth_login, auth_password, ssl, start_url, domain

start_time = time.time()
auth = aiohttp.BasicAuth(login=auth_login, password=auth_password)


# async def worker(q):
#     async with aiohttp.ClientSession(auth=auth) as session:
#         while q.qsize() > 0:
#             url = await q.get()  # из очереди
#             if url[1] == 'shitty':
#                     bad_urls[url[0]] = 'shitty'
#             else:
#                 async with session.get(url[0]) as response:
#                     print(response.url, response.status)
#                     if url[1] == 'html':
#                         await html_handler(response)
#                     elif url[1] == 'img':
#                         await img_handler(response)
#                     elif url[1] == 'js':
#                         await js_handler(response)
#                     elif url[1] == 'css':
#                         await css_handler(response, q)
#                     elif url[1] == 'xml':
#                         await xml_handler(response)



parsed_urls = dict()
bad_urls = dict()
queue = set()
qu = asyncio.Queue()


async def write_binary(response, url, ext=''):
    uri = urlparse(unquote(url))
    path = uri.path + ext
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        async with aiofiles.open(path, mode='wb') as f:
            await f.write(await response.read())
            await f.close()
    except OSError:
        bad_urls[url] = 'OSError'


def get_a_links(response, start_url):
    try:
        links = html.fromstring(response)
        a_links = set(links.xpath('//a/@href'))
        a_links = [x for x in a_links if x.startswith('/') or x.startswith(start_url)]
        # find all links that started with ='|"http|/
        match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', response)
        # get just first group in occurrence
        match = [x[0] for x in match]
        # remove urls with //
        match = [x for x in match if not x.startswith('//')]
        # replace relative url with absolute
        match = [x if not x.startswith('/') else start_url+x for x in match]
        # get outbound links
        outbound_links = [x for x in match if not x.startswith(start_url)]
        # remove outbound links
        match = [x for x in match if x.startswith(start_url)]
        # remove duplicates
        all_links = set()
        # split concatenated urls
        for x in match:
            if ',' in x:
                splitted_urls = x.split(',')
                for item in splitted_urls:
                    if not item.startswith(start_url):
                        item = start_url+item
                        all_links.add(item)
                    all_links.add(item)
            else:
                all_links.add(x)
        return [a_links, all_links, outbound_links]

    except lxml.etree.ParserError:
        return False


def check_type(links_list):
    condition_list = ['?', '#', 'trackback']
    list_urls = list()
    for link in links_list:
        link = unquote(link)
        if link.endswith(('.jpg', '.png', '.jpeg', '.exif', '.tiff', '.gif', '.bmp', '.ico')):
            list_urls.append([link, 'img'])
        elif '.js' in link:
            list_urls.append([link, 'js'])
        elif '.css' in link:
            list_urls.append([link, 'css'])
        elif '.xml' in link:
            list_urls.append([link, 'xml'])
        elif '.php' in link:
            list_urls.append([link, 'php'])
        elif any(word in link for word in condition_list):
            list_urls.append([link, 'shitty'])
        else:
            list_urls.append([link, 'html'])
    return list_urls


def get_meta(plain_html):
    h = html2text.HTML2Text()
    h.ignore_links = True
    plain_text = h.handle(plain_html)
    text_obj = html.fromstring(plain_html.lower())
    try:
        title = text_obj.xpath('//title/text()')[0].strip()
    except Exception as e:
        print('title')
        print(e)
        print(type(e))
        title = 'None'
    try:
        description = text_obj.xpath('//meta[@name="description"]/@content')[0].strip()
    except Exception as e:
        print('description')
        print(e)
        print(type(e))
        description = 'None'
    return [title, description, plain_text, plain_html]


async def html_handler(response):
    try:
        if response.status == 200:
            url = str(response.url)
            response_text = await response.text()
            meta = get_meta(response_text)
            links = get_a_links(response_text, start_url)
            typized_all_links = check_type(links[1])
            async with create_engine(**connection) as engine:
                async with engine.acquire() as conn:
                        await conn.execute(urls_table.insert().values({'url': url,
                                                                       'type': 'html',
                                                                       'title': meta[0],
                                                                       'description': meta[1],
                                                                       'text': json.dumps(meta[2]),
                                                                       'text_len': len(meta[2]),
                                                                       'html': json.dumps(meta[3]),
                                                                       'html_len': len(meta[3]),
                                                                       'a_links_len': len(links[0]),
                                                                       'links_inbound': list(links[0]),
                                                                       'links_inbound_len': len(links[0]),
                                                                       'links_outbound': list(links[2]),
                                                                       'links_outbound_len': len(links[2]),
                                                                       'all_links': list(links[1]),
                                                                       'all_links_len': len(links[1])}))
            await write_binary(response, url, 'index.html')
            pprint(typized_all_links)
        elif response.status in [500, 502]:
            await qu.put([str(response.url), 'html'])
        else:
            bad_urls[str(response.url)] = response.status
    except ValueError:
        bad_urls[str(response.url)] = 'ValueError'
    except TypeError:
        bad_urls[str(response.url)] = 'TypeError'
    except AttributeError:
        print('ValueError', response.url)
        print(response)
    except Exception as e:
        print(e)


async def main():
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get(start_url) as response:
            await html_handler(response)
            async with create_engine(**connection) as engine:
                async with engine.acquire() as conn:
                        await conn.execute(domains_table.insert().values({'process': True,
                                                                          'ssl': ssl,
                                                                          'domain': domain}))



    #
    # tasks = []
    # for _ in range(10):
    #     task = asyncio.Task(worker(qu))
    #     tasks.append(task)
    #
    # await asyncio.gather(*tasks)

if __name__ =='__main__':
    asyncio.run(main())
    print("--- %s seconds ---" % (time.time() - start_time))

