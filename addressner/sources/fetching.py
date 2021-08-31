import asyncio
from aiohttp import ClientSession, TCPConnector
from ssl import SSLContext
from nest_asyncio import apply
apply()


async def fetch(url: str,
                session: ClientSession) -> dict:
    """
    Function that makes a URL query in an asynchronous way with a given session.

    :param url: URL to query
    :param session: session
    :return: the result of the query in .json (dict) format
    """
    async with session.get(url, ssl=SSLContext()) as response:
        return await response.json()


async def fetch_sem(semaphore: asyncio.locks.Semaphore,
                    attempts: int,
                    url: str,
                    session: ClientSession):
    """
    Function that runs "fetch" function with an asyncio Semaphore and checks if the result of the query is a dict

    :param semaphore: asyncio semaphore with the limitation of simultaneous queries
    :param attempts: attempts per query if the result is not dict type
    :param url: URL to query
    :param session: session
    :return: the result of the query in a dict
    """
    async with semaphore:
        for _ in range(attempts):
            result = await fetch(url, session)
            if isinstance(result, dict):
                break
        return result


# Function to search for all queries
async def fetch_all(limit: int,
                    attempts: int,
                    urls: list,
                    loop: asyncio.windows_events._WindowsSelectorEventLoop) -> list:
    """
    Function that makes a set of URLs queries in an asynchronous way.

    :param limit: limitation of simultaneous queries
    :param attempts: attempts per query if the result is not dict type
    :param urls: list of URLs to query
    :param loop: loop of asyncio routine
    :return: the results of the queries in a list of dicts
    """

    sem = asyncio.Semaphore(value=limit, loop=loop)
    connector = TCPConnector(limit=60)
    async with ClientSession(loop=loop, connector=connector) as session:
        return await asyncio.gather(*[fetch_sem(sem, attempts, url, session) for url in urls], return_exceptions=True)
