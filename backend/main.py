from fastapi import FastAPI, Depends
from backend.database.db_connection import connect_to_db
from backend.routers.file_route import router as file_router
from backend.routers.query_route import router as embedding_router
from backend.routers.doc_route import router as doc_router

app = FastAPI(docs_url=None, redoc_url=None)

app.include_router(doc_router)

app.include_router(file_router, prefix="/api/v1")
app.include_router(embedding_router, prefix="/api/v1")

@app.get("/db_connection")
async def get_db(db=Depends(connect_to_db)):
    return {"db_connection": str(db)}
