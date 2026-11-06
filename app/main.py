from fastapi  import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from framework.config import settings
from framework.web.error_handlers import register_error_handlers
from framework.web.routers.auth import router as auth_router
from framework.web.routers.tasks import router as tasks_router

app = FastAPI(title="API CRUD - Clean Architecture")

app.add_middleware(
    CORSMiddleware,
    allow_origins= settings.cors_origin,
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers= ["*"],
)

register_error_handlers(app)
app.include_router(auth_router)
app.include_router(tasks_router)        