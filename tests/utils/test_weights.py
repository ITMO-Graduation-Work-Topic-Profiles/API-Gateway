from src.utils.weights import recalculate_weight


class TestRecalculateWeight:
    def test_recalculate_weight_with_default_params(self) -> None:
        old_weight = 0.8
        new_weight = 0.9

        result = recalculate_weight(old_weight, new_weight)

        assert result == 0.82

    def test_recalculate_weight_with_custom_alpha(self) -> None:
        old_weight = 0.8
        new_weight = 0.9
        alpha = 0.5

        result = recalculate_weight(old_weight, new_weight, alpha=alpha)

        assert result == 0.85

    def test_recalculate_weight_with_custom_precision(self) -> None:
        old_weight = 0.8
        new_weight = 0.9
        precision = 3

        result = recalculate_weight(old_weight, new_weight, precision=precision)

        assert result == 0.82

    def test_recalculate_weight_with_edge_case_values(self) -> None:
        result = recalculate_weight(0.5, 0.9, alpha=0)
        assert result == 0.9

        result = recalculate_weight(0.5, 0.9, alpha=1)
        assert result == 0.5

        result = recalculate_weight(0, 0)
        assert result == 0

        result = recalculate_weight(1, 1)
        assert result == 1
