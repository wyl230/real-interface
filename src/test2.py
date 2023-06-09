import asyncio

async def print_num():
    for i in range(1, 11):
        print(i)
        await asyncio.sleep(1)

async def print_hello():
    for i in range(1, 6):
        print("Hello")
        await asyncio.sleep(2)

loop = asyncio.get_event_loop()
tasks = [loop.create_task(print_num()), loop.create_task(print_hello())]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
