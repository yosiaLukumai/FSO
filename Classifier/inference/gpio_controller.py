from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PowerLevel(int, Enum):
    MIN    = 0  # CLEAR
    MEDIUM = 1  # MEDIUM_FOG
    MAX    = 2  # HEAVY_FOG


_CLASS_TO_POWER: dict[str, PowerLevel] = {
    "CLEAR":      PowerLevel.MIN,
    "MEDIUM_FOG": PowerLevel.MEDIUM,
    "HEAVY_FOG":  PowerLevel.MAX,
}


class GPIOPowerController:
    """2-bit GPIO power controller for FSO transmitter.

    PIN encoding:
        CLEAR      → GPIO17=0, GPIO18=0
        MEDIUM_FOG → GPIO17=0, GPIO18=1
        HEAVY_FOG  → GPIO17=1, GPIO18=0
    """

    GPIO17_PIN = 17
    GPIO18_PIN = 18

    PIN_STATES: dict[PowerLevel, tuple[int, int]] = {
        PowerLevel.MIN:    (0, 0),
        PowerLevel.MEDIUM: (0, 1),
        PowerLevel.MAX:    (1, 0),
    }

    def __init__(self, mock: bool = False) -> None:
        self._mock  = mock
        self._gpio: Optional[Any] = None
        self._current_level: Optional[PowerLevel] = None

        if not self._mock:
            self._init_gpio()

        if self._mock:
            logger.info("GPIOPowerController: MOCK mode (no hardware).")

    def _init_gpio(self) -> None:
        try:
            import RPi.GPIO as GPIO  # type: ignore[import]

            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.GPIO17_PIN, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.GPIO18_PIN, GPIO.OUT, initial=GPIO.LOW)
            self._gpio = GPIO
            logger.info("GPIO17 and GPIO18 configured as OUTPUT.")
        except ImportError:
            logger.warning("RPi.GPIO not found — switching to MOCK mode.")
            self._mock = True

    def _write_pins(self, pin17: int, pin18: int) -> None:
        if self._mock:
            logger.info("MOCK GPIO: GPIO17=%d GPIO18=%d", pin17, pin18)
            return
        gpio = self._gpio
        gpio.output(self.GPIO17_PIN, gpio.HIGH if pin17 else gpio.LOW)
        gpio.output(self.GPIO18_PIN, gpio.HIGH if pin18 else gpio.LOW)

    def set_power_level(self, level: PowerLevel) -> None:
        pin17, pin18 = self.PIN_STATES[level]
        logger.info("Power level: %s (GPIO17=%d, GPIO18=%d)", level.name, pin17, pin18)
        self._write_pins(pin17, pin18)
        self._current_level = level

    def set_from_visibility_class(self, visibility_class: str) -> None:
        cls_upper = visibility_class.upper()
        if cls_upper not in _CLASS_TO_POWER:
            raise ValueError(f"Unknown visibility class: '{visibility_class}'. Valid: {list(_CLASS_TO_POWER)}")
        self.set_power_level(_CLASS_TO_POWER[cls_upper])

    @property
    def current_level(self) -> Optional[PowerLevel]:
        return self._current_level

    def cleanup(self) -> None:
        if self._mock:
            return
        if self._gpio is not None:
            try:
                self._gpio.cleanup()
                logger.info("GPIO cleanup complete.")
            except Exception as exc:
                logger.warning("Error during GPIO cleanup: %s", exc)
            finally:
                self._gpio = None

    def __enter__(self) -> "GPIOPowerController":
        return self

    def __exit__(self, *args: Any) -> None:
        self.cleanup()

    def __repr__(self) -> str:
        return f"GPIOPowerController(mock={self._mock}, current_level={self._current_level})"
