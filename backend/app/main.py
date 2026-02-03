from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.scenes.routes import router as scenes_router
from app.projects.routes import router as projects_router
from app.character.routes import router as character_router

app = FastAPI(title="Veo Backend")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])
app.include_router(scenes_router, prefix="/scenes", tags=["Scenes"])
app.include_router(character_router, prefix="/gemini", tags=["Gemini AI"])

