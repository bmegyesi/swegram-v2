import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.models import Base
from server.routers.database import engine, get_db
from server.routers.features import router as features_router
from server.routers.frequencies import router as frequencies_router
from server.routers.lengths import router as lengths_router
from server.routers.states import router as states_router
from server.routers.text import router as text_router
from server.routers.texts import router as texts_router


app = FastAPI()
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
app.include_router(features_router, prefix=f"{PROD_PREFIX}/features", tags=["features"], dependencies=[Depends(get_db)])
app.include_router(frequencies_router, prefix=f"{PROD_PREFIX}/frequencies", tags=["frequencies"], dependencies=[Depends(get_db)])
app.include_router(lengths_router, prefix=f"{PROD_PREFIX}/lengths", tags=["lengths"], dependencies=[Depends(get_db)])
app.include_router(states_router, prefix=f"{PROD_PREFIX}/states", tags=["states"], dependencies=[Depends(get_db)])
app.include_router(text_router, prefix=f"{PROD_PREFIX}/text", tags=["text"], dependencies=[Depends(get_db)])
app.include_router(texts_router, prefix=f"{PROD_PREFIX}/texts", tags=["texts"], dependencies=[Depends(get_db)])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
