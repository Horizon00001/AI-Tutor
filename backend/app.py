from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import files, mineru, deepseek, ppt, questions, pipeline, tasks, download, health, auth, exams, collections

app = FastAPI(
    title="试卷讲解Demo API",
    description="FastAPI后端，提供试卷处理、PPT生成、相似题生成等功能",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router, prefix="/api/v1")
app.include_router(mineru.router, prefix="/api/v1")
app.include_router(deepseek.router, prefix="/api/v1")
app.include_router(ppt.router, prefix="/api/v1")
app.include_router(questions.router, prefix="/api/v1")
app.include_router(pipeline.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(download.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(exams.router, prefix="/api/v1")
app.include_router(collections.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "试卷讲解Demo API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
