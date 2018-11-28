import aiohttp
import asyncio
import re
from pprint import pprint
import json
from base_handler_class import BaseHandler

# start_link = ['http://megamillions.com.ua/', 'css']
start_link = ['http://megamillions.com.ua/wp-content/plugins/waiting/css/style.css', 'css']


class CssHandler(BaseHandler):
    def css_find_links(self):
        # lets find all urls in url tags
        css_links = re.findall(r"url\((.*?)\)", self.response_text)
        [self.links.add(x) for x in css_links]

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


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            if url[1] == 'css':
                css_instance = CssHandler()
                if await css_instance.request_handler(response):
                    await css_instance.write_binary()
                    css_instance.css_find_links()
                    css_instance.base_iterator()
                    css_instance.inbound = css_instance.check_type(css_instance.inbound)
                    # await css_instance.write_db(css_instance.data_to_db())
                    pprint(css_instance.inbound)
                    pprint(css_instance.outbound)


if __name__ == '__main__':
    asyncio.run(worker(start_link))