from fastapi import FastAPI, Request
from routers import users, images, classifications, auth, logs
from services.classification import load_model_wrapper
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inside lifespan - before loading model")
    try:
        load_model_wrapper()
        print("Model loaded successfully")
    except Exception as e:
        print(f"Failed to load model: {str(e)}")
        raise 
    print("Yielding from lifespan")
    yield
    print("Lifespan shutdown")

app = FastAPI(
    title="Crop Health Analysis Backend",
    description="Backend for NDVI-based crop health monitoring",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication endpoints"},
        {"name": "Users", "description": "User management endpoints"},
        {"name": "Images", "description": "Image upload and management endpoints"},
        {"name": "Classifications", "description": "Image classification endpoints"},
        {"name": "Logs", "description": "Log management endpoints"},
    ],
    openapi_extra={
        "security": [{"BearerAuth": []}],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        }
    }
)

@app.middleware("http")
async def set_supabase_auth(request: Request, call_next):
    print("Middleware: Using service role key, skipping token extraction")
    response = await call_next(request)
    return response

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(images.router)
app.include_router(classifications.router)
app.include_router(logs.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Crop Health Analysis Backend"}