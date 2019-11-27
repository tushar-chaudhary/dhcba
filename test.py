import lxml.html
from ftfy import fix_text
# import requests
import asyncio
import aiohttp
# import gevent.monkey

# gevent.monkey.patch_select(aggressive=True)
# from multiprocessing.dummy import Pool as ThreadPool

# def getDOM(url):
#     return requests.get(url).text

urls = [
    "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=1",
    "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=2",
    "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=3",
    "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=4",
    "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=5"
]

async def fetch(url, session):
    # The async task

    async with session.get(url) as response:

        html = await response.read()
        return html

session = aiohttp.ClientSession()

tasks = [asyncio.ensure_future(fetch(url, session)) for url in urls]

# Create a loop to run all the tasks in.
loop = asyncio.get_event_loop()

# Gather is like Promise.all
responses = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
print(responses)
loop.close()