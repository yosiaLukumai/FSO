from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

import numpy as np
import onnxruntime as ort
from PIL import Image

_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGENET_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)


@dataclass
class PredictionResult:
    class_label: str
    class_index: int
    confidence: float
    all_probabilities: dict[str, float]


class ONNXPredictor:
    CLASSES = ["CLEAR", "MEDIUM_FOG", "HEAVY_FOG"]

    def __init__(self, model_path: Union[str, Path], image_size: int = 224, resize_to: int = 256) -> None:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"ONNX model not found: {model_path}")

        self.image_size = image_size
        self.resize_to = resize_to

        opts = ort.SessionOptions()
        opts.log_severity_level = 3
        self._session = ort.InferenceSession(str(model_path), sess_options=opts, providers=["CPUExecutionProvider"])
        self._input_name  = self._session.get_inputs()[0].name
        self._output_name = self._session.get_outputs()[0].name

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected BGR image (H, W, 3), got {image.shape}")

        rgb = image[:, :, ::-1].astype(np.float32)

        h, w = rgb.shape[:2]
        if h < w:
            new_h, new_w = self.resize_to, int(w * self.resize_to / h)
        else:
            new_h, new_w = int(h * self.resize_to / w), self.resize_to

        pil = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), mode="RGB")
        rgb = np.array(pil.resize((new_w, new_h), Image.BILINEAR), dtype=np.float32)

        h2, w2 = rgb.shape[:2]
        top  = (h2 - self.image_size) // 2
        left = (w2 - self.image_size) // 2
        rgb  = rgb[top:top + self.image_size, left:left + self.image_size]

        rgb = (rgb / 255.0 - _IMAGENET_MEAN) / _IMAGENET_STD
        return rgb.transpose(2, 0, 1)[np.newaxis, ...].astype(np.float32)

    def predict(self, image: np.ndarray) -> PredictionResult:
        logits = self._session.run([self._output_name], {self._input_name: self.preprocess(image)})[0][0]

        exp = np.exp(logits - logits.max())
        probs = exp / exp.sum()

        idx = int(np.argmax(probs))
        return PredictionResult(
            class_label=self.CLASSES[idx],
            class_index=idx,
            confidence=float(probs[idx]),
            all_probabilities={cls: float(probs[i]) for i, cls in enumerate(self.CLASSES)},
        )
