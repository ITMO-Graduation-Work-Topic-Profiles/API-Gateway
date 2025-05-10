__all__ = ["recalculate_weight"]


def recalculate_weight(
    old_weight: float,
    new_weight: float,
    *,
    alpha: float = 0.8,
    precision: int = 2,
) -> float:
    result = alpha * old_weight + (1 - alpha) * new_weight
    return round(result, precision)
