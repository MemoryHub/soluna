import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# 初始化FastAPI应用
app = FastAPI(title="Soluna Character API", version="1.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入并注册路由
from src.api.character.routes import router as character_router
from src.api.event.routes import router as event_router
from src.api.user.routes import router as user_router
from src.api.invited_code.routes import router as invite_code_router
from src.api.interaction.routes import router as interaction_router

app.include_router(character_router)
app.include_router(event_router)
app.include_router(user_router)
app.include_router(invite_code_router)
app.include_router(interaction_router)

# 根路由
@app.get("/")
async def root():
    return {"message": "Soluna Character API is running. Visit /docs for documentation."}

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)