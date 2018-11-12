import aiohttp
import asyncio
import re
from main import write_binary, check_type, start_url, connection, create_engine, urls_table
from urllib.parse import unquote
from pprint import pprint
from css_handler_class import CssHandler
import json
from lxml import html

start_link = ['http://megamillions.com.ua/', 'html']


class HtmlHandler(CssHandler):
    def find_a_links(self):
        try:
            links = html.fromstring(self.response_text)
            a_links = links.xpath('//a/@href')
            for link in a_links:
                if link.startswith('/'):
                    print(self.url.parent + link)
                elif link.startswith(str(self.url.parent)):
                    self.inbound[link] = link
                else:
                    self.outbound[link] = link
        except Exception as e:
            print(type(e))

    def find_lookalike_links(self):
        match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', self.response_text)
        match = [x[0] for x in match]
        # pprint(match)

    def find_srcset(self):
        match = re.findall(r'srcset=[\'\"]?((http|/)[^\'\">]+)', self.response_text)
        for m in match:
            for item in m:
                if self.url.host in item:
                    print(item)

    def iterator(self):
        for self.link in self.links:
            self.prepare_n_rm()
            if '?f=' in self.new_link:
                self.new_link = self.link_parameter_f()
            if self.new_link.startswith('.'):
                self.link_dot()
            elif self.new_link.startswith('/'):
                self.link_slash()
            elif self.new_link.startswith('http'):
                self.link_http()
            else:
                self.link_other()
        self.inbound = check_type(self.inbound)


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            print(url[0])
            if url[1] == 'html':
                html = HtmlHandler()
                if await html.request_handler(response):
                    html.find_a_links()
                    html.find_css_links()
                    html.find_lookalike_links()
                    html.find_srcset()

                    # print(html.links)
                # html.iterator()
                # css.link_outbound_rm()
                # await css.write_db()



asyncio.run(worker(start_link))