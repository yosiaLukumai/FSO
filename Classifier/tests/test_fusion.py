import pytest

from inference.predictor import PredictionResult
from inference.weather_api import VisibilityClass
from pipeline.fusion import FusionResult, WeatherFusion

CLASS_ORDER = ["CLEAR", "MEDIUM_FOG", "HEAVY_FOG"]


def _make_prediction(class_label, confidence, probs=None):
    class_index = CLASS_ORDER.index(class_label)
    if probs is None:
        remaining = (1.0 - confidence) / 2
        probs = {cls: remaining for cls in CLASS_ORDER}
        probs[class_label] = confidence
    return PredictionResult(
        class_label=class_label,
        class_index=class_index,
        confidence=confidence,
        all_probabilities=probs,
    )


@pytest.fixture()
def fusion():
    return WeatherFusion()


class TestStrategySelection:
    def test_high_confidence_uses_model(self, fusion):
        result = fusion.decide(_make_prediction("CLEAR", 0.95), VisibilityClass.MEDIUM_FOG)
        assert result.fusion_strategy_used == "model_only"

    def test_high_confidence_boundary(self, fusion):
        result = fusion.decide(_make_prediction("CLEAR", 0.85), VisibilityClass.MEDIUM_FOG)
        assert result.fusion_strategy_used == "model_only"

    def test_low_confidence_uses_api(self, fusion):
        result = fusion.decide(_make_prediction("MEDIUM_FOG", 0.40), VisibilityClass.HEAVY_FOG)
        assert result.fusion_strategy_used == "api_only"
        assert result.final_class == "HEAVY_FOG"

    def test_low_confidence_boundary(self, fusion):
        result = fusion.decide(_make_prediction("CLEAR", 0.599), VisibilityClass.MEDIUM_FOG)
        assert result.fusion_strategy_used == "api_only"

    def test_medium_confidence_weighted_vote(self, fusion):
        result = fusion.decide(_make_prediction("CLEAR", 0.75), VisibilityClass.HEAVY_FOG)
        assert result.fusion_strategy_used == "weighted_vote"

    def test_medium_confidence_lower_boundary(self, fusion):
        result = fusion.decide(_make_prediction("CLEAR", 0.60), VisibilityClass.MEDIUM_FOG)
        assert result.fusion_strategy_used == "weighted_vote"


class TestOutputValidity:
    def test_final_class_always_valid(self, fusion):
        for conf in (0.3, 0.7, 0.95):
            for model_cls in CLASS_ORDER:
                for api_cls in VisibilityClass:
                    result = fusion.decide(_make_prediction(model_cls, conf), api_cls)
                    assert result.final_class in CLASS_ORDER

    def test_result_metadata_populated(self, fusion):
        result = fusion.decide(_make_prediction("CLEAR", 0.90), VisibilityClass.MEDIUM_FOG)
        assert result.model_prediction == "CLEAR"
        assert result.api_prediction == "MEDIUM_FOG"
        assert 0.0 <= result.model_confidence <= 1.0

    def test_agreement_high_confidence(self, fusion):
        result = fusion.decide(_make_prediction("HEAVY_FOG", 0.92), VisibilityClass.HEAVY_FOG)
        assert result.final_class == "HEAVY_FOG"
        assert result.fusion_strategy_used == "model_only"

    def test_api_only_matches_api_input(self, fusion):
        for api_cls in VisibilityClass:
            result = fusion.decide(_make_prediction("CLEAR", 0.30), api_cls)
            assert result.final_class == api_cls.value


class TestWeightedVote:
    def test_strong_model_wins(self, fusion):
        probs = {"CLEAR": 0.78, "MEDIUM_FOG": 0.13, "HEAVY_FOG": 0.09}
        result = fusion.decide(_make_prediction("CLEAR", 0.78, probs), VisibilityClass.HEAVY_FOG)
        assert result.fusion_strategy_used == "weighted_vote"
        assert result.final_class == "CLEAR"

    def test_api_overrides_uncertain_model(self, fusion):
        probs = {"CLEAR": 0.34, "MEDIUM_FOG": 0.33, "HEAVY_FOG": 0.33}
        pred = PredictionResult(
            class_label="CLEAR",
            class_index=0,
            confidence=0.70,
            all_probabilities=probs,
        )
        result = fusion.decide(pred, VisibilityClass.HEAVY_FOG)
        assert result.fusion_strategy_used == "weighted_vote"
        assert result.final_class == "HEAVY_FOG"


class TestCustomThresholds:
    def test_strict_thresholds(self):
        fusion = WeatherFusion(high_threshold=0.95, low_threshold=0.80)
        result = fusion.decide(_make_prediction("CLEAR", 0.88), VisibilityClass.CLEAR)
        assert result.fusion_strategy_used == "weighted_vote"

    def test_invalid_thresholds_raises(self):
        with pytest.raises(ValueError):
            WeatherFusion(high_threshold=0.5, low_threshold=0.8)

    def test_invalid_model_weight_raises(self):
        with pytest.raises(ValueError):
            WeatherFusion(model_weight=1.0)
