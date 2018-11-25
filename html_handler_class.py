import aiohttp
import asyncio
import re
from pprint import pprint
from urllib.parse import unquote
from css_handler_class import CssHandler
from js_handler import JsHandler
from lxml import html as lhtml
import html

start_link = ['http://megamillions.com.ua/', 'html']


class HtmlHandler(CssHandler, JsHandler):
    def html_find_a_links(self):
        try:
            a_links = lhtml.fromstring(self.response_text)
            a_links = a_links.xpath('//a/@href')
            [self.links.add(link) for link in a_links]
        except Exception as e:
            print('find_a_links', type(e))

    def html_find_lookalike_links(self):
        match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def html_find_srcset(self):
        match = re.findall(r'srcset=[\'\"]?((http|/)[^\'\">]+)', self.response_text)
        for m in match:
            for item in m:
                if self.url.host in item:
                    if ','in item:
                        item = item.split(',')
                        for img_url in item:
                            self.links.add(img_url.strip().split(' ')[0])
                    # may cause errors
                    else:
                        self.links.add(item.strip().split(' ')[0])
                        print('find_srcset_else_item', item)

    def html_iterator(self):
        listation = list(self.links)
        for self.link in listation:
            self.new_link = html.unescape(unquote(self.link))
            if self.new_link.startswith('\\\\'):
                self.rm_backslash()
            if self.new_link.startswith('//'):
                self.startsw_double_slash()
            if '#' in self.new_link:
                self.rm_hash()
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

        # self.inbound = check_type(self.inbound)


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            if url[1] == 'html':
                html_instance = HtmlHandler()
                if await html_instance.request_handler(response):
                    html_instance.html_find_a_links()
                    html_instance.html_find_lookalike_links()
                    html_instance.html_find_srcset()
                    html_instance.html_iterator()
                    print('html_inbound', len(html_instance.inbound))
                    print('html_outbound', len(html_instance.outbound))
                    # css parser
                    html_instance.css_find_links()
                    html_instance.css_iterator()
                    print('css_inbound', len(html_instance.inbound))
                    print('css_outbound', len(html_instance.outbound))
                    # js parser
                    html_instance.js_find_sw_bracket_links()
                    html_instance.js_find_sw_colon_links()
                    html_instance.js_find_sw_equal_links()
                    html_instance.js_find_sw_space_links()
                    html_instance.js_iterator()
                    print('js_inbound', len(html_instance.inbound))
                    print('js_outbound', len(html_instance.outbound))
                    # pprint(html.links)
                    print('****outbound****')
                    pprint(html_instance.outbound)
                    print('****inbound****')
                    pprint(html_instance.inbound)




asyncio.run(worker(start_link))