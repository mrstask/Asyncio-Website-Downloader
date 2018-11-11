import aiohttp
import asyncio
import re
from main import write_binary, check_type, start_url, connection, create_engine, urls_table
from urllib.parse import unquote
from pprint import pprint
import json

link = ['http://megamillions.com.ua/wp-content/themes/maskitto-light/css/style.css', 'css']


class CssHandler:
    def __init__(self):
        self.result_links = dict()
        self.response_text = object()
        self.links = list()
        self.url = object()

    async def css_handler(self, response):
        if response.status == 200:
            self.url = response.url
            # print(url.parent)
            # await write_binary(response, response.url)
            self.response_text = await response.text()
            # lets find all urls in url tags
            self.links = re.findall(r"url\((.*?)\)", self.response_text)
        elif response.status == 404:
            print('bad_url')

#     def prepare_n_rm(self, link):
#         new_link = unquote(link)
#         new_link = new_link.replace('\\', '')
#         for entity in ['&', '#']:
#             if entity in new_link:
#                 new_link = new_link.split(entity)[0]
#         return new_link
#
# # todo check this on html handler
#     def link_parameter_f(self, new_link):
#         new_link = new_link.split('?f=')[1:]
#         return self.url.with_path(new_link)
#
#     def link_dot(self, new_link):
#         # count steps back in response url to find absolute path for url by counting dots in url
#         steps_back = new_link.split('/')[0].count('.')
#         # making steps back from current path
#         path = self.url.parts[:-steps_back]
#         # joining url back without first slash
#         path = '/'.join(path[1:])
#         # getting absolute url together
#         self.result_links[(str(self.url.with_path(path + new_link[steps_back:])))] = link
#
#     def link_slash(self, new_link):
#         # if link is relative and in the same folder that url is, make that link absolute
#         self.result_links[self.url.with_path(new_link[1:])] = link
#
#     def link_http(self, new_link):
#         if self.url.host in new_link:
#             self.result_links[new_link] = link
#         else:
#             # find links in all wierd occurencies
#             match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', new_link)
#             # great possibility of error generation
#             if not match:
#                 self.result_links[str(self.url.parent) + '/' + new_link] = link
#             if match:
#                 for item in match[0]:
#                     if '/' in item:
#                         self.result_links[item] = link
#             for key in list(self.result_links.keys()):
#                 if not key.startswith(start_url):
#                     self.result_links.pop(key, None)
#
#     def write_db(self):
#         async with create_engine(**connection) as engine:
#             async with engine.acquire() as conn:
#                 await conn.execute(urls_table.insert().values({'url': str(self.url),
#                                                                'type': 'css',
#                                                                'title': 'None',
#                                                                'description': 'None',
#                                                                'text': 'None',
#                                                                'text_len': 0,
#                                                                'html': json.dumps(self.response),
#                                                                'html_len': len(self.response),
#                                                                'a_links_len': 0,
#                                                                'links_inbound': json.dumps(self.result_links),
#                                                                'links_inbound_len': len(self.result_links.keys()),
#                                                                'links_outbound': 'None',
#                                                                'links_outbound_len': 0,
#                                                                'all_links': 'None',
#                                                                'all_links_len': 0}))
#
    def iterator(self):
        for link in self.links:
            new_link = self.prepare_n_rm(link)
            if '?f=' in new_link:
                new_link = self.link_parameter_f(new_link)
            if new_link.startswith('.'):
                self.link_dot(new_link)
            elif new_link.startswith('/'):
                self.link_slash(new_link)
            elif new_link.startswith('http'):
                self.link_http(new_link)
        result_links = check_type(self.result_links)
        return result_links


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            # print(response.url, response.status)
            if url[1] == 'css':
                css = CssHandler()
                await css.css_handler(response)
                css.iterator()


asyncio.run(worker(link))