import aiohttp
import asyncio
import re
from pprint import pprint
from base_handler_class import BaseHandler


start_link = ['http://megamillions.com.ua/xmlrpc.php?rsd', 'xml']


class XmlHandler(BaseHandler):
    def xml_find_sw_equal_links(self):
        match = re.findall(r'=[\'\"]?((http|//)[^\'\" >]+)', self.response_text)
        [self.links.add(x[0]) for x in match]

    def xml_find_angual_links(self):
        match = re.findall(r'>((http)[^ <]+)', self.response_text)
        [self.links.add(x[0]) for x in match]



async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            if url[1] == 'xml':
                xml_instance = XmlHandler()
                if await xml_instance.request_handler(response):
                    xml_instance.xml_find_sw_equal_links()
                    xml_instance.xml_find_angual_links()
                    xml_instance.base_iterator()

                    # pprint(xml_instance.links)
                    print('****outbound****')
                    pprint(xml_instance.outbound)
                    print('****inbound****')
                    pprint(xml_instance.check_type(xml_instance.inbound))

if __name__ == '__main__':
    asyncio.run(worker(start_link))