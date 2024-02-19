from fastapi import FastAPI, Depends

from server.models import Base
from server.routers.database import engine, get_db
from server.routers.states import router as states_router
from server.routers.text import router as text_router
from server.routers.texts import router as texts_router


app = FastAPI()
# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(states_router, prefix="/states", tags=["states"], dependencies=[Depends(get_db)])
app.include_router(text_router, prefix="/text", tags=["text"], dependencies=[Depends(get_db)])
app.include_router(texts_router, prefix="/texts", tags=["texts"], dependencies=[Depends(get_db)])
