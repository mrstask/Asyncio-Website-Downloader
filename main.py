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
# from html_handler import html_handler

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
    # creating path from host and path
    path = url.host+url.path
    # removing filename
    directory = path.split('/')[:-1]
    directory = '/'.join(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        async with aiofiles.open(path+ext, mode='wb') as f:
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


def check_type(links_dict):
    condition_list = ['#', 'trackback']
    list_urls = dict()
    for link, source in links_dict.items():
        link = unquote(link)
        if link.endswith(('.jpg', '.png', '.jpeg', '.exif', '.tiff', '.gif', '.bmp', '.ico')):
            list_urls[link] = ['img', source]
        elif '.js' in link:
            list_urls[link] = ['js', source]
        elif '.css' in link:
            list_urls[link] = ['css', source]
        elif '.xml' in link:
            list_urls[link] = ['xml', source]
        elif link.endswith(('.ttf', '.woff', '.woff2', '.svg', '.eot')):
            list_urls[link] = ['font', source]
        elif '?' in link:
            list_urls[link] = ['parametrized', source]
        elif any(word in link for word in condition_list):
            list_urls[link] = ['shitty', source]
        else:
            list_urls[link] = ['html', source]
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

