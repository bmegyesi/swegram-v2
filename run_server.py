from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.models import Base
from server.routers.database import engine, get_db
from server.routers.states import router as states_router
from server.routers.text import router as text_router
from server.routers.texts import router as texts_router


app = FastAPI()


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
app.include_router(states_router, prefix="/api/states", tags=["states"], dependencies=[Depends(get_db)])
app.include_router(text_router, prefix="/api/text", tags=["text"], dependencies=[Depends(get_db)])
app.include_router(texts_router, prefix="/api/texts", tags=["texts"], dependencies=[Depends(get_db)])

