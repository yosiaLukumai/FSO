# FSO Fog Classifier

Adaptive transmitter power control for Free Space Optics (FSO) links using
real-time fog classification fused with live weather data.

A Raspberry Pi camera captures the optical path, a MobileNetV2 ONNX model
classifies visibility, and 2-bit GPIO output selects the transmitter power level —
all in a closed loop.

---

## How It Works

```
  Pi Camera ──▶ Preprocess ──▶ ONNX FogClassifier (MobileNetV2)
                                        │
                                        ▼
  OpenWeatherMap API ──────▶ WeatherFusion (confidence-gated)
                                        │
                              ┌─────────▼──────────┐
                              │  GPIOPowerController│
                              │  CLEAR     → MIN    │
                              │  MED_FOG   → MED    │
                              │  HEAVY_FOG → MAX    │
                              └─────────────────────┘
```

**Fusion logic:**

| Model confidence | Decision |
|---|---|
| ≥ 0.85 | Model only |
| 0.60 – 0.84 | Weighted vote (model + API) |
| < 0.60 | API only |

---

## Hardware

| Component | Spec |
|---|---|
| Compute | Raspberry Pi 4 Model B (4 GB) |
| Camera | Pi Camera Module v2 or HQ Camera |
| OS | Raspberry Pi OS Lite 64-bit, kernel ≥ 6.1 |
| Python | 3.11+ |
| Power | 5 V / 3 A USB-C |

**GPIO wiring:**

| GPIO | Physical Pin | Role |
|---|---|---|
| GPIO17 | Pin 11 | Power bit 1 (MSB) |
| GPIO18 | Pin 12 | Power bit 0 (LSB) |
| GND | Pin 6 | Ground |

---

## Setup

### 1. Install dependencies

```bash
cd Classifier/
pip install -r requirements.txt

# Raspberry Pi only:
pip install picamera2 RPi.GPIO
```

### 2. Get the trained model

Training was done on Kaggle using PyTorch — view the full notebook here: [`fso_fog_classifier.ipynb`](fso_fog_classifier.ipynb).

The model is MobileNetV2 fine-tuned in two phases (frozen backbone → full fine-tune) on RESIDE-SOTS and DAWN fog datasets.

![Training curves](training_curves.png)
*Training & validation loss/accuracy across 20 epochs — Phase A (frozen backbone) then Phase B (full fine-tune).*

To export the trained checkpoint to ONNX:

```bash
python export/export_onnx.py \
    --checkpoint checkpoints/mobilenetv2_fog_best.pt \
    --output     models/fog_classifier.onnx

# Verify numerical equivalence:
python export/verify_onnx.py \
    --checkpoint checkpoints/mobilenetv2_fog_best.pt \
    --onnx       models/fog_classifier.onnx
```

Expected: `PASS — max delta: X.XXe-06 (tolerance: 1.00e-05)`

### 3. Run the pipeline

```bash
# Production (Raspberry Pi)
python pipeline/main.py \
    --model_path models/fog_classifier.onnx \
    --api_key    YOUR_OWM_API_KEY \
    --lat        YOUR_LATITUDE \
    --lon        YOUR_LONGITUDE \
    --interval   15

# Mock mode — no hardware needed, good for testing the loop
python pipeline/main.py --mock --interval 5 --cycles 10
```

### 4. Run tests

```bash
pytest tests/ -v
```

All tests mock hardware (GPIO, camera, API) and run on any machine.

---

## Modules

| Path | Description |
|---|---|
| `fso_fog_classifier.ipynb` | Kaggle training notebook (MobileNetV2, two-phase fine-tuning) |
| `models/classifier.py` | PyTorch FogClassifier definition |
| `export/export_onnx.py` | Export checkpoint → ONNX |
| `export/verify_onnx.py` | Verify ONNX output matches PyTorch |
| `inference/predictor.py` | ONNX Runtime inference wrapper |
| `inference/camera.py` | picamera2 / OpenCV camera abstraction |
| `inference/weather_api.py` | OpenWeatherMap API client |
| `inference/gpio_controller.py` | 2-bit GPIO power controller |
| `pipeline/fusion.py` | Confidence-gated fusion layer |
| `pipeline/main.py` | Main orchestration loop |
| `tests/` | pytest unit tests |

---

## Performance Targets

| Metric | Target |
|---|---|
| Test accuracy | ≥ 90 % |
| Macro F1 | ≥ 0.88 |
| ONNX inference (Pi 4) | < 200 ms / frame |
| Pipeline cycle time | < 5 s (excl. sleep) |
| Memory (Pi 4) | < 512 MB RSS |
