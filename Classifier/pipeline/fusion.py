from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from inference.predictor import PredictionResult
from inference.weather_api import VisibilityClass

HIGH_CONFIDENCE = 0.85
LOW_CONFIDENCE  = 0.60


@dataclass
class FusionResult:
    final_class: str
    model_prediction: str
    model_confidence: float
    api_prediction: str
    fusion_strategy_used: str


class WeatherFusion:
    """Confidence-gated fusion of camera model + weather API.

    >= 0.85  → model only
    0.60–0.85 → weighted vote (70% model, 30% API)
    < 0.60   → API only
    """

    CLASS_ORDER = ["CLEAR", "MEDIUM_FOG", "HEAVY_FOG"]

    def __init__(self, high_threshold: float = HIGH_CONFIDENCE, low_threshold: float = LOW_CONFIDENCE, model_weight: float = 0.7) -> None:
        if not (0.0 <= low_threshold < high_threshold <= 1.0):
            raise ValueError("Thresholds must satisfy 0 <= low_threshold < high_threshold <= 1.")
        if not (0.0 < model_weight < 1.0):
            raise ValueError("model_weight must be in (0, 1).")

        self.high_threshold = high_threshold
        self.low_threshold  = low_threshold
        self.model_weight   = model_weight
        self.api_weight     = 1.0 - model_weight

    def decide(self, model_result: PredictionResult, api_result: VisibilityClass) -> FusionResult:
        confidence  = model_result.confidence
        model_class = model_result.class_label
        api_class   = api_result.value

        if confidence >= self.high_threshold:
            final_class, strategy = model_class, "model_only"
        elif confidence >= self.low_threshold:
            final_class, strategy = self._weighted_vote(model_result, api_class), "weighted_vote"
        else:
            final_class, strategy = api_class, "api_only"

        return FusionResult(
            final_class=final_class,
            model_prediction=model_class,
            model_confidence=confidence,
            api_prediction=api_class,
            fusion_strategy_used=strategy,
        )

    def _weighted_vote(self, model_result: PredictionResult, api_class: str) -> str:
        model_probs = np.array([model_result.all_probabilities.get(cls, 0.0) for cls in self.CLASS_ORDER], dtype=np.float64)

        api_onehot = np.zeros(len(self.CLASS_ORDER), dtype=np.float64)
        if api_class in self.CLASS_ORDER:
            api_onehot[self.CLASS_ORDER.index(api_class)] = 1.0
        else:
            api_onehot[:] = 1.0 / len(self.CLASS_ORDER)

        combined = self.model_weight * model_probs + self.api_weight * api_onehot
        return self.CLASS_ORDER[int(np.argmax(combined))]
