import asyncio
import aiohttp
async def worker(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(response.url.query_string)

asyncio.run(worker('http://megamillions.com.ua/wp-json/oembed/1.0/embed?url=http://megamillions.com.ua/'))