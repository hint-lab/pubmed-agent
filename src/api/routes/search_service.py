from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends,  HTTPException
from fastapi.responses import JSONResponse
from src.api.depends import get_pubmed_assistant
from src.api.models import MeshTerm, Article, SearchQuery
from src.agents.pubmed_assistant import PubMedAssistant

router = APIRouter()

# 定义API路由
@router.get("/{pmid}", response_model=Article)
async def get_article_by_pmid(
    pmid: str,
    agent: PubMedAssistant = Depends(get_pubmed_assistant)
)-> Article:
    """
    根据PMID检索文章信息
    """
    try:
        # 使用搜索代理检索文章
        result = await agent.get_article_details(pmid)
        if not result:
            raise HTTPException(status_code=404, detail="文章未找到")
            
        return _convert_to_article(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索文章时发生错误: {str(e)}")


@router.post("/batch", response_model=Dict[str, List[Article]])
async def get_articles_by_pmids(
    pmids: List[str],
    agent: PubMedAssistant = Depends(get_pubmed_assistant)
) -> Dict[str, List[Article]]:
    """
    批量并发检索多个PMID的文章信息
    """
    try:
        # 使用批量获取方法
        results = await agent.batch_get_details(pmids)
        articles = []
        for result in results:
            if isinstance(result, Exception) or not result:
                continue  # 已由基类处理异常
            articles.append(_convert_to_article(result))
            
        return {"articles": articles}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量检索文章时发生错误: {str(e)}")
 

@router.post("/", response_model=Dict[str, List[str]])
async def search_articles(
    search_params: SearchQuery,
    agent: PubMedAssistant = Depends(get_pubmed_assistant)
)-> Dict[str, List[str]]:
    """
    执行PubMed文献搜索
    """
    try:
        # 适配新的search_pubmed参数
        result = await agent.search_pubmed(
            query=search_params.query or "",
            topk=search_params.topk
        )
        return {"pmids": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索过程中发生错误: {str(e)}")

def _convert_to_article(result: Dict) -> Article:
    """统一转换结果到Article模型"""
    mesh_terms = {}
    for mesh_id, term in result.get('mesh_terms', {}).items():
        if isinstance(term, dict):  # 添加类型检查
            mesh_terms[mesh_id] = MeshTerm(
                descriptor_name=term.get('descriptor_name', ''),
                major_topic=term.get('major_topic', False),
                qualifier_name=term.get('qualifier_name'),
                qualifier_ui=term.get('qualifier_ui')
            )
    
    return Article(
        title=result.get('title', ''),
        first_author=result.get('first_author', ''),
        last_author=result.get('last_author', ''),
        authors=result.get('authors', []),
        abstract=result.get('abstract', ''),
        mesh_terms=mesh_terms,
        keywords=result.get('keywords', []),
        year=str(result.get('year', '')),  # 确保字符串类型
        journal=result.get('journal', ''),
        pmid=str(result.get('pmid', ''))
    )
