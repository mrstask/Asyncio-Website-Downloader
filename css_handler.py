import aiohttp
import asyncio
import re
from main import write_binary, check_type, start_url, connection, create_engine, urls_table
from urllib.parse import unquote
from pprint import pprint
import json

link = ['http://megamillions.com.ua/wp-content/plugins/so-widgets-bundle/widgets/button/css/style.css', 'css']


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            # print(response.url, response.status)
            if url[1] == 'css':
                await css_handler(response)


async def css_handler(response):
    if response.status == 200:
        url = response.url
        # print(url.parent)
        await write_binary(response, response.url)
        response = await response.text()
        # links = re.findall(r"url\(\'(.*?)\'\)", response) old one
        # lets find all urls in url tags
        links = re.findall(r"url\((.*?)\)", response)
        result_links = dict()
        for link in links:
            new_link = unquote(link)
            new_link = new_link.replace('\\', '')
            for entity in ['&', '#']:
                if entity in new_link:
                    new_link = new_link.split(entity)[0]

            # todo check this on html handler
            if '?f=' in new_link:
                new_link = new_link.split('?f=')[1:]
                new_link = url.with_path(new_link)
            # if url starts with . lets find absolute url
            if new_link.startswith('.'):
                # count steps back in response url to find absolute path for url by counting dots in url
                steps_back = new_link.split('/')[0].count('.')
                # making steps back from current path
                path = url.parts[:-steps_back]
                # joining url back without first slash
                path = '/'.join(path[1:])
                # getting absolute url together
                result_links[(str(url.with_path(path + new_link[steps_back:])))] = link
            elif new_link.startswith('/'):
                # if link is relative and in the same folder that url is, make that link absolute
                print('link started with /', url.with_path(new_link[1:]))
                result_links[url.with_path(new_link[1:])] = link
            elif new_link.startswith('http'):
                if url.host in new_link:
                    result_links[new_link] = link
            else:
                # find links in all wierd occurencies
                match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', new_link)
                # great possibility of error generation
                if not match:
                    result_links[str(url.parent) + '/' + new_link] = link
                if match:
                    for item in match[0]:
                        if '/' in item:
                            result_links[item] = link
        for key in list(result_links):
            if not key.startswith(start_url):
                result_links.pop(key, None)
        result_links = check_type(result_links)
        async with create_engine(**connection) as engine:
            async with engine.acquire() as conn:
                await conn.execute(urls_table.insert().values({'url': str(url),
                                                               'type': 'css',
                                                               'title': 'None',
                                                               'description': 'None',
                                                               'text': 'None',
                                                               'text_len': 0,
                                                               'html': json.dumps(response),
                                                               'html_len': len(response),
                                                               'a_links_len': 0,
                                                               'links_inbound': json.dumps(result_links),
                                                               'links_inbound_len': len(result_links.keys()),
                                                               'links_outbound': 'None',
                                                               'links_outbound_len': 0,
                                                               'all_links': 'None',
                                                               'all_links_len': 0}))
        print(result_links)
        return True
    elif response.status == 404:
        print('bad_url')


print(asyncio.run(worker(link)))