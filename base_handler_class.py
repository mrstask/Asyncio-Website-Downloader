import os
import re
import aiofiles
import json
from db import connection, urls_table
from aiopg.sa import create_engine
from urllib.parse import unquote, urljoin


class BaseHandler:
    def __init__(self):
        self.inbound = dict()
        self.outbound = dict()
        self.response_text = object()
        self.response_object = object()
        self.links = set()
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
# removing stuff

    def rm_backslash(self):
        self.new_link = self.new_link.replace('\\', '')

    def rm_hash(self):
        if '?#' in self.new_link:
            self.new_link = self.new_link.split('?#')[0]
        else:
            self.new_link = self.new_link.split('#')[0]

    def rm_parameter_f(self):
        # print('rm_parameter_f', self.new_link)
        occurancies = self.new_link.split('?f=')
        if ',' in occurancies[1]:
            occurances = set(occurancies[1].split(','))
            new_occurances = set()
            for item in occurances:
                new_occurances.add(str(self.url.with_path(item)))
            return new_occurances
        else:
             return self.new_link[1]

    def rm_dot_in_link(self):
        path = urljoin(self.new_link, '.')
        filename = self.new_link.split('/')[-1]
        return path +''.join(filename)

        # startswith stuff

    def startsw_dot(self):
        # count steps back in response url to find absolute path for url by counting dots in url
        steps_back = self.new_link.split('/')[0].count('.')
        # making steps back from current path
        path = self.url.parts[:-steps_back]
        # joining url back without first slash
        path = '/'.join(path[1:])
        # getting absolute url together
        self.new_link = str(self.url.with_path(path + self.new_link[steps_back:]))

    def startsw_slash(self):
        # if link is relative and in the same folder that url is, make that link absolute
        self.new_link = str(self.url.with_path(self.new_link[1:]))

    def startsw_double_slash(self):
        self.new_link = 'http:' + self.new_link

    def dict_to_type(self):
        if self.url.host in self.new_link:
            self.inbound[self.new_link] = self.link
        else:
            self.outbound[self.new_link] = self.link

    def starsw_other(self):
            # find links in all wierd occurencies
            match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', self.new_link)
            # great possibility of error generation
            if not match:
                if '?' in self.new_link:
                    self.new_link = self.new_link.split('?')[:-1][0]
                self.new_link = str(self.url.parent) + '/' + self.new_link
            if match:
                for item in match[0]:
                    if not item.startswith(str(self.url.parent)):
                        if '/' in item:
                            self.new_link = item

    async def write_db(self, values):
        async with create_engine(**connection) as engine:
            async with engine.acquire() as conn:
                await conn.execute(urls_table.insert().values(**values))