import os
import sys
# 获取当前文件的父目录的父目录（即项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到系统路径
sys.path.append(project_root)
from fastapi import FastAPI 
from fastapi.responses import JSONResponse 
from src.config import Config
from src.api import api_routers
from fastapi.middleware.cors import CORSMiddleware

# 创建FastAPI应用
app = FastAPI(
    title="PubMed文献搜索服务", 
    description="基于多智能体的用于检索和返回PubMed文献信息的API服务",
    docs_url="/docs",
    redoc_url="/redoc",
    version="1.0.0",
    )

# 修改路由注册方式
app.include_router(api_routers, prefix="/api")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": f"发生未知错误: {str(exc)}"}
    )

# 创建搜索代理实例
config = Config(config_file="./config.yaml")
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api_server:app",  # 使用模块路径引用
        host="0.0.0.0", 
        port=8000,
        workers=6,  # 设置工作进程数
        reload=True  # 开发环境下启用热重载
    ) 