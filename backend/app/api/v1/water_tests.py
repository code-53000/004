from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api.deps import get_db, get_current_user, require_roles
from app.models.user import User
from app.models.well import Well
from app.models.water_test_batch import WaterTestBatch
from app.models.water_test_item import WaterTestItem
from app.models.water_quality_standard import WaterQualityStandard
from app.core.water_quality_judge import judge_water_quality, calculate_overall_result
from app.schemas.water_test_batch import WaterTestBatchCreate, WaterTestBatch as WaterTestBatchSchema, WaterTestBatchWithItems
from app.schemas.water_test_item import WaterTestItemCreate, WaterTestItem as WaterTestItemSchema
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("/batches", response_model=PageResponse[WaterTestBatchSchema])
def list_test_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    keyword: str = Query(None),
    overall_result: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        WaterTestBatch,
        User.full_name.label("tester_name")
    ).join(User, WaterTestBatch.tester_id == User.id)

    if keyword:
        query = query.filter(
            or_(
                WaterTestBatch.batch_no.like(f"%{keyword}%"),
                WaterTestBatch.lab_name.like(f"%{keyword}%")
            )
        )

    if overall_result:
        query = query.filter(WaterTestBatch.overall_result == overall_result)

    if current_user.role == "tester":
        query = query.filter(WaterTestBatch.tester_id == current_user.id)

    total = query.count()
    items = query.order_by(WaterTestBatch.test_date.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for batch, tester_name in items:
        batch_dict = batch.__dict__.copy()
        batch_dict["tester_name"] = tester_name
        result.append(WaterTestBatchSchema(**batch_dict))

    return PageResponse(
        items=result,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/batches/{batch_id}", response_model=WaterTestBatchWithItems)
def get_test_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    batch_result = db.query(
        WaterTestBatch,
        User.full_name.label("tester_name")
    ).join(User, WaterTestBatch.tester_id == User.id
    ).filter(WaterTestBatch.id == batch_id).first()

    if not batch_result:
        raise HTTPException(status_code=404, detail="检测批次不存在")

    batch, tester_name = batch_result

    items_result = db.query(
        WaterTestItem,
        WaterQualityStandard.indicator_name.label("indicator_name"),
        WaterQualityStandard.indicator_code.label("indicator_code"),
        WaterQualityStandard.unit.label("unit"),
        WaterQualityStandard.limit_value.label("limit_value"),
        WaterQualityStandard.comparison_type.label("comparison_type"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(WaterQualityStandard, WaterTestItem.standard_id == WaterQualityStandard.id
    ).join(Well, WaterTestItem.well_id == Well.id
    ).filter(WaterTestItem.batch_id == batch_id
    ).order_by(WaterQualityStandard.priority, WaterQualityStandard.indicator_name).all()

    test_items = []
    for item, indicator_name, indicator_code, unit, limit_value, comparison_type, well_code, well_location in items_result:
        item_dict = item.__dict__.copy()
        item_dict["indicator_name"] = indicator_name
        item_dict["indicator_code"] = indicator_code
        item_dict["unit"] = unit
        item_dict["limit_value"] = limit_value
        item_dict["comparison_type"] = comparison_type
        item_dict["well_code"] = well_code
        item_dict["well_location"] = well_location
        test_items.append(WaterTestItemSchema(**item_dict))

    batch_dict = batch.__dict__.copy()
    batch_dict["tester_name"] = tester_name
    batch_dict["test_items"] = test_items

    return WaterTestBatchWithItems(**batch_dict)


@router.post("/batches", response_model=WaterTestBatchSchema)
def create_test_batch(
    batch_in: WaterTestBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["tester", "supervisor"]))
):
    existing = db.query(WaterTestBatch).filter(
        WaterTestBatch.batch_no == batch_in.batch_no
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="批次号已存在")

    batch = WaterTestBatch(**batch_in.dict())
    batch.tester_id = current_user.id
    batch.overall_result = "pending"

    db.add(batch)
    db.commit()
    db.refresh(batch)

    batch_dict = batch.__dict__.copy()
    batch_dict["tester_name"] = current_user.full_name
    return WaterTestBatchSchema(**batch_dict)


@router.post("/batches/{batch_id}/items", response_model=WaterTestItemSchema)
def add_test_item(
    batch_id: int,
    item_in: WaterTestItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["tester", "supervisor"]))
):
    batch = db.query(WaterTestBatch).filter(WaterTestBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="检测批次不存在")

    if current_user.role == "tester" and batch.tester_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能向自己创建的批次添加数据")

    well = db.query(Well).filter(Well.id == item_in.well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="井不存在")

    standard = db.query(WaterQualityStandard).filter(
        WaterQualityStandard.id == item_in.standard_id
    ).first()
    if not standard:
        raise HTTPException(status_code=404, detail="水质指标不存在")

    is_qualified, basis = judge_water_quality(item_in.measured_value, standard)

    item = WaterTestItem(**item_in.dict())
    item.batch_id = batch_id
    item.is_qualified = 1 if is_qualified else 0
    item.judgment_basis = basis

    db.add(item)
    db.commit()
    db.refresh(item)

    all_items = db.query(WaterTestItem).filter(WaterTestItem.batch_id == batch_id).all()
    batch.overall_result = calculate_overall_result(all_items)
    db.commit()

    item_dict = item.__dict__.copy()
    item_dict["indicator_name"] = standard.indicator_name
    item_dict["indicator_code"] = standard.indicator_code
    item_dict["unit"] = standard.unit
    item_dict["limit_value"] = standard.limit_value
    item_dict["comparison_type"] = standard.comparison_type
    item_dict["well_code"] = well.well_code
    item_dict["well_location"] = well.location

    return WaterTestItemSchema(**item_dict)


