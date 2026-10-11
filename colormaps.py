# colormaps.py - Colormap application functions
import numpy as np
from typing import Optional

def apply_colormap(img_array: np.ndarray, colormap_name: Optional[str]) -> np.ndarray:
    if not colormap_name or colormap_name == "None (RGB)": return img_array
    img = img_array.astype(np.float32) / 255.0; gray = np.mean(img, axis=2)
    cmap_effects = {
        "grayscale": np.stack([gray, gray, gray], axis=2),
        "sepia": np.stack([img[:,:,0]*0.393 + img[:,:,1]*0.769 + img[:,:,2]*0.189, img[:,:,0]*0.349 + img[:,:,1]*0.686 + img[:,:,2]*0.168, img[:,:,0]*0.272 + img[:,:,1]*0.534 + img[:,:,2]*0.131], axis=2),
        "thermal": np.stack([np.clip(gray * 3, 0, 1), np.clip(gray * 3 - 1, 0, 1), np.clip(gray * 3 - 2, 0, 1)], axis=2),
        "ocean": np.stack([np.clip(gray * 0.2, 0, 1), np.clip(gray * 0.5 + 0.2, 0, 1), np.clip(gray * 0.8 + 0.2, 0, 1)], axis=2),
        "neon": np.stack([np.clip(img[:,:,0] * 1.5, 0, 1), np.clip(img[:,:,1] * 0.5 + 0.5, 0, 1), np.clip(img[:,:,2] * 1.5, 0, 1)], axis=2),
        "inverted": 1.0 - img,
        "vintage": np.stack([img[:,:,0] * 0.6 + 0.2, img[:,:,1] * 0.5 + 0.15, img[:,:,2] * 0.4 + 0.1], axis=2),
        "cyberpunk": np.stack([np.clip(img[:,:,0] * 1.5 + img[:,:,2] * 0.3, 0, 1), img[:,:,1] * 0.3, np.clip(img[:,:,2] * 1.8 + img[:,:,0] * 0.2, 0, 1)], axis=2),
        "sunset": np.stack([np.clip(gray * 1.2 + 0.2, 0, 1), np.clip(gray * 0.6 + img[:,:,1] * 0.4, 0, 1), np.clip(img[:,:,2] * 0.8 + gray * 0.2, 0, 1)], axis=2),
        "forest": np.stack([np.clip(img[:,:,0] * 0.5 + gray * 0.2, 0, 1), np.clip(img[:,:,1] * 1.2 + gray * 0.1, 0, 1), np.clip(img[:,:,2] * 0.4 + gray * 0.1, 0, 1)], axis=2),
        "ice": np.stack([np.clip(img[:,:,0] * 0.7 + gray * 0.3 + 0.1, 0, 1), np.clip(img[:,:,1] * 0.8 + gray * 0.2 + 0.15, 0, 1), np.clip(img[:,:,2] * 1.2 + gray * 0.2 + 0.2, 0, 1)], axis=2),
    }
    return np.clip(cmap_effects.get(colormap_name, img) * 255, 0, 255).astype(np.uint8)

def apply_brightness(img_array: np.ndarray, brightness: float) -> np.ndarray: return np.clip(img_array * brightness, 0, 255)
def apply_contrast(img_array: np.ndarray, contrast: float) -> np.ndarray: return (img_array - 128) * contrast + 128 if contrast != 1.0 else img_array
def apply_saturation(img_array: np.ndarray, saturation: float) -> np.ndarray: 
    if saturation == 1.0: return img_array
    gray = np.mean(img_array, axis=2, keepdims=True); return gray + (img_array - gray) * saturation
def apply_gamma(img_array: np.ndarray, gamma: float) -> np.ndarray: return np.power(img_array / 255.0, 1.0 / gamma) * 255.0 if gamma != 1.0 else img_array