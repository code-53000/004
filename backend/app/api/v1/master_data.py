from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_roles
from app.models.user import User
from app.models.village import Village
from app.models.well_type import WellType
from app.models.water_quality_standard import WaterQualityStandard
from app.schemas.village import VillageCreate, Village
from app.schemas.well_type import WellTypeCreate, WellType
from app.schemas.water_quality_standard import WaterQualityStandardCreate, WaterQualityStandard

router = APIRouter()


@router.get("/villages", response_model=List[Village])
def list_villages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Village).order_by(Village.code).all()


@router.post("/villages", response_model=Village)
def create_village(
    village_in: VillageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    existing = db.query(Village).filter(
        (Village.name == village_in.name) | (Village.code == village_in.code)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="村组名称或编码已存在")

    village = Village(**village_in.dict())
    db.add(village)
    db.commit()
    db.refresh(village)
    return village


@router.put("/villages/{village_id}", response_model=Village)
def update_village(
    village_id: int,
    village_in: VillageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="村组不存在")

    existing = db.query(Village).filter(
        ((Village.name == village_in.name) | (Village.code == village_in.code)) &
        (Village.id != village_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="村组名称或编码已存在")

    village.name = village_in.name
    village.code = village_in.code
    db.commit()
    db.refresh(village)
    return village


@router.delete("/villages/{village_id}")
def delete_village(
    village_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="村组不存在")

    if village.wells:
        raise HTTPException(status_code=400, detail="该村组下还有水井，无法删除")

    db.delete(village)
    db.commit()
    return {"message": "删除成功"}


@router.get("/well-types", response_model=List[WellType])
def list_well_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(WellType).order_by(WellType.name).all()


@router.post("/well-types", response_model=WellType)
def create_well_type(
    well_type_in: WellTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    existing = db.query(WellType).filter(WellType.name == well_type_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="井类型已存在")

    well_type = WellType(**well_type_in.dict())
    db.add(well_type)
    db.commit()
    db.refresh(well_type)
    return well_type


@router.put("/well-types/{type_id}", response_model=WellType)
def update_well_type(
    type_id: int,
    well_type_in: WellTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    well_type = db.query(WellType).filter(WellType.id == type_id).first()
    if not well_type:
        raise HTTPException(status_code=404, detail="井类型不存在")

    existing = db.query(WellType).filter(
        (WellType.name == well_type_in.name) & (WellType.id != type_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="井类型已存在")

    well_type.name = well_type_in.name
    well_type.inspection_cycle_days = well_type_in.inspection_cycle_days
    db.commit()
    db.refresh(well_type)
    return well_type


@router.delete("/well-types/{type_id}")
def delete_well_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    well_type = db.query(WellType).filter(WellType.id == type_id).first()
    if not well_type:
        raise HTTPException(status_code=404, detail="井类型不存在")

    if well_type.wells:
        raise HTTPException(status_code=400, detail="该类型下还有水井，无法删除")

    db.delete(well_type)
    db.commit()
    return {"message": "删除成功"}


@router.get("/water-quality-standards", response_model=List[WaterQualityStandard])
def list_water_quality_standards(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(WaterQualityStandard)
    if category:
        query = query.filter(WaterQualityStandard.category == category)
    return query.order_by(WaterQualityStandard.priority, WaterQualityStandard.indicator_name).all()


@router.post("/water-quality-standards", response_model=WaterQualityStandard)
def create_water_quality_standard(
    standard_in: WaterQualityStandardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    existing = db.query(WaterQualityStandard).filter(
        (WaterQualityStandard.indicator_name == standard_in.indicator_name) |
        (WaterQualityStandard.indicator_code == standard_in.indicator_code)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="指标名称或编码已存在")

    standard = WaterQualityStandard(**standard_in.dict())
    db.add(standard)
    db.commit()
    db.refresh(standard)
    return standard


@router.put("/water-quality-standards/{standard_id}", response_model=WaterQualityStandard)
def update_water_quality_standard(
    standard_id: int,
    standard_in: WaterQualityStandardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    standard = db.query(WaterQualityStandard).filter(
        WaterQualityStandard.id == standard_id
    ).first()
    if not standard:
        raise HTTPException(status_code=404, detail="水质指标不存在")

    existing = db.query(WaterQualityStandard).filter(
        ((WaterQualityStandard.indicator_name == standard_in.indicator_name) |
         (WaterQualityStandard.indicator_code == standard_in.indicator_code)) &
        (WaterQualityStandard.id != standard_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="指标名称或编码已存在")

    for field, value in standard_in.dict().items():
        setattr(standard, field, value)

    db.commit()
    db.refresh(standard)
    return standard


@router.delete("/water-quality-standards/{standard_id}")
def delete_water_quality_standard(
    standard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    standard = db.query(WaterQualityStandard).filter(
        WaterQualityStandard.id == standard_id
    ).first()
    if not standard:
        raise HTTPException(status_code=404, detail="水质指标不存在")

    if standard.test_items:
        raise HTTPException(status_code=400, detail="该指标下还有检测数据，无法删除")

    db.delete(standard)
    db.commit()
    return {"message": "删除成功"}
