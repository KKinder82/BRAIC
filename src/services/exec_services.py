import asyncio
from concurrent.futures import ThreadPoolExecutor

executer = ThreadPoolExecutor(max_workers=10)

def run_async(func, *args):
    try:
        loop = asyncio.get_event_loop()
        loop.run_in_executor(executer, func, *args)
    except Exception as e:
        print(e)

def run_async2(func, *args):
    try:
        executer.submit(func, *args)
    except Exception as e:
        print(e)

