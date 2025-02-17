from typing import Any, Dict
from metapub import PubMedFetcher
from src.tools.base import BaseTool
from src.logger import logger

class PubMedGetArticleTool(BaseTool):
    def __init__(self,name:str, config=None):
        """
        PubMed 文章获取工具，用于获取指定 PMID 的文章详细信息。
        :param config: 配置对象
        """
        super().__init__(name, config=config)
        self.fetch = PubMedFetcher()

    def execute(self, pmid: str) -> dict:
        """同步获取"""
        try:
            article = self.fetch.article_by_pmid(pmid)
            return self._format_article(article, pmid)
        except Exception as e:
            self.logger.error(f"同步获取失败 PMID {pmid}: {str(e)}")
            raise

    async def async_execute(self, pmid: str) -> dict:
        """异步获取"""
        try:
            article = await self._execute_operation(
                self.fetch.article_by_pmid,
                pmid,
                error_prefix="获取文章"
            )
            return self._format_article(article, pmid)
        except Exception as e:
            self.logger.error(f"异步获取失败 PMID {pmid}: {str(e)}")
            raise

    def _format_article(self, article, pmid):
        """统一格式化文章信息"""
        return {
            'pmid': pmid,
            'title': article.title,
            'abstract': article.abstract,
            'authors': article.authors,
            'journal': article.journal,
            'year': article.year
        }
