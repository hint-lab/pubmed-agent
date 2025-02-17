from typing import Any, Dict, List
from metapub import PubMedFetcher
from src.tools.base import BaseTool
from src.logger import logger
from src.config import Config

class PubMedSearchTool(BaseTool):
    def __init__(self, name:str, config=None):
        """
        PubMed 搜索工具，继承自 BaseTool 类，用于执行 PubMed 搜索。
        :param config: 配置对象
        """
        super().__init__(name, config=config)
        self.fetch = PubMedFetcher()

    def execute(self, query: str, max_results: int = 100) -> list:
        """同步执行"""
        try:
            pmids = self.fetch.pmids_for_query(query, retmax=max_results)
            self.logger.info(f"同步找到 {len(pmids)} 篇文献")
            return pmids
        except Exception as e:
            self.logger.error(f"同步搜索失败: {str(e)}")
            raise

    async def async_execute(self, query: str, max_results: int = 100) -> list:
        """异步执行"""
        try:
            pmids = await self._execute_operation(
                self.fetch.pmids_for_query,
                query,
                retmax=max_results,
                error_prefix="PubMed搜索"
            )
            self.logger.info(f"异步找到 {len(pmids)} 篇文献")
            return pmids
        except Exception as e:
            self.logger.error(f"异步搜索失败: {str(e)}")
            raise

    async def execute_async(self, input_data: Dict[str, str]) -> Dict[str, Any]:
        """
        执行 PubMed 搜索，接受一个包含搜索参数的字典。
        :param input_data: 包含搜索参数（期刊、作者、年份、关键词等）和可选的 timeout 的字典
        :return: 搜索结果，字典形式
        """
        timeout = input_data.get('timeout')  # 可选参数
        max_retries = input_data.get('max_retries')  # 可选参数
        
        journal = input_data.get('journal')
        author = input_data.get('author')
        year = input_data.get('year')
        keyword = input_data.get('keyword')
        query = input_data.get('query')
        try:
            if query:
                self.logger.info(f"搜索查询字符串: {query}")
                result = await self._execute_operation(
                    self.fetch.pmids_for_query,
                    query,
                    timeout=timeout,
                    max_retries=max_retries,
                    error_prefix="PubMed搜索"
                )
                return result
            else:
                params = {}
                if journal:
                    params['journal'] = journal
                if author:
                    params['first author'] = author
                if year:
                    params['year'] = year
                if keyword:
                    params['keyword'] = keyword
                if params:
                    self.logger.info(f"搜索参数: {params}")
                    result = await self._execute_operation(
                        lambda: self.fetch.pmids_for_query(**params),
                        timeout=timeout,
                        max_retries=max_retries,
                        error_prefix="PubMed搜索"
                    )
                    return result
                return []

        except Exception as e:
            return {"error": f"搜索执行失败: {str(e)}"}
