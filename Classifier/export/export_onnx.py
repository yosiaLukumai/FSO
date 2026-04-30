from __future__ import annotations

import argparse
import logging
from pathlib import Path

import torch

from models.classifier import CLASS_NAMES, FogClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


def export_to_onnx(checkpoint_path: Path, output_path: Path, image_size: int = 224, opset_version: int = 12) -> None:
    checkpoint_path = Path(checkpoint_path)
    output_path = Path(output_path)

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Loading checkpoint from %s", checkpoint_path)
    model = FogClassifier(num_classes=len(CLASS_NAMES), pretrained=False)
    model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
    model.eval()

    dummy_input = torch.randn(1, 3, image_size, image_size)

    logger.info("Exporting to ONNX (opset=%d) → %s", opset_version, output_path)
    with torch.no_grad():
        torch.onnx.export(
            model,
            dummy_input,
            str(output_path),
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=["image"],
            output_names=["logits"],
            dynamic_axes={"image": {0: "batch_size"}, "logits": {0: "batch_size"}},
            dynamo=False,
            verbose=False,
        )

    size_mb = output_path.stat().st_size / (1024 ** 2)
    logger.info("Done: %s (%.2f MB)", output_path, size_mb)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image_size", type=int, default=224)
    parser.add_argument("--opset", type=int, default=12, dest="opset_version")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    export_to_onnx(args.checkpoint, args.output, args.image_size, args.opset_version)
