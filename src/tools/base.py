from typing import Any, Dict, Callable, TypeVar, Optional
from src.config import Config
from src.logger import logger
from time import sleep
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Coroutine
T = TypeVar('T')
 
class BaseTool:
    def __init__(self, name:str, config=None):
        self.name = name
        self.config = config
        self.logger = logger
        self._semaphore = None
        self.max_concurrent_tasks = getattr(config, 'max_concurrent_tasks', 10) if config else 10

    def execute(self, *args, **kwargs):
        """同步执行入口"""
        raise NotImplementedError("同步执行方法未实现")

    async def async_execute(self, *args, **kwargs):
        """异步执行入口"""
        try:
            # 默认将同步方法转为异步
            return await asyncio.to_thread(self.execute, *args, **kwargs)
        except NotImplementedError:
            # 如果子类实现了异步方法则直接调用
            return await self._async_execute_impl(*args, **kwargs)
            
    async def _async_execute_impl(self, *args, **kwargs):
        """实际的异步实现"""
        raise NotImplementedError("异步执行方法未实现")

    async def _execute_operation(self, operation, *args, timeout=None, max_retries=None, error_prefix="操作", **kwargs):
        """
        执行操作的通用方法，支持超时和重试
        :param operation: 要执行的操作（函数）
        :param args: 传递给操作的位置参数
        :param timeout: 超时时间（秒）
        :param max_retries: 最大重试次数
        :param error_prefix: 错误消息前缀
        :param kwargs: 传递给操作的关键字参数
        :return: 操作结果
        """
        retries = 0
        max_retries = max_retries or 3
        timeout = timeout or 30

        while retries < max_retries:
            try:
                # 使用 asyncio.wait_for 来处理超时
                if args:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(operation, *args),
                        timeout=timeout
                    )
                else:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(operation, **kwargs),
                        timeout=timeout
                    )
                return result

            except asyncio.TimeoutError:
                retries += 1
                if retries < max_retries:
                    self.logger.warning(f"{error_prefix}超时，正在重试 ({retries}/{max_retries})...")
                else:
                    raise TimeoutError(f"{error_prefix}在 {timeout} 秒内未完成，已重试 {max_retries} 次")

            except Exception as e:
                retries += 1
                if retries < max_retries:
                    self.logger.warning(f"{error_prefix}失败: {str(e)}，正在重试 ({retries}/{max_retries})...")
                else:
                    raise Exception(f"{error_prefix}失败: {str(e)}，已重试 {max_retries} 次")

    async def _async_operation(self, operation: Callable, *args, **kwargs):
        """
        在线程池中执行同步操作
        """
        with ThreadPoolExecutor() as pool:
            return await self.loop.run_in_executor(
                pool, partial(operation, *args, **kwargs)
            )

    def __del__(self):
        """
        清理事件循环 - 移除自动关闭逻辑
        """
        pass  # 不再自动关闭事件循环，避免影响其他任务

    def __str__(self):
        return f"Tool(name={self.name})"