import os
import re
import aiofiles
import json
from db import connection, urls_table
from aiopg.sa import create_engine
from urllib.parse import unquote

class BaseHandler:
    def __init__(self):
        self.inbound = dict()
        self.outbound = dict()
        self.response_text = object()
        self.response_object = object()
        self.links = list()
        self.url = object()
        self.link = str()
        self.new_link = str()

    async def request_handler(self, response):
        if response.status == 200:
            self.url = response.url
            self.response_object = response
            self.response_text = await response.text()
            return True
        elif response.status == 404:
            print('bad_url')
            return False

    async def write_binary(self, ext=''):
        # creating path from host and path
        path = self.url.host + self.url.path
        # removing filename
        directory = path.split('/')[:-1]
        directory = '/'.join(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            async with aiofiles.open(path + ext, mode='wb') as f:
                await f.write(await self.response_object.read())
                await f.close()
        except OSError:
            print('OSError')

    def prepare_n_rm(self):
        self.new_link = unquote(self.link)
        self.new_link = self.new_link.replace('\\', '')
        if '&' in self.new_link or '#' in self.new_link:
            for entity in ['&', '#']:
                if entity in self.new_link:
                    self.new_link = self.new_link.split(entity)[0]

    def link_parameter_f(self):
        self.new_link = self.new_link.split('?f=')[1:]
        return self.url.with_path(self.new_link)

    def link_dot(self):
        # count steps back in response url to find absolute path for url by counting dots in url
        steps_back = self.new_link.split('/')[0].count('.')
        # making steps back from current path
        path = self.url.parts[:-steps_back]
        # joining url back without first slash
        path = '/'.join(path[1:])
        # getting absolute url together
        self.inbound[(str(self.url.with_path(path + self.new_link[steps_back:])))] = self.link

    def link_slash(self):
        # if link is relative and in the same folder that url is, make that link absolute
        self.inbound[self.url.with_path(self.new_link[1:])] = self.link

    def link_http(self):
        if self.url.host in self.new_link:
            self.inbound[self.new_link] = self.link
        else:
            self.outbound.add(self.link)

    def link_other(self):
            # find links in all wierd occurencies
            match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', self.new_link)
            # great possibility of error generation
            if not match:
                if '?' in self.new_link:
                    self.new_link = self.new_link.split('?')[:-1][0]
                self.inbound[str(self.url.parent) + '/' + self.new_link] = self.link
            if match:
                for item in match[0]:
                    if not item.startswith(str(self.url.parent)):
                        if '/' in item:
                            self.outbound[item] = self.link

    async def write_db(self, values):
        async with create_engine(**connection) as engine:
            async with engine.acquire() as conn:
                await conn.execute(urls_table.insert().values(**values))