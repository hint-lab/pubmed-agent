from src.config import Config
from src.tools.pubmed_search import PubMedSearchTool
from src.tools.pubmed_get_article import PubMedGetArticleTool
from src.tools.translate import TranslateTool
from src.agents import EasyAgent
from typing import Any, List, Dict
 

class PubMedAssistant(EasyAgent):
    def __init__(self, name: str, config: Config = None):
        """
        PubMedAssistant 类，继承自 EasyAgent，专注于 PubMed 搜索任务。
        :param name: 智能体名称
        :param config: 配置对象
        """
        super().__init__(name, config)
        self._register_pubmed_tools()
        self.cached_search_results= {}

    def _register_pubmed_tools(self):
        """统一注册工具"""
        tools = [
            PubMedSearchTool(name="PubMedSearchTool", config=self.config),
            PubMedGetArticleTool(name="PubMedGetArticleTool", config=self.config),
            TranslateTool(name="TranslateTool", config=self.config)
        ]
        for tool in tools:
            self.register_tool(tool)

    async def search_pubmed(self, **params) -> List[str]:
        """搜索入口"""
        try:
            results = await self.execute_tool_async(
                "PubMedSearchTool",
                query=params.get('query'),
                max_results=self.config.get("max_search_results")
            )
            self.cached_search_results = results
            self.logger.info(f"找到 {len(results)} 篇文献 (模式: {'异步'})")
            return results[:params.get('topk', 10)]
        except Exception as e:
            self.logger.error(f"文献搜索失败: {str(e)}")
            raise

    async def batch_get_details(self, pmids: List[str]) -> List[Dict]:
        """批量获取详情"""
        params_list = [{"pmid": pmid} for pmid in pmids]
        return await self.async_execute_tools("PubMedGetArticleTool", params_list)

    async def get_article_details(self, pmid: int) -> Dict[Any, Any]:
        """统一使用异步调用"""
        return await self.execute_tool_async("PubMedGetArticleTool", pmid=pmid)
        
  