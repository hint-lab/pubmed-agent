from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends,  HTTPException
from fastapi.responses import JSONResponse
from src.api.models import Article

router = APIRouter()
 
@router.post("/")
async def translate_article(article: Article):
    """
    翻译文章内容
    """
    try:
        # 准备要翻译的文章数据
        article_dict = article.dict()
        # 调用翻译工具
        translated = agent.translate_article(article_dict)
        return translated
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译过程中发生错误: {str(e)}")

