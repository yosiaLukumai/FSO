from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class PiCameraCapture:
    """Camera interface — prefers picamera2 on Pi, falls back to OpenCV."""

    def __init__(self, width: int = 640, height: int = 480, use_picamera: bool = True, camera_index: int = 0) -> None:
        self.width  = width
        self.height = height
        self._use_picamera  = use_picamera
        self._camera_index  = camera_index
        self._picam: Optional[Any] = None
        self._cv2_cap: Optional[Any] = None
        self._backend = ""
        self._init_camera()

    def _init_camera(self) -> None:
        if self._use_picamera:
            try:
                self._init_picamera2()
                self._backend = "picamera2"
                return
            except Exception as exc:
                logger.warning("picamera2 unavailable (%s), falling back to OpenCV.", exc)

        self._init_opencv()
        self._backend = "opencv"

    def _init_picamera2(self) -> None:
        from picamera2 import Picamera2  # type: ignore[import]

        self._picam = Picamera2()
        config = self._picam.create_preview_configuration(main={"size": (self.width, self.height), "format": "RGB888"})
        self._picam.configure(config)
        self._picam.start()
        logger.info("picamera2 opened: %dx%d", self.width, self.height)

    def _init_opencv(self) -> None:
        try:
            import cv2  # type: ignore[import]
        except ImportError as exc:
            raise ImportError("Neither picamera2 nor OpenCV is available.") from exc

        cap = cv2.VideoCapture(self._camera_index)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera device {self._camera_index}.")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._cv2_cap = cap
        logger.info("OpenCV VideoCapture opened: device=%d %dx%d", self._camera_index, self.width, self.height)

    def capture_frame(self) -> np.ndarray:
        if self._backend == "picamera2" and self._picam is not None:
            frame_rgb = self._picam.capture_array("main")
            return frame_rgb[:, :, ::-1].copy().astype(np.uint8)

        if self._backend == "opencv" and self._cv2_cap is not None:
            import cv2  # type: ignore[import]
            ret, frame = self._cv2_cap.read()
            if not ret or frame is None:
                raise RuntimeError("Failed to read frame from OpenCV VideoCapture.")
            return frame

        raise RuntimeError("Camera not initialised.")

    def release(self) -> None:
        if self._picam is not None:
            try:
                self._picam.stop()
                self._picam.close()
            except Exception as exc:
                logger.warning("Error releasing picamera2: %s", exc)
            finally:
                self._picam = None

        if self._cv2_cap is not None:
            try:
                self._cv2_cap.release()
            except Exception as exc:
                logger.warning("Error releasing OpenCV cap: %s", exc)
            finally:
                self._cv2_cap = None

    def __enter__(self) -> "PiCameraCapture":
        return self

    def __exit__(self, *args: Any) -> None:
        self.release()

    def __repr__(self) -> str:
        return f"PiCameraCapture(backend={self._backend!r}, {self.width}x{self.height})"
