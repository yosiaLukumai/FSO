from __future__ import annotations

import argparse
import logging
import random
import time
from pathlib import Path
from typing import Optional

from inference.gpio_controller import GPIOPowerController
from inference.weather_api import OpenWeatherMapClient, VisibilityClass
from pipeline.fusion import WeatherFusion


def setup_logging(log_file: Optional[Path] = None) -> logging.Logger:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(str(log_file)))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )
    return logging.getLogger("fso.pipeline")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FSO adaptive power control pipeline.")
    parser.add_argument("--mock",       action="store_true", help="Run without hardware (random inputs).")
    parser.add_argument("--model_path", type=Path,  default=Path("models/fog_classifier.onnx"))
    parser.add_argument("--api_key",    type=str,   default="")
    parser.add_argument("--lat",        type=float, default=0.0)
    parser.add_argument("--lon",        type=float, default=0.0)
    parser.add_argument("--cam_width",  type=int,   default=640)
    parser.add_argument("--cam_height", type=int,   default=480)
    parser.add_argument("--interval",   type=float, default=60.0, help="Seconds between cycles.")
    parser.add_argument("--cycles",     type=int,   default=0,    help="Max cycles (0 = infinite).")
    parser.add_argument("--log_file",   type=Path,  default=None)
    return parser.parse_args()


def _mock_frame(width: int = 640, height: int = 480):
    import numpy as np
    return np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)


def _mock_prediction():
    import numpy as np
    from inference.predictor import PredictionResult
    classes = ["CLEAR", "MEDIUM_FOG", "HEAVY_FOG"]
    probs = np.random.dirichlet([1, 1, 1])
    idx = int(np.argmax(probs))
    return PredictionResult(classes[idx], idx, float(probs[idx]), {c: float(probs[i]) for i, c in enumerate(classes)})


def main() -> None:
    args   = parse_args()
    logger = setup_logging(args.log_file)

    logger.info("FSO pipeline starting — mock=%s, model=%s", args.mock, args.model_path)

    if not args.mock:
        if not args.api_key:
            raise ValueError("--api_key required in non-mock mode.")
        if not args.model_path.exists():
            raise FileNotFoundError(f"ONNX model not found: {args.model_path}")

    fusion = WeatherFusion()

    predictor     = None
    weather_client = None
    camera        = None

    if not args.mock:
        from inference.predictor import ONNXPredictor
        from inference.camera import PiCameraCapture
        predictor      = ONNXPredictor(str(args.model_path))
        weather_client = OpenWeatherMapClient(api_key=args.api_key)
        camera         = PiCameraCapture(width=args.cam_width, height=args.cam_height)

    gpio  = GPIOPowerController(mock=args.mock)
    cycle = 0

    try:
        while True:
            cycle += 1
            t0 = time.monotonic()
            logger.info("--- Cycle %d ---", cycle)

            frame        = _mock_frame(args.cam_width, args.cam_height) if args.mock else camera.capture_frame()
            model_result = _mock_prediction()                            if args.mock else predictor.predict(frame)

            logger.info("Model: %s (conf=%.3f)", model_result.class_label, model_result.confidence)

            if args.mock:
                api_result = random.choice(list(VisibilityClass))
            else:
                try:
                    api_result = weather_client.get_visibility_class(lat=args.lat, lon=args.lon)
                except Exception as exc:
                    logger.warning("Weather API error: %s — falling back to model.", exc)
                    api_result = VisibilityClass(model_result.class_label)

            logger.info("API: %s", api_result.value)

            fusion_result = fusion.decide(model_result, api_result)
            logger.info("Fusion: %s (strategy=%s)", fusion_result.final_class, fusion_result.fusion_strategy_used)

            gpio.set_from_visibility_class(fusion_result.final_class)

            elapsed = time.monotonic() - t0
            logger.info("Cycle %d done in %.2fs", cycle, elapsed)

            if args.cycles > 0 and cycle >= args.cycles:
                break

            sleep_for = max(0.0, args.interval - elapsed)
            if sleep_for > 0:
                time.sleep(sleep_for)

    except KeyboardInterrupt:
        logger.info("Interrupted — shutting down.")
    finally:
        gpio.cleanup()
        if camera is not None:
            camera.release()
        logger.info("Pipeline shutdown complete.")


if __name__ == "__main__":
    main()
