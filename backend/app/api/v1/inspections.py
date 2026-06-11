from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api.deps import get_db, get_current_user, require_roles
from app.models.user import User
from app.models.well import Well
from app.models.inspection_record import InspectionRecord
from app.core.water_quality_judge import judge_residual_chlorine
from app.api.v1.wells import update_overdue_status
from app.schemas.inspection_record import InspectionRecordCreate, InspectionRecordUpdate, InspectionRecord as InspectionRecordSchema
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[InspectionRecordSchema])
def list_inspections(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    keyword: str = Query(None),
    well_id: int = Query(None),
    status: str = Query(None),
    needs_rectification: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        InspectionRecord,
        User.full_name.label("inspector_name"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(User, InspectionRecord.inspector_id == User.id
    ).join(Well, InspectionRecord.well_id == Well.id)

    if keyword:
        query = query.filter(
            or_(
                Well.well_code.like(f"%{keyword}%"),
                Well.location.like(f"%{keyword}%"),
                InspectionRecord.hidden_dangers.like(f"%{keyword}%")
            )
        )

    if well_id:
        query = query.filter(InspectionRecord.well_id == well_id)

    if status:
        query = query.filter(InspectionRecord.status == status)

    if needs_rectification is not None:
        query = query.filter(InspectionRecord.needs_rectification == needs_rectification)

    if current_user.role == "inspector":
        query = query.filter(InspectionRecord.inspector_id == current_user.id)

    total = query.count()
    items = query.order_by(InspectionRecord.inspection_date.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for record, inspector_name, well_code, well_location in items:
        record_dict = record.__dict__.copy()
        record_dict["inspector_name"] = inspector_name
        record_dict["well_code"] = well_code
        record_dict["well_location"] = well_location
        result.append(InspectionRecordSchema(**record_dict))

    return PageResponse(
        items=result,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{record_id}", response_model=InspectionRecordSchema)
def get_inspection(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(
        InspectionRecord,
        User.full_name.label("inspector_name"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(User, InspectionRecord.inspector_id == User.id
    ).join(Well, InspectionRecord.well_id == Well.id
    ).filter(InspectionRecord.id == record_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="巡检记录不存在")

    record, inspector_name, well_code, well_location = result
    record_dict = record.__dict__.copy()
    record_dict["inspector_name"] = inspector_name
    record_dict["well_code"] = well_code
    record_dict["well_location"] = well_location
    return InspectionRecordSchema(**record_dict)


@router.post("", response_model=InspectionRecordSchema)
def create_inspection(
    record_in: InspectionRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["inspector", "supervisor"]))
):
    well = db.query(Well).filter(Well.id == record_in.well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="井不存在")

    record = InspectionRecord(**record_in.dict())
    record.inspector_id = current_user.id

    if record_in.residual_chlorine:
        status, _ = judge_residual_chlorine(record_in.residual_chlorine)
        record.residual_chlorine_status = status

    if record_in.needs_rectification == 1:
        record.status = "rectifying"
    else:
        record.status = "completed"

    db.add(record)

    well.last_inspection_date = datetime.now()
    well.cover_status = record_in.cover_status
    well.pump_status = record_in.pump_status
    well.drainage_status = record_in.drainage_status
    well.equipment_status = record_in.equipment_status
    well.hidden_dangers = record_in.hidden_dangers
    well.photo_url = record_in.photo_url

    if record_in.needs_rectification == 1:
        well.rectification_responsible = None

    db.commit()
    db.refresh(record)

    update_overdue_status(db, record_in.well_id)

    result = db.query(
        InspectionRecord,
        User.full_name.label("inspector_name"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(User, InspectionRecord.inspector_id == User.id
    ).join(Well, InspectionRecord.well_id == Well.id
    ).filter(InspectionRecord.id == record.id).first()

    record, inspector_name, well_code, well_location = result
    record_dict = record.__dict__.copy()
    record_dict["inspector_name"] = inspector_name
    record_dict["well_code"] = well_code
    record_dict["well_location"] = well_location
    return InspectionRecordSchema(**record_dict)


@router.put("/{record_id}", response_model=InspectionRecordSchema)
def update_inspection(
    record_id: int,
    record_in: InspectionRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["inspector", "supervisor"]))
):
    record = db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="巡检记录不存在")

    if current_user.role == "inspector" and record.inspector_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的巡检记录")

    for field, value in record_in.dict(exclude_unset=True).items():
        if field == "residual_chlorine" and value:
            status, _ = judge_residual_chlorine(value)
            record.residual_chlorine_status = status
            record.residual_chlorine = value
        elif field == "needs_rectification" and value is not None:
            record.needs_rectification = value
            if value == 1:
                record.status = "rectifying"
            else:
                record.status = "completed"
        else:
            setattr(record, field, value)

    db.commit()
    db.refresh(record)

    result = db.query(
        InspectionRecord,
        User.full_name.label("inspector_name"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(User, InspectionRecord.inspector_id == User.id
    ).join(Well, InspectionRecord.well_id == Well.id
    ).filter(InspectionRecord.id == record_id).first()

    record, inspector_name, well_code, well_location = result
    record_dict = record.__dict__.copy()
    record_dict["inspector_name"] = inspector_name
    record_dict["well_code"] = well_code
    record_dict["well_location"] = well_location
    return InspectionRecordSchema(**record_dict)


@router.delete("/{record_id}")
def delete_inspection(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    record = db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="巡检记录不存在")

    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
