from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.v1 import auth, dish, inventory, marketing, member, merchant_profile, order, service, staff, table
from app.api.v1.platform import auth as platform_auth
from app.api.v1.platform import dashboard as platform_dashboard
from app.api.v1.platform import merchants as platform_merchants
from app.api.v1.customer import auth as customer_auth
from app.api.v1.customer import menu as customer_menu
from app.core.response import fail
from app.core.tenant import TenantMiddleware
MERCHANT_PREFIX = "/api/v1/merchant"
PLATFORM_PREFIX = "/api/v1/platform"
CUSTOMER_PREFIX = "/api/v1/customer"

app = FastAPI(title="SmartDine API", version="2.0.0")

# Middleware: CORS first, then tenant extraction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TenantMiddleware)

# ========== 商户管理端路由（原 V1.0 路由，统一加 /merchant 前缀） ==========
app.include_router(auth.router, prefix=MERCHANT_PREFIX)               # /api/v1/merchant/auth/*
app.include_router(dish.router, prefix=MERCHANT_PREFIX)               # /api/v1/merchant/dishes/*
app.include_router(order.router, prefix=MERCHANT_PREFIX)              # /api/v1/merchant/orders/*
app.include_router(table.router, prefix=MERCHANT_PREFIX)              # /api/v1/merchant/tables/*
app.include_router(inventory.router, prefix=MERCHANT_PREFIX)          # /api/v1/merchant/ingredients|stock-logs|suppliers
app.include_router(member.router, prefix=MERCHANT_PREFIX)             # /api/v1/merchant/members/*
app.include_router(marketing.router, prefix=MERCHANT_PREFIX)          # /api/v1/merchant/campaigns|/coupons
app.include_router(staff.router, prefix=MERCHANT_PREFIX)              # /api/v1/merchant/staff/*
app.include_router(service.router, prefix=MERCHANT_PREFIX)            # /api/v1/merchant/service/tickets/*
app.include_router(merchant_profile.router, prefix=MERCHANT_PREFIX)   # /api/v1/merchant/profile

# ========== 平台管理端路由（V2.0 新增） ==========
app.include_router(platform_auth.router, prefix=PLATFORM_PREFIX)       # /api/v1/platform/auth/*
app.include_router(platform_merchants.router, prefix=PLATFORM_PREFIX)  # /api/v1/platform/merchants/*
app.include_router(platform_dashboard.router, prefix=PLATFORM_PREFIX)  # /api/v1/platform/dashboard

# ========== 用户端路由（V2.0 新增） ==========
app.include_router(customer_auth.router, prefix=CUSTOMER_PREFIX)       # /api/v1/customer/auth/*
app.include_router(customer_menu.router, prefix=CUSTOMER_PREFIX)       # /api/v1/customer/merchants/*


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """将 HTTPException 转换为统一响应结构，使前端能读取到 message 字段"""
    return JSONResponse(status_code=exc.status_code, content=fail(exc.status_code, exc.detail))


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
