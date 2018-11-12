import aiohttp
import asyncio
import re
from main import check_type, start_url, connection, create_engine, urls_table
from pprint import pprint
import json
from base_handler_class import BaseHandler

start_link = ['http://megamillions.com.ua/wp-content/themes/maskitto-light/css/style.css', 'css']


class CssHandler(BaseHandler):
    def find_css_links(self):
        # lets find all urls in url tags
        self.links = re.findall(r"url\((.*?)\)", self.response_text)

    def data_to_db(self):
        return {'url': str(self.url),
                'type': 'css',
                'title': 'None',
                'description': 'None',
                'text': 'None',
                'text_len': 0,
                'html': json.dumps(self.response_text),
                'html_len': len(self.response_text),
                'a_links_len': 0,
                'links_inbound': json.dumps(self.inbound),
                'links_inbound_len': len(self.inbound.keys()),
                'links_outbound': json.dumps(self.outbound),
                'links_outbound_len': len(self.outbound.keys())}

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
            if url[1] == 'css':
                css = CssHandler()
                if await css.request_handler(response):
                    await css.write_binary()
                    css.find_css_links()
                    css.iterator()
                    await css.write_db(css.data_to_db())
                    pprint(css.inbound)
                    pprint(css.outbound)


if __name__ == '__main__':
    asyncio.run(worker(start_link))