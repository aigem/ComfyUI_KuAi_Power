"""comflow/utils/async_runner.py - 异步任务运行器"""

import threading
import asyncio
from typing import Any, Coroutine

def _runner(loop: asyncio.AbstractEventLoop, coro: Coroutine[Any, Any, Any]):
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro)
    finally:
        loop.stop()
        loop.close()

def run_async(coro) -> threading.Thread:
    """在后台线程运行协程，避免阻塞主进程。
    返回 Thread，以便调用方管理生命周期（开发占位）。
    """
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=_runner, args=(loop, coro), daemon=True)
    t.start()
    return t