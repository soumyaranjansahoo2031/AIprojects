from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.projects import router as projects_router
from app.db.database import Base, engine
from app.models.project import Project


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OpenSlate Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "openslate-backend",
    }


app.include_router(projects_router, prefix="/api")