from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.api.deps import get_db, get_current_user, require_roles
from app.models.user import User
from app.models.well import Well
from app.models.village import Village
from app.models.well_type import WellType
from app.models.inspection_record import InspectionRecord
from app.schemas.well import WellCreate, WellUpdate, WellListResponse
from app.schemas.common import PageResponse

router = APIRouter()


def update_overdue_status(db: Session, well_id: int = None):
    query = db.query(Well).join(WellType).filter(WellType.inspection_cycle_days is not None)

    if well_id:
        query = query.filter(Well.id == well_id)

    wells = query.all()
    for well in wells:
        if well.last_inspection_date and well.well_type:
            cycle_days = well.well_type.inspection_cycle_days
            next_date = well.last_inspection_date + timedelta(days=cycle_days)
            well.next_inspection_date = next_date
            well.inspection_overdue = 1 if datetime.now() > next_date else 0
        elif not well.last_inspection_date:
            well.inspection_overdue = 1

    db.commit()


@router.get("", response_model=PageResponse[WellListResponse])
def list_wells(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str = Query(None),
    village_id: int = Query(None),
    overdue_only: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_overdue_status(db)

    query = db.query(
        Well,
        Village.name.label("village_name"),
        WellType.name.label("well_type_name")
    ).join(Village).join(WellType)

    if keyword:
        query = query.filter(
            or_(
                Well.well_code.like(f"%{keyword}%"),
                Well.location.like(f"%{keyword}%")
            )
        )

    if village_id:
        query = query.filter(Well.village_id == village_id)

    if overdue_only is not None:
        query = query.filter(Well.inspection_overdue == overdue_only)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for well, village_name, well_type_name in items:
        well_dict = well.__dict__.copy()
        well_dict["village_name"] = village_name
        well_dict["well_type_name"] = well_type_name
        result.append(WellListResponse(**well_dict))

    return PageResponse(
        items=result,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{well_id}", response_model=WellListResponse)
def get_well(
    well_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_overdue_status(db, well_id)

    result = db.query(
        Well,
        Village.name.label("village_name"),
        WellType.name.label("well_type_name")
    ).join(Village).join(WellType).filter(Well.id == well_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="井不存在")

    well, village_name, well_type_name = result
    well_dict = well.__dict__.copy()
    well_dict["village_name"] = village_name
    well_dict["well_type_name"] = well_type_name
    return WellListResponse(**well_dict)


@router.post("", response_model=WellListResponse)
def create_well(
    well_in: WellCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    existing = db.query(Well).filter(Well.well_code == well_in.well_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="井编号已存在")

    well = Well(**well_in.dict())
    well.inspection_overdue = 1
    db.add(well)
    db.commit()
    db.refresh(well)

    result = db.query(
        Well,
        Village.name.label("village_name"),
        WellType.name.label("well_type_name")
    ).join(Village).join(WellType).filter(Well.id == well.id).first()

    well, village_name, well_type_name = result
    well_dict = well.__dict__.copy()
    well_dict["village_name"] = village_name
    well_dict["well_type_name"] = well_type_name
    return WellListResponse(**well_dict)


@router.put("/{well_id}", response_model=WellListResponse)
def update_well(
    well_id: int,
    well_in: WellUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="井不存在")

    for field, value in well_in.dict(exclude_unset=True).items():
        setattr(well, field, value)

    db.commit()
    db.refresh(well)

    result = db.query(
        Well,
        Village.name.label("village_name"),
        WellType.name.label("well_type_name")
    ).join(Village).join(WellType).filter(Well.id == well_id).first()

    well, village_name, well_type_name = result
    well_dict = well.__dict__.copy()
    well_dict["village_name"] = village_name
    well_dict["well_type_name"] = well_type_name
    return WellListResponse(**well_dict)


@router.delete("/{well_id}")
def delete_well(
    well_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="井不存在")

    db.delete(well)
    db.commit()
    return {"message": "删除成功"}
