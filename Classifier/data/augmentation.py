from __future__ import annotations

import random
from typing import Tuple

import numpy as np
import torchvision.transforms as transforms
from PIL import Image


class SyntheticFogAugment:
    """Adds synthetic fog to an image using the Koschmieder scattering model.

    I(x) = J(x) * t(x) + A * (1 - t(x))
    where t(x) = exp(-beta * depth_map)
    """

    def __init__(
        self,
        beta_range: Tuple[float, float] = (0.5, 2.5),
        A: float = 1.0,
        p: float = 0.3,
    ) -> None:
        if not (0.0 <= p <= 1.0):
            raise ValueError(f"Probability p must be in [0, 1], got {p}.")
        if beta_range[0] < 0 or beta_range[1] < beta_range[0]:
            raise ValueError(f"beta_range must satisfy 0 <= min <= max, got {beta_range}.")
        self.beta_range = beta_range
        self.A = float(A)
        self.p = p

    def __call__(self, img: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return img

        img_np = np.array(img, dtype=np.float32) / 255.0

        luminance = (
            0.299 * img_np[:, :, 0]
            + 0.587 * img_np[:, :, 1]
            + 0.114 * img_np[:, :, 2]
        )

        lum_min, lum_max = luminance.min(), luminance.max()
        if lum_max - lum_min > 1e-6:
            lum_norm = (luminance - lum_min) / (lum_max - lum_min)
        else:
            lum_norm = luminance.copy()

        depth_map = 1.0 - lum_norm

        beta = random.uniform(self.beta_range[0], self.beta_range[1])
        transmission = np.exp(-beta * depth_map)
        t = transmission[:, :, np.newaxis]

        fogged = img_np * t + self.A * (1.0 - t)
        fogged = np.clip(fogged, 0.0, 1.0)

        return Image.fromarray((fogged * 255).astype(np.uint8))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(beta_range={self.beta_range}, A={self.A}, p={self.p})"


def get_train_transforms(image_size: int = 224) -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(image_size),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        transforms.RandomRotation(15),
        SyntheticFogAugment(p=0.3),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_val_transforms(image_size: int = 224) -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
