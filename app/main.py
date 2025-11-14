from fastapi import FastAPI
from app.core.config import settings
from app.api import auth,bot
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Upload a pdf and ask question about it!!!",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/system-check/")
def system_route():
    return {"success":"system loads perfectly"}

app.include_router(auth.router,prefix="/api/auth",tags=["Auth Routers"])
app.include_router(bot.router,prefix="/api/bot",tags=["Chatbot Routers"])

