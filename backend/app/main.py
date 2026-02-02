from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.scenes.routes import router as scenes_router

app = FastAPI(title="Veo Backend")

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(scenes_router, prefix="/scenes", tags=["Scenes"])
