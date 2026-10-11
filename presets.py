# presets.py - Preset mathematical functions
import numpy as np
from typing import Dict, Any

def mandelbrot_func(x, y, rng=None, params=None):
    c = (x + 1j * y) * params["zoom"] + complex(params["center_x"], params["center_y"])
    z, img = np.zeros_like(c, dtype=complex), np.zeros(c.shape, dtype=np.float64)
    for _ in range(int(params["max_iter"])):
        mask = np.abs(z) <= 2; z[mask] = z[mask]**2 + c[mask]; img[mask] += 1
    return np.clip((img / int(params["max_iter"])) * 2 - 1, -1, 1) * params["amplitude"]

def julia_func(x, y, rng=None, params=None):
    c = complex(params["c_real"], params["c_imag"]); z = (x + 1j * y) * params["zoom"]; img = np.zeros(z.shape, dtype=np.float64)
    for _ in range(int(params["max_iter"])):
        mask = np.abs(z) <= 2; z[mask] = z[mask]**2 + c; img[mask] += 1
    return np.clip((img / int(params["max_iter"])) * 2 - 1, -1, 1) * params["amplitude"]

def burning_ship_func(x, y, rng=None, params=None):
    c = (x + 1j * y) * params["zoom"] + complex(params["center_x"], params["center_y"])
    z, img = np.zeros_like(c, dtype=complex), np.zeros(c.shape, dtype=np.float64)
    for _ in range(int(params["max_iter"])):
        mask = np.abs(z) <= 2; z[mask] = (np.abs(z[mask].real) + 1j * np.abs(z[mask].imag))**2 + c[mask]; img[mask] += 1
    return np.clip((img / int(params["max_iter"])) * 2 - 1, -1, 1) * params["amplitude"]

def interference_func(x, y, rng=None, params=None):
    res = np.zeros_like(x)
    for i in range(int(params["num_sources"])):
        a = 2 * np.pi * i / int(params["num_sources"]) + params["angle_offset"]
        sx, sy = params["radius"] * np.cos(a), params["radius"] * np.sin(a)
        res += np.sin(np.sqrt((x - sx)**2 + (y - sy)**2) * params["frequency"] + params["phase"])
    return res / int(params["num_sources"]) * params["amplitude"]

def spiral_func(x, y, rng=None, params=None):
    r = np.sqrt(x**2 + y**2) + 0.001
    return np.sin(np.arctan2(y, x) * params["arms"] + r * params["frequency"] + params["phase"]) * params["amplitude"] * np.exp(-r * params["decay"])

def diamond_func(x, y, rng=None, params=None):
    return np.sin((x + y) * params["frequency"] + params["phase"]) * np.cos((x - y) * params["frequency"] * params["ratio"] + params["phase2"]) * params["amplitude"]

def moire_func(x, y, rng=None, params=None):
    g1 = np.sin(x * params["freq1"]) * np.sin(y * params["freq1"])
    g2 = np.sin((x + params["offset_x"]) * params["freq2"]) * np.sin((y + params["offset_y"]) * params["freq2"])
    return (g1 + g2) * params["amplitude"] / 2

def wave_interference_func(x, y, rng=None, params=None):
    w1 = np.sin(params["frequency"] * (x * np.cos(params["angle1"]) + y * np.sin(params["angle1"])) + params["phase1"])
    w2 = np.sin(params["frequency"] * (x * np.cos(params["angle2"]) + y * np.sin(params["angle2"])) + params["phase2"])
    return (w1 + w2) * params["amplitude"] / 2

def ripple_func(x, y, rng=None, params=None):
    res, n = np.zeros_like(x), int(params["sources"])
    for i in range(n):
        ox, oy = params["spread"] * np.cos(2 * np.pi * i / n), params["spread"] * np.sin(2 * np.pi * i / n)
        r = np.sqrt((x - ox)**2 + (y - oy)**2)
        res += np.sin(r * params["frequency"] - params["speed"] * 5) / (1 + r * params["damping"])
    return res * params["amplitude"]

