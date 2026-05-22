


from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth_router, admin_router, common_router, static_data_router

app = FastAPI()


load_dotenv()


origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(router = auth_router.router, prefix="/api/auth", tags=["User"])
app.include_router(router = admin_router.router, prefix="/api/admin", tags=["Admin"])
app.include_router(router = common_router.router, prefix="/api/common", tags=["Common"])
app.include_router(router = static_data_router.router, prefix="/api/static", tags=["Static"])
