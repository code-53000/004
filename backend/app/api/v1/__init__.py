from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.wells import router as wells_router
from app.api.v1.inspections import router as inspections_router
from app.api.v1.rectifications import router as rectifications_router
from app.api.v1.water_tests import router as water_tests_router
from app.api.v1.master_data import router as master_data_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(wells_router, prefix="/wells", tags=["水井管理"])
api_router.include_router(inspections_router, prefix="/inspections", tags=["巡检记录"])
api_router.include_router(rectifications_router, prefix="/rectifications", tags=["整改记录"])
api_router.include_router(water_tests_router, prefix="/water-tests", tags=["水质检测"])
api_router.include_router(master_data_router, prefix="/master-data", tags=["基础数据"])