def checkerboard_func(x, y, rng=None, params=None):
    return np.tanh(np.sin(x * params["freq_x"]) * params["sharpness"]) * np.tanh(np.sin(y * params["freq_y"]) * params["sharpness"]) * params["amplitude"]

def voronoi_approx_func(x, y, rng=None, params=None):
    min_d = np.ones_like(x) * 100; np.random.seed(42)
    for _ in range(int(params["num_cells"])):
        px, py = np.random.uniform(-params["scale"], params["scale"]), np.random.uniform(-params["scale"], params["scale"])
        min_d = np.minimum(min_d, np.sqrt((x - px)**2 + (y - py)**2))
    return np.clip(1.0 - min_d * params["frequency"], -1, 1) * params["amplitude"]

def perlin_approx_func(x, y, rng=None, params=None):
    res, freq, amp = np.zeros_like(x), params["frequency"], 1.0
    for _ in range(int(params["octaves"])):
        res += amp * np.sin(x * freq) * np.cos(y * freq) + amp * 0.5 * np.sin((x + y) * freq * 0.7)
        freq *= 2.0; amp *= params["persistence"]
    return res / (1 + params["persistence"]) * params["amplitude"]

def domain_warp_func(x, y, rng=None, params=None):
    wx = np.sin(y * params["freq1"] + params["phase1"]) * params["strength"]
    wy = np.cos(x * params["freq2"] + params["phase2"]) * params["strength"]
    return np.sin((x + wx) * params["freq3"]) * np.cos((y + wy) * params["freq3"]) * params["amplitude"]

def cardioid_func(x, y, rng=None, params=None):
    r = np.sqrt(x**2 + y**2) + 0.001; theta = np.arctan2(y, x)
    dfc = np.abs(r - (np.cos(theta) - np.cos(2 * theta)) * params["scale"])
    return np.sin(dfc * params["frequency"]) * params["amplitude"] * np.exp(-dfc * params["decay"])

