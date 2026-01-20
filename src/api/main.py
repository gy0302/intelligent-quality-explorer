import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config.settings import settings

# 导入所有路由器
from src.api.ai_review import router as ai_review_router
from src.api.api_management import router as api_management_router
from src.api.config import router as config_router
from src.api.project_management import router as project_management_router
from src.api.test_case import router as test_case_router
from src.api.test_execution import router as test_execution_router
from src.api.test_point import router as test_point_router
from src.api.test_script import router as test_script_router
from src.api.workflow import router as workflow_router

app = FastAPI(
    title="AQES-Test",
    description="AQES-Test Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册项目管理路由器
app.include_router(project_management_router,prefix="")
# 注册API管理路由器
app.include_router(api_management_router,prefix="")
# 注册AI评审路由器
app.include_router(ai_review_router,prefix="")
# 注册测试点路由器
app.include_router(test_point_router,prefix="")
# 注册测试用例路由器
app.include_router(test_case_router,prefix="")
# 注册测试脚本路由器
app.include_router(test_script_router,prefix="")
# 注册测试执行路由器
app.include_router(test_execution_router,prefix="")
# 注册工作流路由器
app.include_router(workflow_router,prefix="")
# 注册配置中心路由器
app.include_router(config_router,prefix="")

@app.get("/", summary="健康检查", tags=["系统"])
async def health_check():
    return {"status": "ok", "message": "AQE-Test API服务正常运行"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局统一异常处理器"""
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"服务器内部错误: {str(exc)}"}
    )



if __name__ == "__main__":
    print(f"✅ AQES-Test 服务启动成功，版本：1.0.0")
    print(f"📚 接口文档地址：http://localhost:8000/docs")
    print(f"🔍 健康检查地址：http://localhost:8000/")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)