import os
import re
import aiofiles
from db import connection, urls_table
from aiopg.sa import create_engine
from urllib.parse import urljoin, unquote
import html


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
        print(self.url.path)
        print(self.url.query_string)
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
        return path + '' .join(filename)

    def rm_n_in_link(self):
        return self.new_link.replace('\n', '')

    def rm_wierd_stuff_in_link(self):
        if '\'' in self.new_link:
            new_link = self.new_link.split('\'')[0]
        elif '\"' in self.new_link:
            new_link = self.new_link.split('\"')[0]
        elif '*' in self.new_link:
            new_link = self.new_link.split('*')[0]
        else:
            new_link = self.new_link.split(')')[0]
        return new_link

    def rm_unescaped_in_link(self):
        return self.new_link.replace('\/', '/')

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
        if os.linesep in self.link:
            self.link = self.link.split(os.linesep)[0]
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

    def check_type(self, links_dict):
        list_urls = dict()
        for link, source in links_dict.items():
            link = unquote(link)
            if link.endswith(('.jpg', '.png', '.jpeg', '.exif', '.tiff', '.gif', '.bmp', '.ico')):
                list_urls[link] = ['img', source]
            elif '.js' in link:
                list_urls[link] = ['js', source]
            elif '.css' in link:
                list_urls[link] = ['css', source]
            elif '.xml' in link:
                list_urls[link] = ['xml', source]
            elif link.endswith(('.ttf', '.woff', '.woff2', '.svg', '.eot')):
                list_urls[link] = ['font', source]
            elif '?' in link:
                list_urls[link] = ['parametrized', source]
            else:
                list_urls[link] = ['html', source]
        return list_urls

    def base_iterator(self):
        listation = list(self.links)
        for self.link in listation:
            self.new_link = html.unescape(unquote(self.link))
            if self.new_link.startswith('\\\\'):
                self.rm_backslash()
            if self.new_link.startswith('//'):
                self.startsw_double_slash()
            if '\/' in self.new_link:
                self.new_link = self.rm_unescaped_in_link()
            if '\n' in self.new_link:
                self.new_link = self.rm_n_in_link()
            if any(x in self.new_link for x in ['\'', '\"', '*', ')']):
                self.new_link = self.rm_wierd_stuff_in_link()
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


    async def write_db(self, values):
        async with create_engine(**connection) as engine:
            async with engine.acquire() as conn:
                await conn.execute(urls_table.insert().values(**values))