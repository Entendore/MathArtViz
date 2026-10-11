# generators.py - Image generation math pipeline
import numpy as np
from math_engine import math_engine
from colormaps import apply_colormap, apply_brightness, apply_contrast, apply_saturation, apply_gamma
from config import MIN_RESOLUTION


def generate_presets(xv, yv, function_map, channel_funcs, sliders):
    channels = []
    for ch, func_name in channel_funcs.items():
        if func_name not in function_map:
            channels.append(np.zeros(xv.shape, dtype=np.uint8))
            continue
        func = function_map[func_name]
        params = {
            key.split('_', 1)[1]: slider.value()
            for key, slider in sliders.items()
            if key.startswith(f"{ch}_")
        }
        result = func(xv, yv, None, params)
        channels.append(np.clip((result + 1) * 127.5, 0, 255).astype(np.uint8))
    return np.stack(channels, axis=2)


def generate_custom(xv, yv, formulas, user_vars, time_value):
    channels = []
    for ch, expr in formulas.items():
        if not expr.strip():
            channels.append(np.zeros(xv.shape, dtype=np.uint8))
        else:
            channels.append(
                np.clip(
                    (math_engine.evaluate(expr, xv, yv, user_vars, time_value) + 1) * 127.5,
                    0, 255
                ).astype(np.uint8)
            )
    return np.stack(channels, axis=2)


def apply_post_processing(img_array, brightness, contrast, saturation, gamma, colormap_name):
    img_float = apply_brightness(img_array.astype(np.float32), brightness)
    img_float = apply_contrast(img_float, contrast)
    img_float = apply_saturation(img_float, saturation)
    img_float = apply_gamma(img_float, gamma)
    return apply_colormap(np.clip(img_float, 0, 255).astype(np.uint8), colormap_name)


def _build_grid(app_instance, width, height):
    """Build x/y meshgrid from app settings."""
    scale = app_instance.settings_panel.scale_spin.value()
    xv, yv = np.meshgrid(
        np.linspace(-1, 1, width) * scale,
        np.linspace(-1, 1, height) * scale
    )
    return xv, yv


def _get_source_config(app_instance):
    """Extract channel config from current tab."""
    is_custom = app_instance.tabs.currentIndex() == 1
    if is_custom:
        return "custom", {
            "formulas": {
                "R": app_instance.custom_tab.r_text.toPlainText(),
                "G": app_instance.custom_tab.g_text.toPlainText(),
                "B": app_instance.custom_tab.b_text.toPlainText(),
            },
            "user_vars": {n: s.value() for n, s in app_instance.custom_tab.sliders.items()},
        }
    else:
        return "presets", {
            "funcs": app_instance.presets_tab.channel_selector.currentFunctions(),
            "sliders": app_instance.presets_tab.sliders,
        }


def generate_frame(app_instance, width, height, time_value):
    """Generate a single frame at the given resolution and time.
    Used by both live preview and GIF export.
    """
    xv, yv = _build_grid(app_instance, width, height)
    source_type, config = _get_source_config(app_instance)

    if source_type == "custom":
        img = generate_custom(
            xv, yv, config["formulas"],
            config["user_vars"], time_value
        )
    else:
        img = generate_presets(
            xv, yv, app_instance.function_map,
            config["funcs"], config["sliders"]
        )

    pp = app_instance.postprocess_panel
    return apply_post_processing(
        img,
        pp.brightness_slider.value(), pp.contrast_slider.value(),
        pp.saturation_slider.value(), pp.gamma_slider.value(),
        pp.colormap_combo.currentText()
    )


def generate_full_resolution(app_instance):
    """Generate at full configured resolution (for save)."""
    w = app_instance.settings_panel.width_spin.value()
    h = app_instance.settings_panel.height_spin.value()
    return generate_frame(app_instance, w, h, app_instance.time_value)