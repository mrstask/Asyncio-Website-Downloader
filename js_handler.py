import aiohttp
import asyncio
import html
import re
from pprint import pprint
from urllib.parse import unquote
from base_handler_class import BaseHandler


start_link = ['http://megamillions.com.ua/wp-content/cache/autoptimize/js/autoptimize_0bda8df07439e32b5d7c6e29dc61b480.js','js']


class JsHandler(BaseHandler):
    def js_find_sw_equal_links(self):
        match = re.findall(r'=[\'\"]?((http|//)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def js_find_sw_colon_links(self):
        match = re.findall(r':[\'\"]?((http|//)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def js_find_sw_space_links(self):
        match = re.findall(r'\s[\'\"]?((http|//)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]
        match = re.findall(r'\s((http)[^\n >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def js_find_sw_bracket_links(self):
        match = re.findall(r'\(((http|//)[^\)]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def js_iterator(self):
        listation = list(self.links)
        for self.link in listation:
            # will remove hash or & parameters and create new_link
            self.new_link = html.unescape(unquote(self.link))
            if self.new_link.startswith('\\\\'):
                self.rm_backslash()
            if self.new_link.startswith('//'):
                self.startsw_double_slash()
            if '\/' in self.new_link:
                self.new_link = self.rm_unescaped_in_link()
            if '#' in self.new_link:
                self.rm_hash()
            if '\n' in self.new_link:
                self.new_link = self.rm_n_in_link()
            if any(x in self.new_link for x in ['\'', '\"', '*', ')']):
                self.new_link = self.rm_wierd_stuff_in_link()
            if '?f=' in self.new_link:
                result = self.rm_parameter_f()
                if isinstance(result, set):
                    new_link_is_set = False
                    for link in result:
                        if link not in listation and new_link_is_set == False:
                            self.new_link = link
                            new_link_is_set = True
                        else:
                            listation.append(link)
                else:
                    self.new_link = result
            if '..' in self.new_link:
                self.new_link = self.rm_dot_in_link()
            if self.new_link.startswith('.'):
                self.startsw_dot()
                self.dict_to_type()
            elif self.new_link.startswith('/'):
                self.startsw_slash()
                self.dict_to_type()
            elif self.new_link.startswith('http'):
                self.dict_to_type()
            else:
                self.starsw_other()
                self.dict_to_type()


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            if url[1] == 'js':
                js = JsHandler()
                if await js.request_handler(response):
                    js.find_sw_equal_links()
                    js.find_sw_colon_links()
                    js.find_sw_space_links()
                    js.find_sw_bracket_links()
                    js.js_iterator()
                    # pprint(js.links)
                    print('****outbound****')
                    pprint(js.outbound)
                    print('****inbound****')
                    pprint(js.inbound)

if __name__ == '__main__':
    asyncio.run(worker(start_link))