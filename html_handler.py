import json, aiohttp, asyncio, re
from lxml import html
from main import get_meta, start_url, check_type, create_engine, connection,\
    urls_table, write_binary, bad_urls, pprint, qu


link = ['http://megamillions.com.ua/', 'css']


async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url[0]) as response:
            # print(response.url, response.status)
            if url[1] == 'css':
                await html_handler(response)


def get_a_links(response, start_url):
    try:
        links = html.fromstring(response)
        a_links = set(links.xpath('//a/@href'))
        a_links = [x for x in a_links if x.startswith('/') or x.startswith(start_url)]
        # find all links that started with ='|"http|/
        match = re.findall(r'=[\'\"]?((http|/)[^\'\" >]+)', response)
        # get just first group in occurrence
        match = [x[0] for x in match]
        # remove urls with //
        match = [x for x in match if not x.startswith('//')]
        # replace relative url with absolute
        match = [x if not x.startswith('/') else start_url+x for x in match]
        # get outbound links
        outbound_links = [x for x in match if not x.startswith(start_url)]
        # remove outbound links
        match = [x for x in match if x.startswith(start_url)]
        # remove duplicates
        all_links = set()
        # split concatenated urls
        for x in match:
            if ',' in x:
                splitted_urls = x.split(',')
                for item in splitted_urls:
                    if not item.startswith(start_url):
                        item = start_url+item
                        all_links.add(item)
                    all_links.add(item)
            else:
                all_links.add(x)
        return [a_links, all_links, outbound_links]

    except lxml.etree.ParserError:
        return False

# todo remove html enteties from url, convert result to dictionary,
async def html_handler(response):
    try:
        if response.status == 200:
            url = str(response.url)
            response_text = await response.text()
            meta = get_meta(response_text)
            links = get_a_links(response_text, start_url)
            pprint(links)
            # typized_all_links = check_type(links[1])
            # print(typized_all_links)
    #         async with create_engine(**connection) as engine:
    #             async with engine.acquire() as conn:
    #                     await conn.execute(urls_table.insert().values({'url': url,
    #                                                                    'type': 'html',
    #                                                                    'title': meta[0],
    #                                                                    'description': meta[1],
    #                                                                    'text': json.dumps(meta[2]),
    #                                                                    'text_len': len(meta[2]),
    #                                                                    'html': json.dumps(meta[3]),
    #                                                                    'html_len': len(meta[3]),
    #                                                                    'a_links_len': len(links[0]),
    #                                                                    'links_inbound': list(links[0]),
    #                                                                    'links_inbound_len': len(links[0]),
    #                                                                    'links_outbound': list(links[2]),
    #                                                                    'links_outbound_len': len(links[2]),
    #                                                                    'all_links': list(links[1]),
    #                                                                    'all_links_len': len(links[1])}))
    #         await write_binary(response, url, 'index.html')
    #         pprint(typized_all_links)
    #     elif response.status in [500, 502]:
    #         await qu.put([str(response.url), 'html'])
    #     else:
    #         bad_urls[str(response.url)] = response.status
    # except ValueError:
    #     bad_urls[str(response.url)] = 'ValueError'
    # except TypeError:
    #     bad_urls[str(response.url)] = 'TypeError'
    # except AttributeError:
    #     print('ValueError', response.url)
    #     print(response)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    asyncio.run(worker(link))
