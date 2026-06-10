from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api.deps import get_db, get_current_user, require_roles
from app.models.user import User
from app.models.well import Well
from app.models.inspection_record import InspectionRecord
from app.models.rectification_record import RectificationRecord
from app.schemas.rectification_record import RectificationRecordCreate, RectificationRecordUpdate, RectificationRecord
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[RectificationRecord])
def list_rectifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str = Query(None),
    inspection_id: int = Query(None),
    status: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        RectificationRecord,
        User.full_name.label("rectifier_name"),
        InspectionRecord.inspection_date.label("inspection_date"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(User, RectificationRecord.rectifier_id == User.id
    ).join(InspectionRecord, RectificationRecord.inspection_id == InspectionRecord.id
    ).join(Well, InspectionRecord.well_id == Well.id)

    if keyword:
        query = query.filter(
            or_(
                Well.well_code.like(f"%{keyword}%"),
                Well.location.like(f"%{keyword}%"),
                RectificationRecord.measures.like(f"%{keyword}%")
            )
        )

    if inspection_id:
        query = query.filter(RectificationRecord.inspection_id == inspection_id)

    if status:
        query = query.filter(RectificationRecord.status == status)

    if current_user.role == "rectifier":
        query = query.filter(RectificationRecord.rectifier_id == current_user.id)

    total = query.count()
    items = query.order_by(RectificationRecord.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for record, rectifier_name, inspection_date, well_code, well_location in items:
        record_dict = record.__dict__.copy()
        record_dict["rectifier_name"] = rectifier_name
        record_dict["inspection_date"] = inspection_date
        record_dict["well_code"] = well_code
        record_dict["well_location"] = well_location
        result.append(RectificationRecord(**record_dict))

    return PageResponse(
        items=result,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{record_id}", response_model=RectificationRecord)
def get_rectification(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(
        RectificationRecord,
        User.full_name.label("rectifier_name"),
        InspectionRecord.inspection_date.label("inspection_date"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(User, RectificationRecord.rectifier_id == User.id
    ).join(InspectionRecord, RectificationRecord.inspection_id == InspectionRecord.id
    ).join(Well, InspectionRecord.well_id == Well.id
    ).filter(RectificationRecord.id == record_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="整改记录不存在")

    record, rectifier_name, inspection_date, well_code, well_location = result
    record_dict = record.__dict__.copy()
    record_dict["rectifier_name"] = rectifier_name
    record_dict["inspection_date"] = inspection_date
    record_dict["well_code"] = well_code
    record_dict["well_location"] = well_location
    return RectificationRecord(**record_dict)


@router.post("", response_model=RectificationRecord)
def create_rectification(
    record_in: RectificationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["rectifier", "supervisor"]))
):
    inspection = db.query(InspectionRecord).filter(
        InspectionRecord.id == record_in.inspection_id
    ).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="巡检记录不存在")

    record = RectificationRecord(**record_in.dict())
    record.rectifier_id = current_user.id
    record.status = "in_progress"

    db.add(record)
    db.commit()
    db.refresh(record)

    result = db.query(
        RectificationRecord,
        User.full_name.label("rectifier_name"),
        InspectionRecord.inspection_date.label("inspection_date"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(User, RectificationRecord.rectifier_id == User.id
    ).join(InspectionRecord, RectificationRecord.inspection_id == InspectionRecord.id
    ).join(Well, InspectionRecord.well_id == Well.id
    ).filter(RectificationRecord.id == record.id).first()

    record, rectifier_name, inspection_date, well_code, well_location = result
    record_dict = record.__dict__.copy()
    record_dict["rectifier_name"] = rectifier_name
    record_dict["inspection_date"] = inspection_date
    record_dict["well_code"] = well_code
    record_dict["well_location"] = well_location
    return RectificationRecord(**record_dict)


@router.put("/{record_id}", response_model=RectificationRecord)
def update_rectification(
    record_id: int,
    record_in: RectificationRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["rectifier", "supervisor"]))
):
    record = db.query(RectificationRecord).filter(RectificationRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="整改记录不存在")

    if current_user.role == "rectifier" and record.rectifier_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的整改记录")

    for field, value in record_in.dict(exclude_unset=True).items():
        if field == "status" and value == "completed" and not record.rectification_date:
            record.rectification_date = datetime.now().date()
        setattr(record, field, value)

    if record_in.status == "completed" or record.status == "completed":
        inspection = db.query(InspectionRecord).filter(
            InspectionRecord.id == record.inspection_id
        ).first()
        if inspection:
            inspection.status = "rectified"

    db.commit()
    db.refresh(record)

    result = db.query(
        RectificationRecord,
        User.full_name.label("rectifier_name"),
        InspectionRecord.inspection_date.label("inspection_date"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(User, RectificationRecord.rectifier_id == User.id
    ).join(InspectionRecord, RectificationRecord.inspection_id == InspectionRecord.id
    ).join(Well, InspectionRecord.well_id == Well.id
    ).filter(RectificationRecord.id == record_id).first()

    record, rectifier_name, inspection_date, well_code, well_location = result
    record_dict = record.__dict__.copy()
    record_dict["rectifier_name"] = rectifier_name
    record_dict["inspection_date"] = inspection_date
    record_dict["well_code"] = well_code
    record_dict["well_location"] = well_location
    return RectificationRecord(**record_dict)


@router.delete("/{record_id}")
def delete_rectification(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    record = db.query(RectificationRecord).filter(RectificationRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="整改记录不存在")

    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
