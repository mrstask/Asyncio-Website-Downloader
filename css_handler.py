import aiohttp
import asyncio
import re
from main import write_binary
from pprint import pprint

link = ['http://megamillions.com.ua/wp-content/themes/maskitto-light/css/style.css', 'css']


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            # print(response.url, response.status)
            if url[1] == 'css':
                await css_handler(response)


async def css_handler(response):
    if response.status == 200:
        url = response.url
        # await write_binary(response, str(response.url))
        response = await response.text()
        # links = re.findall(r"url\(\'(.*?)\'\)", response) old one
        # lets find all urls in url tags
        links = re.findall(r"url\((.*?)\)", response)
        result_links = set()
        for link in links:
            link = link.replace('\\', '')
            # if url starts with . lets find absolute url
            if link.startswith('.'):
                # count steps back in response url to find absolute path for url by counting dots in url
                steps_back = link.split('/')[0].count('.')
                # making steps back from current path
                path = url.parts[:-steps_back]
                # joining url back without first slash
                path = '/'.join(path[1:])
                # getting absolute url together
                result_links.add(str(url.with_path(path + link[steps_back:])))
            elif link.startswith('/'):
                # if link is relative and in the same folder that url is, make that link absolute
                print('link started with /', url.with_path(link[1:]))
                result_links.add(url.with_path(link[1:]))
            elif link.startswith('http'):
                if url.host in link:
                    result_links.add(link)
            else:
                # find links in all wierd occurencies
                match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', link)
                for item in match[0]:
                    if '/' in item:
                        result_links.add(item)
        print(result_links)


asyncio.run(worker(link))