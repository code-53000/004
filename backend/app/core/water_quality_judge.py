import operator
from typing import Tuple
from app.models.water_quality_standard import WaterQualityStandard


COMPARISON_OPERATORS = {
    "<=": operator.le,
    ">=": operator.ge,
    "<": operator.lt,
    ">": operator.gt,
    "==": operator.eq,
}


def judge_water_quality(
    measured_value: float,
    standard: WaterQualityStandard
) -> Tuple[bool, str]:
    op = COMPARISON_OPERATORS.get(standard.comparison_type)
    if not op:
        return False, f"无效的比较类型: {standard.comparison_type}"

    is_qualified = op(measured_value, standard.limit_value)
    basis = f"{standard.indicator_name}: {measured_value}{standard.unit} {standard.comparison_type} {standard.limit_value}{standard.unit}"

    return is_qualified, basis


def judge_residual_chlorine(measured_value: str) -> Tuple[str, str]:
    try:
        value = float(measured_value)
    except (ValueError, TypeError):
        return "unknown", "无法解析的余氯值"

    if value < 0.3:
        return "low", f"余氯偏低: {value}mg/L (标准≥0.3mg/L)"
    elif value > 4.0:
        return "high", f"余氯偏高: {value}mg/L (标准≤4.0mg/L)"
    else:
        return "normal", f"余氯正常: {value}mg/L"


def calculate_overall_result(test_items: list) -> str:
    if not test_items:
        return "pending"

    qualified_count = sum(1 for item in test_items if item.is_qualified == 1)
    total_count = len(test_items)

    if qualified_count == total_count:
        return "qualified"
    else:
        return "unqualified"