@router.get("/items", response_model=PageResponse[WaterTestItemSchema])
def list_test_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    keyword: str = Query(None),
    well_id: int = Query(None),
    standard_id: int = Query(None),
    is_qualified: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        WaterTestItem,
        WaterQualityStandard.indicator_name.label("indicator_name"),
        WaterQualityStandard.indicator_code.label("indicator_code"),
        WaterQualityStandard.unit.label("unit"),
        WaterQualityStandard.limit_value.label("limit_value"),
        WaterQualityStandard.comparison_type.label("comparison_type"),
        Well.well_code.label("well_code"),
        Well.location.label("well_location")
    ).join(WaterQualityStandard, WaterTestItem.standard_id == WaterQualityStandard.id
    ).join(Well, WaterTestItem.well_id == Well.id
    ).join(WaterTestBatch, WaterTestItem.batch_id == WaterTestBatch.id)

    if keyword:
        query = query.filter(
            or_(
                Well.well_code.like(f"%{keyword}%"),
                Well.location.like(f"%{keyword}%"),
                WaterQualityStandard.indicator_name.like(f"%{keyword}%")
            )
        )

    if well_id:
        query = query.filter(WaterTestItem.well_id == well_id)

    if standard_id:
        query = query.filter(WaterTestItem.standard_id == standard_id)

    if is_qualified is not None:
        query = query.filter(WaterTestItem.is_qualified == is_qualified)

    if current_user.role == "tester":
        query = query.filter(WaterTestBatch.tester_id == current_user.id)

    total = query.count()
    items = query.order_by(WaterTestItem.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for item, indicator_name, indicator_code, unit, limit_value, comparison_type, well_code, well_location in items:
        item_dict = item.__dict__.copy()
        item_dict["indicator_name"] = indicator_name
        item_dict["indicator_code"] = indicator_code
        item_dict["unit"] = unit
        item_dict["limit_value"] = limit_value
        item_dict["comparison_type"] = comparison_type
        item_dict["well_code"] = well_code
        item_dict["well_location"] = well_location
        result.append(WaterTestItemSchema(**item_dict))

    return PageResponse(
        items=result,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.delete("/batches/{batch_id}")
def delete_test_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    batch = db.query(WaterTestBatch).filter(WaterTestBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="检测批次不存在")

    db.delete(batch)
    db.commit()
    return {"message": "删除成功"}


@router.delete("/items/{item_id}")
def delete_test_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["supervisor"]))
):
    item = db.query(WaterTestItem).filter(WaterTestItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="检测项不存在")

    batch_id = item.batch_id
    db.delete(item)
    db.commit()

    remaining_items = db.query(WaterTestItem).filter(WaterTestItem.batch_id == batch_id).all()
    batch = db.query(WaterTestBatch).filter(WaterTestBatch.id == batch_id).first()
    if batch:
        batch.overall_result = calculate_overall_result(remaining_items)
        db.commit()

    return {"message": "删除成功"}
