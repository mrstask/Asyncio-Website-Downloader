import aiohttp
import asyncio
import re
from pprint import pprint
from base_handler_class import BaseHandler


# start_link = ['http://megamillions.com.ua/wp-content/cache/autoptimize/js/autoptimize_0bda8df07439e32b5d7c6e29dc61b480.js','js']
start_link = ['http://megamillions.com.ua/','js']


class JsHandler(BaseHandler):
    def js_find_sw_equal_links(self):
        match = re.findall(r'=[\'\"]?((http|//)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def js_find_sw_colon_links(self):
        match = re.findall(r':[\'\"]?((http)[^)\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def js_find_sw_space_links(self):
        match = re.findall(r'\s[\'\"]?((http|//)[^\'\" \n>]+)', self.response_text)
        [self.links.add(x[0]) for x in match]
        match = re.findall(r'\s((http)[^\n\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def js_find_sw_bracket_links(self):
        match = re.findall(r'\(((http|//)[^\)]+)', self.response_text)
        [self.links.add(x[0]) for x in match]


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            if url[1] == 'js':
                js = JsHandler()
                if await js.request_handler(response):
                    js.js_find_sw_equal_links()
                    js.js_find_sw_colon_links()
                    js.js_find_sw_space_links()
                    js.js_find_sw_bracket_links()
                    js.base_iterator()
                    # html_instance.inbound = html_instance.check_type(html_instance.inbound)

                    # pprint(js.links)
                    print('****outbound****', len(js.outbound))
                    pprint(js.outbound)
                    print('****inbound****', len(js.inbound))
                    pprint(js.check_type(js.inbound))

if __name__ == '__main__':
    asyncio.run(worker(start_link))