FUNCTION_MAP: Dict[str, Dict[str, Any]] = {
    "Sine Wave": {"func": lambda x, y, rng=None, params=None: np.sin(x * params["frequency"] + params["phase"]) * params["amplitude"], "desc": "Simple sine wave along X-axis", "params": {"frequency": (1, 50, 10), "amplitude": (0.1, 2.0, 1.0), "phase": (0, 6.28, 0.0)}},
    "Radial Wave": {"func": lambda x, y, rng=None, params=None: np.sin(np.sqrt(x**2 + y**2) * params["frequency"] + params["phase"]) * params["amplitude"], "desc": "Concentric radial waves from center", "params": {"frequency": (1, 50, 10), "amplitude": (0.1, 2.0, 1.0), "phase": (0, 6.28, 0.0)}},
    "Plasma": {"func": lambda x, y, rng=None, params=None: (np.sin(x * params["freq1"] + params["phase1"]) + np.sin(y * params["freq2"] + params["phase2"]) + np.sin((x + y) * params["freq3"] + params["phase3"])) * params["amplitude"] / 3.0, "desc": "Classic procedural plasma effect", "params": {"freq1": (1, 50, 5), "freq2": (1, 50, 10), "freq3": (1, 50, 15), "phase1": (0, 6.28, 0.0), "phase2": (0, 6.28, 0.0), "phase3": (0, 6.28, 0.0), "amplitude": (0.1, 2.0, 1.0)}},
    "Fractal (Mandelbrot)": {"func": mandelbrot_func, "desc": "True iterative Mandelbrot fractal set", "params": {"max_iter": (5, 150, 30), "zoom": (0.5, 5.0, 1.5), "center_x": (-2.0, 2.0, -0.5), "center_y": (-2.0, 2.0, 0.0), "amplitude": (0.1, 2.0, 1.0)}},
    "Fractal (Julia)": {"func": julia_func, "desc": "Julia set fractal with adjustable C parameter", "params": {"max_iter": (5, 150, 30), "zoom": (0.5, 3.0, 1.0), "c_real": (-2.0, 2.0, -0.7), "c_imag": (-2.0, 2.0, 0.27), "amplitude": (0.1, 2.0, 1.0)}},
    "Fractal (Burning Ship)": {"func": burning_ship_func, "desc": "Burning Ship fractal variant", "params": {"max_iter": (5, 150, 30), "zoom": (0.5, 5.0, 1.5), "center_x": (-2.0, 2.0, -0.4), "center_y": (-2.0, 2.0, -0.5), "amplitude": (0.1, 2.0, 1.0)}},
    "Interference": {"func": interference_func, "desc": "Multi-source wave interference pattern", "params": {"num_sources": (2, 8, 3), "frequency": (5, 100, 30), "radius": (0.1, 2.0, 0.5), "amplitude": (0.1, 2.0, 1.0), "phase": (0, 6.28, 0.0), "angle_offset": (0, 6.28, 0.0)}},
    "Spiral": {"func": spiral_func, "desc": "Logarithmic spiral with adjustable arms", "params": {"arms": (1, 10, 3), "frequency": (5, 50, 15), "amplitude": (0.1, 2.0, 1.0), "phase": (0, 6.28, 0.0), "decay": (0.0, 5.0, 0.5)}},
    "Diamond Wave": {"func": diamond_func, "desc": "Rotated diamond/checkerboard pattern", "params": {"frequency": (1, 30, 8), "ratio": (0.1, 3.0, 1.0), "amplitude": (0.1, 2.0, 1.0), "phase": (0, 6.28, 0.0), "phase2": (0, 6.28, 0.0)}},
    "Moiré Pattern": {"func": moire_func, "desc": "Overlapping grid interference effect", "params": {"freq1": (5, 50, 20), "freq2": (5, 50, 21), "offset_x": (-1.0, 1.0, 0.1), "offset_y": (-1.0, 1.0, 0.1), "amplitude": (0.1, 2.0, 1.0)}},
    "Plane Wave": {"func": wave_interference_func, "desc": "Two crossing plane waves", "params": {"frequency": (5, 80, 20), "angle1": (0, 6.28, 0.0), "angle2": (0, 6.28, 1.57), "amplitude": (0.1, 2.0, 1.0), "phase1": (0, 6.28, 0.0), "phase2": (0, 6.28, 0.0)}},
    "Water Ripple": {"func": ripple_func, "desc": "Multiple water ripple sources with damping", "params": {"sources": (1, 6, 2), "frequency": (10, 80, 30), "spread": (0.2, 1.5, 0.5), "speed": (0.1, 3.0, 1.0), "damping": (0.1, 5.0, 1.0), "amplitude": (0.1, 2.0, 1.0)}},
    "Smooth Checker": {"func": checkerboard_func, "desc": "Smooth-edged checkerboard with tanh transitions", "params": {"freq_x": (1, 20, 4), "freq_y": (1, 20, 4), "sharpness": (1, 20, 5), "amplitude": (0.1, 2.0, 1.0)}},
    "Voronoi Approx": {"func": voronoi_approx_func, "desc": "Distance-field Voronoi cell approximation", "params": {"num_cells": (5, 50, 15), "scale": (0.5, 3.0, 1.5), "frequency": (1, 10, 3), "amplitude": (0.1, 2.0, 1.0)}},
    "Perlin-like Noise": {"func": perlin_approx_func, "desc": "Sine-based pseudo-Perlin noise with octaves", "params": {"frequency": (1, 30, 5), "octaves": (1, 6, 3), "persistence": (0.1, 0.9, 0.5), "amplitude": (0.1, 2.0, 1.0)}},
    "Domain Warp": {"func": domain_warp_func, "desc": "Domain warping distortion effect", "params": {"freq1": (1, 30, 5), "freq2": (1, 30, 5), "freq3": (1, 30, 10), "strength": (0.0, 1.0, 0.3), "amplitude": (0.1, 2.0, 1.0), "phase1": (0, 6.28, 0.0), "phase2": (0, 6.28, 0.0)}},
    "Cardioid": {"func": cardioid_func, "desc": "Cardioid curve pattern with decay", "params": {"frequency": (5, 50, 15), "scale": (0.1, 2.0, 0.5), "decay": (0.0, 5.0, 0.5), "amplitude": (0.1, 2.0, 1.0)}},
}