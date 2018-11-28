import aiohttp
import asyncio
import time
import re
import lxml
import os
import aiofiles
from lxml import html
from urllib.parse import unquote
import html2text
from pprint import pprint
from aiopg.sa import create_engine
from db import connection, domains_table, urls_table

from settings import auth_login, auth_password, ssl, start_url, domain

start_time = time.time()
auth = aiohttp.BasicAuth(login=auth_login, password=auth_password)
# todo create json recognizer

# async def worker(q):
#     async with aiohttp.ClientSession(auth=auth) as session:
#         while q.qsize() > 0:
#             url = await q.get()  # из очереди
#             if url[1] == 'shitty':
#                     bad_urls[url[0]] = 'shitty'
#             else:
#                 async with session.get(url[0]) as response:
#                     print(response.url, response.status)
#                     if url[1] == 'html':
#                         await html_handler(response)
#                     elif url[1] == 'img':
#                         await img_handler(response)
#                     elif url[1] == 'js':
#                         await js_handler(response)
#                     elif url[1] == 'css':
#                         await css_handler(response, q)
#                     elif url[1] == 'xml':
#                         await xml_handler(response)



parsed_urls = dict()
bad_urls = dict()
queue = set()
qu = asyncio.Queue()






async def main():
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get(start_url) as response:
            await html_handler(response)
            async with create_engine(**connection) as engine:
                async with engine.acquire() as conn:
                        await conn.execute(domains_table.insert().values({'process': True,
                                                                          'ssl': ssl,
                                                                          'domain': domain}))



    #
    # tasks = []
    # for _ in range(10):
    #     task = asyncio.Task(worker(qu))
    #     tasks.append(task)
    #
    # await asyncio.gather(*tasks)

if __name__ =='__main__':
    asyncio.run(main())
    print("--- %s seconds ---" % (time.time() - start_time))

