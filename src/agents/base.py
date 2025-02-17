from typing import Dict, List, Any
from src.tools.base import BaseTool
from src.config import Config
from src.logger import logger
import asyncio

class EasyAgent:
    def __init__(self, name: str, config: Config = None):
        self.name = name
        self.config = config
        self.tools: Dict[str, BaseTool] = {}
        self.logger = logger
        self.cached_results = {}  # 添加通用缓存

    def register_tool(self, tool: BaseTool):
        """注册工具"""
        self.tools[tool.name] = tool
        self.logger.info(f"Tool '{tool.name}' registered to agent '{self.name}'.")

    async def execute_tool_async(self, tool_name: str, *args, **kwargs) -> Any:
        """异步执行工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 {tool_name} 未找到")
        tool = self.tools[tool_name]
        self.logger.info(f"异步执行工具: {tool.name}")
        return await tool.async_execute(*args, **kwargs)

    def execute_tool_sync(self, tool_name: str, *args, **kwargs) -> Any:
        """同步执行工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 {tool_name} 未找到")
        tool = self.tools[tool_name]
        self.logger.info(f"同步执行工具: {tool.name}")
        return tool.execute(*args, **kwargs)

    # 保持原有异步方法兼容
    async def execute_tool(self, *args, **kwargs):
        """兼容旧代码的异步执行"""
        return await self.execute_tool_async(*args, **kwargs)

    async def async_execute_tools(self, tool_name: str, params_list: List[Dict]) -> List[Any]:
        """并发执行多个工具任务"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 {tool_name} 未找到")
            
        tool = self.tools[tool_name]
        tasks = []
        for params in params_list:
            tasks.append(tool.async_execute(**params))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._process_async_results(results)

    def _process_async_results(self, results: List[Any]) -> List[Any]:
        """统一处理异步结果"""
        success = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"异步操作失败: {str(result)}")
            else:
                success.append(result)
        return success

    def __str__(self):
        return f"Agent(name={self.name}, tools={list(self.tools.keys())})"