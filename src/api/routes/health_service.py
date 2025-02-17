from fastapi import APIRouter

router = APIRouter()
# 添加健康检查端点
@router.get("/")
async def health_check():
    """
    服务健康检查接口
    """
    return {"status": "healthy"}

