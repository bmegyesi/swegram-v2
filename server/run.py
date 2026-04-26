import os
import asyncio
import uvicorn

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse

from server.routers.job import router as job_router
from server.routers.task import router as task_router
from server.database.handler import TaskDatabaseHandler, CorpusDatabaseHandler

# Add Background scheduler to automatically remove expired texts in the database
scheduler = BackgroundScheduler()
# scheduler.add_job(remove_texts, CronTrigger(hour=0, minute=0))
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

# # Create tables
# Base.metadata.create_all(bind=engine)

@app.get("/healthcheck")
async def healthcheck():
    return HTMLResponse(content="Application health check runs successfully", status_code=200)


@app.get("/")
async def index() -> RedirectResponse:
    return RedirectResponse(url="/docs")

TaskDatabaseHandler().create_tables()
CorpusDatabaseHandler().create_tables()
app.include_router(job_router, prefix=f"{PROD_PREFIX}/jobs", tags=["jobs"], dependencies=[Depends(TaskDatabaseHandler.get_db)])
app.include_router(task_router, prefix=f"{PROD_PREFIX}/tasks", tags=["tasks"], dependencies=[Depends(TaskDatabaseHandler.get_db)])


# app.include_router(download_router, prefix=f"{PROD_PREFIX}/download", tags=["download"], dependencies=[Depends(get_db)])
# app.include_router(features_router, prefix=f"{PROD_PREFIX}/features", tags=["features"], dependencies=[Depends(get_db)])
# app.include_router(frequencies_router, prefix=f"{PROD_PREFIX}/frequencies", tags=["frequencies"], dependencies=[Depends(get_db)])
# app.include_router(lengths_router, prefix=f"{PROD_PREFIX}/lengths", tags=["lengths"], dependencies=[Depends(get_db)])
# app.include_router(states_router, prefix=f"{PROD_PREFIX}/states", tags=["states"], dependencies=[Depends(get_db)])
# app.include_router(text_router, prefix=f"{PROD_PREFIX}/text", tags=["text"], dependencies=[Depends(get_db)])
# app.include_router(texts_router, prefix=f"{PROD_PREFIX}/texts", tags=["texts"], dependencies=[Depends(get_db)])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
