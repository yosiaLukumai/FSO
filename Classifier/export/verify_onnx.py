from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch

from models.classifier import CLASS_NAMES, FogClassifier


def verify_onnx_export(checkpoint_path: Path, onnx_path: Path, image_size: int = 224, tolerance: float = 1e-5) -> bool:
    checkpoint_path = Path(checkpoint_path)
    onnx_path = Path(onnx_path)

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    if not onnx_path.exists():
        raise FileNotFoundError(f"ONNX file not found: {onnx_path}")

    torch.manual_seed(0)
    dummy = torch.randn(1, 3, image_size, image_size)

    model = FogClassifier(num_classes=len(CLASS_NAMES), pretrained=False)
    model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
    model.eval()
    with torch.no_grad():
        pt_out = model(dummy).numpy()

    session = ort.InferenceSession(
        str(onnx_path),
        providers=["CPUExecutionProvider"],
    )
    ort_out = session.run(None, {session.get_inputs()[0].name: dummy.numpy()})[0]

    max_diff = float(np.max(np.abs(pt_out - ort_out)))
    passed = max_diff < tolerance

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] max absolute diff = {max_diff:.2e} (tolerance {tolerance:.2e})")
    return passed


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--onnx", type=Path, required=True)
    parser.add_argument("--image_size", type=int, default=224)
    parser.add_argument("--tolerance", type=float, default=1e-5)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    ok = verify_onnx_export(args.checkpoint, args.onnx, args.image_size, args.tolerance)
    sys.exit(0 if ok else 1)
