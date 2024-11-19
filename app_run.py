import os
import asyncio
import uvicorn

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse

from server.models import Base
from server.routers.database import engine, get_db
from server.routers.download import router as download_router
from server.routers.features import router as features_router
from server.routers.frequencies import router as frequencies_router
from server.routers.lengths import router as lengths_router
from server.routers.states import router as states_router
from server.routers.task import router as task_router
from server.routers.taskgroup import router as taskgroup_router
from server.routers.tasks import router as tasks_router
from server.routers.text import router as text_router
from server.routers.texts import router as texts_router
from server.routers.texts import remove_texts


# Add Background scheduler to automatically remove expired texts in the database
scheduler = BackgroundScheduler()
scheduler.add_job(remove_texts, CronTrigger(hour=0, minute=0))
scheduler.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
PROD_PREFIX = "/api" if os.environ.get("PRODUCTION") else ""


# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with the actual allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/healthcheck")
async def healthcheck():
    return HTMLResponse(content="Application health check runs successfully", status_code=200)


@app.get("/")
async def index() -> RedirectResponse:
    return RedirectResponse(url="/docs")


app.include_router(download_router, prefix=f"{PROD_PREFIX}/download", tags=["download"], dependencies=[Depends(get_db)])
app.include_router(features_router, prefix=f"{PROD_PREFIX}/features", tags=["features"], dependencies=[Depends(get_db)])
app.include_router(frequencies_router, prefix=f"{PROD_PREFIX}/frequencies", tags=["frequencies"], dependencies=[Depends(get_db)])
app.include_router(lengths_router, prefix=f"{PROD_PREFIX}/lengths", tags=["lengths"], dependencies=[Depends(get_db)])
app.include_router(states_router, prefix=f"{PROD_PREFIX}/states", tags=["states"], dependencies=[Depends(get_db)])
app.include_router(task_router, prefix=f"{PROD_PREFIX}/task", tags=["task"], dependencies=[Depends(get_db)])
app.include_router(taskgroup_router, prefix=f"{PROD_PREFIX}/taskgroup", tags=["taskgroup"], dependencies=[Depends(get_db)])
app.include_router(tasks_router, prefix=f"{PROD_PREFIX}/tasks", tags=["tasks"], dependencies=[Depends(get_db)])
app.include_router(text_router, prefix=f"{PROD_PREFIX}/text", tags=["text"], dependencies=[Depends(get_db)])
app.include_router(texts_router, prefix=f"{PROD_PREFIX}/texts", tags=["texts"], dependencies=[Depends(get_db)])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
