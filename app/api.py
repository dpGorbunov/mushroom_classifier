from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from database.database import init_db
from routes.auth import router as auth_router
from routes.prediction import router as predictions_router
from routes.transaction import router as transactions_router
from routes.user import router as users_router
from routes.web import web_router
import uvicorn
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="ML Service API")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(transactions_router, prefix="/transactions")
app.include_router(predictions_router, prefix="/predictions")
app.include_router(users_router, prefix="/users")
app.include_router(web_router)


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=True)