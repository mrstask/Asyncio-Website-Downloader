import aiohttp
import asyncio
import os
import html
import re
import json
import codecs
from pprint import pprint
from urllib.parse import unquote
from base_handler_class import BaseHandler


start_link = ['http://megamillions.com.ua/wp-json/oembed/1.0/embed?url=http://megamillions.com.ua/', 'json']


class JsonHandler(BaseHandler):
    def json_find_links(self):
        response = self.response_text.encode().decode('utf-8-sig')
        response.replace(os.linesep, '')
        response = json.loads(response, strict=False)
        for key, item in response.items():
            item = str(item)
            if item.startswith('http'):
                self.links.add(item)
            else:
                match = re.findall(r'=[\'\"]?((http|//)[^\'\" >]+)', item)
                [self.links.add(x[0]) for x in match]


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            if url[1] == 'json':
                json_instance = JsonHandler()
                if await json_instance.request_handler(response):
                    json_instance.json_find_links()
                    json_instance.base_iterator()
                    await json_instance.write_binary('index.json')
                    pprint(json_instance.links)
                    print('****outbound****')
                    pprint(json_instance.outbound)
                    print('****inbound****')
                    pprint(json_instance.check_type(json_instance.inbound))

if __name__ == '__main__':
    asyncio.run(worker(start_link))