import aiohttp
import asyncio
import re
from pprint import pprint
from css_handler_class import CssHandler
from js_handler import JsHandler
from lxml import html as lhtml
import html
import html2text

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

    def get_meta(self):
        plain_html = self.response_text
        h = html2text.HTML2Text()
        h.ignore_links = True
        plain_text = h.handle(plain_html)
        text_obj = html.fromstring(plain_html.lower())
        try:
            title = text_obj.xpath('//title/text()')[0].strip()
        except Exception:
            title = 'None'
        try:
            description = text_obj.xpath('//meta[@name="description"]/@content')[0].strip()
        except Exception:
            description = 'None'
        return [title, description, plain_text, plain_html]


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            if url[1] == 'html':
                html_instance = HtmlHandler()
                if await html_instance.request_handler(response):
                    await html_instance.write_binary('index.html')
                    html_instance.html_find_a_links()
                    html_instance.html_find_lookalike_links()
                    html_instance.html_find_srcset()
                    # css parser
                    html_instance.css_find_links()
                    # js parser
                    html_instance.js_find_sw_bracket_links()
                    html_instance.js_find_sw_colon_links()
                    html_instance.js_find_sw_equal_links()
                    html_instance.js_find_sw_space_links()

                    html_instance.base_iterator()
                    html_instance.inbound = html_instance.check_type(html_instance.inbound)
                    # pprint(html.links)
                    print('****outbound****')
                    pprint(html_instance.outbound)
                    print('****inbound****')
                    pprint(html_instance.inbound)




asyncio.run(worker(start_link))