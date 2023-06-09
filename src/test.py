import asyncio

async def hello_world():
    print("Hello")
    await asyncio.sleep(1)
    print("World")


async def f():
    while True:
        print("f")
        await asyncio.sleep(1)


async def g():
    while True:
        print("g")
        await asyncio.sleep(2)

loop = asyncio.get_event_loop()
loop.run_until_complete(g())
loop.close()
