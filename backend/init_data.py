import sys
import time
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.village import Village
from app.models.well_type import WellType
from app.models.water_quality_standard import WaterQualityStandard
from app.models.user import User
from app.core.security import get_password_hash


def wait_for_db():
    retries = 30
    while retries > 0:
        try:
            connection = engine.connect()
            connection.close()
            print("数据库连接成功")
            return
        except Exception as e:
            retries -= 1
            print(f"等待数据库连接... 剩余重试次数: {retries}")
            time.sleep(2)
    print("数据库连接超时")
    sys.exit(1)


def init_data():
    wait_for_db()

    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        if db.query(Village).count() == 0:
            villages = [
                Village(name="东村村", code="CUN-001"),
                Village(name="西村村", code="CUN-002"),
                Village(name="南村村", code="CUN-003"),
                Village(name="北村村", code="CUN-004"),
                Village(name="中村村", code="CUN-005"),
            ]
            db.add_all(villages)
            print("已导入村组数据")

        if db.query(WellType).count() == 0:
            well_types = [
                WellType(name="深水井", inspection_cycle_days=15),
                WellType(name="浅水井", inspection_cycle_days=30),
                WellType(name="手压井", inspection_cycle_days=30),
                WellType(name="集中供水井", inspection_cycle_days=10),
            ]
            db.add_all(well_types)
            print("已导入井类型数据")

        if db.query(WaterQualityStandard).count() == 0:
            standards = [
                WaterQualityStandard(indicator_name="总大肠菌群", indicator_code="TC001", unit="MPN/100mL", limit_value=0, comparison_type="<=", category="微生物", priority=1),
                WaterQualityStandard(indicator_name="耐热大肠菌群", indicator_code="TC002", unit="MPN/100mL", limit_value=0, comparison_type="<=", category="微生物", priority=1),
                WaterQualityStandard(indicator_name="大肠埃希氏菌", indicator_code="TC003", unit="MPN/100mL", limit_value=0, comparison_type="<=", category="微生物", priority=1),
                WaterQualityStandard(indicator_name="菌落总数", indicator_code="BC001", unit="CFU/mL", limit_value=100, comparison_type="<=", category="微生物", priority=2),
                WaterQualityStandard(indicator_name="砷", indicator_code="TM001", unit="mg/L", limit_value=0.01, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="镉", indicator_code="TM002", unit="mg/L", limit_value=0.005, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="铬(六价)", indicator_code="TM003", unit="mg/L", limit_value=0.05, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="铅", indicator_code="TM004", unit="mg/L", limit_value=0.01, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="汞", indicator_code="TM005", unit="mg/L", limit_value=0.001, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="硒", indicator_code="TM006", unit="mg/L", limit_value=0.01, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="氰化物", indicator_code="TM007", unit="mg/L", limit_value=0.05, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="氟化物", indicator_code="TM008", unit="mg/L", limit_value=1.0, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="硝酸盐(以N计)", indicator_code="TM009", unit="mg/L", limit_value=20, comparison_type="<=", category="毒理", priority=1),
                WaterQualityStandard(indicator_name="三氯甲烷", indicator_code="TM010", unit="mg/L", limit_value=0.06, comparison_type="<=", category="毒理", priority=2),
                WaterQualityStandard(indicator_name="四氯化碳", indicator_code="TM011", unit="mg/L", limit_value=0.002, comparison_type="<=", category="毒理", priority=2),
                WaterQualityStandard(indicator_name="色度", indicator_code="SP001", unit="度", limit_value=15, comparison_type="<=", category="感官", priority=3),
                WaterQualityStandard(indicator_name="浑浊度", indicator_code="SP002", unit="NTU", limit_value=1, comparison_type="<=", category="感官", priority=3),
                WaterQualityStandard(indicator_name="臭和味", indicator_code="SP003", unit="级", limit_value=0, comparison_type="<=", category="感官", priority=3),
                WaterQualityStandard(indicator_name="肉眼可见物", indicator_code="SP004", unit="", limit_value=0, comparison_type="<=", category="感官", priority=3),
                WaterQualityStandard(indicator_name="pH", indicator_code="GC001", unit="", limit_value=6.5, comparison_type=">=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="pH上限", indicator_code="GC001-2", unit="", limit_value=8.5, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="铝", indicator_code="GC002", unit="mg/L", limit_value=0.2, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="铁", indicator_code="GC003", unit="mg/L", limit_value=0.3, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="锰", indicator_code="GC004", unit="mg/L", limit_value=0.1, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="铜", indicator_code="GC005", unit="mg/L", limit_value=1.0, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="锌", indicator_code="GC006", unit="mg/L", limit_value=1.0, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="氯化物", indicator_code="GC007", unit="mg/L", limit_value=250, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="硫酸盐", indicator_code="GC008", unit="mg/L", limit_value=250, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="溶解性总固体", indicator_code="GC009", unit="mg/L", limit_value=1000, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="总硬度(以CaCO3计)", indicator_code="GC010", unit="mg/L", limit_value=450, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="耗氧量", indicator_code="GC011", unit="mg/L", limit_value=3, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="挥发酚类", indicator_code="GC012", unit="mg/L", limit_value=0.002, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="阴离子合成洗涤剂", indicator_code="GC013", unit="mg/L", limit_value=0.3, comparison_type="<=", category="一般化学", priority=3),
                WaterQualityStandard(indicator_name="总放射性", indicator_code="RD001", unit="Bq/L", limit_value=0.5, comparison_type="<=", category="放射性", priority=4),
                WaterQualityStandard(indicator_name="总β放射性", indicator_code="RD002", unit="Bq/L", limit_value=1, comparison_type="<=", category="放射性", priority=4),
            ]
            db.add_all(standards)
            print("已导入水质指标模板数据")

        if db.query(User).count() == 0:
            users = [
                User(username="admin", password_hash=get_password_hash("admin123"), full_name="系统管理员", role="supervisor", phone="13800000001"),
                User(username="inspector1", password_hash=get_password_hash("123456"), full_name="张三", role="inspector", phone="13800000002"),
                User(username="inspector2", password_hash=get_password_hash("123456"), full_name="李四", role="inspector", phone="13800000003"),
                User(username="rectifier1", password_hash=get_password_hash("123456"), full_name="王五", role="rectifier", phone="13800000004"),
                User(username="rectifier2", password_hash=get_password_hash("123456"), full_name="赵六", role="rectifier", phone="13800000005"),
                User(username="tester1", password_hash=get_password_hash("123456"), full_name="钱七", role="tester", phone="13800000006"),
                User(username="supervisor1", password_hash=get_password_hash("123456"), full_name="孙八", role="supervisor", phone="13800000007"),
            ]
            db.add_all(users)
            print("已导入用户账号数据")

        db.commit()
        print("初始化数据导入完成")

    except Exception as e:
        db.rollback()
        print(f"初始化数据失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_data()
