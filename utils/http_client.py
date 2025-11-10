"""comflow/utils/http_client.py - 异步 HTTP 客户端封装"""

import aiohttp
import asyncio
from typing import Any, Dict, Optional, Union
from ComfyUI_KuAi_Power.config import settings
from .async_runner import run_async

# 模块级复用的会话（连接池）
_session: Optional[aiohttp.ClientSession] = None

def _get_session(timeout: Optional[int] = None) -> aiohttp.ClientSession:
    """获取或创建全局复用的 ClientSession（带连接池与超时）。"""
    global _session
    to = aiohttp.ClientTimeout(total=timeout or settings.HTTP_TIMEOUT)
    if _session is None or _session.closed:
        # 使用默认连接器；如需更细的池控制可增加 limit/keepalive 等参数
        _session = aiohttp.ClientSession(timeout=to)
    else:
        # 更新会话超时（若调用时传入覆盖值）
        _session._default_timeout = to  # 使用内部属性以更新默认超时（aiohttp内部API，谨慎使用）
    return _session

async def fetch(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None,
    data: Optional[Union[bytes, str, Dict[str, Any]]] = None,
    timeout: Optional[int] = None,
) -> Union[Dict[str, Any], str]:
    """发送异步 HTTP 请求（连接池 + 重试），优先返回 JSON，失败时返回文本。
    - method: GET/POST/PUT/DELETE
    - headers: 可选请求头（可包含认证，如 Authorization）
    - json/data: 二者选其一，json 优先
    - timeout: 覆盖默认超时（秒）
    - 重试：基于 settings.HTTP_RETRY，遇到网络错误/超时进行重试
    """
    session = _get_session(timeout)
    attempts = max(0, int(getattr(settings, "HTTP_RETRY", 0))) + 1
    last_err: Optional[Exception] = None

    for i in range(attempts):
        try:
            async with session.request(method.upper(), url, headers=headers, json=json, data=data) as resp:
                text = await resp.text()
                try:
                    return await resp.json()
                except Exception:
                    return text
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            last_err = e
            # 简单退避：异步等待短暂时间（避免立即重试打爆服务）
            if i < attempts - 1:
                await asyncio.sleep(min(0.5 * (i + 1), 2.0))
        except Exception as e:
            # 其他异常不重试，直接抛出
            raise e

    # 所有重试失败，抛出最后一个错误
    raise last_err if last_err else RuntimeError("HTTP 请求失败且无详细错误")

def fetch_async_in_thread(*args, **kwargs):
    """在独立事件循环/线程中执行 fetch 并返回任务对象（开发占位）。"""
    coro = fetch(*args, **kwargs)
    return run_async(coro)