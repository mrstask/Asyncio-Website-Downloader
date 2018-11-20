import aiohttp
import asyncio
from pprint import pprint
import re
from base_handler_class import BaseHandler

start_link = ['http://megamillions.com.ua/wp-content/cache/autoptimize/js/autoptimize_0bda8df07439e32b5d7c6e29dc61b480.js','js']


class JsHandler(BaseHandler):
    def find_sw_equal_links(self):
        match = re.findall(r'=[\'\"]?((http|//)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def find_sw_colon_links(self):
        match = re.findall(r':[\'\"]?((http|//)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def find_sw_space_links(self):
        match = re.findall(r'\s[\'\"]?((http|//)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]
        match = re.findall(r'\s((http)[^\n >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]


    def find_sw_bracket_links(self):
        match = re.findall(r'\(((http|//)[^\)]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

# todo cleenup links






async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            if url[1] == 'js':
                js = JsHandler()
                if await js.request_handler(response):
                    # js.find_sw_equal_links()
                    js.find_sw_colon_links()
                    # js.find_sw_space_links()
                    # js.find_sw_bracket_links()
                    pprint(js.links)


asyncio.run(worker(start_link))