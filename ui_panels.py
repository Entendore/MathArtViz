# ui_panels.py - Panel and tab builder classes

from typing import Dict, TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QPlainTextEdit
)
from PySide6.QtCore import Qt

from config import (
    RESOLUTION_PRESETS, MIN_RESOLUTION, MAX_RESOLUTION,
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_SCALE, MIN_SCALE, MAX_SCALE,
    DEFAULT_SPEED_MS, MIN_SPEED_MS, MAX_SPEED_MS, TIME_STEP, SHORTCUTS
)
from presets import FUNCTION_MAP, FORMULA_PRESETS, COLORMAPS
from ui_components import LabeledSlider, ImageButton, ChannelSelector, create_time_label

if TYPE_CHECKING:
    from app import MathArtApp


class PresetsTab(QWidget):
    """Presets selection and parameter adjustment tab."""
    
    def __init__(self, app: 'MathArtApp', parent=None):
        super().__init__(parent)
        self.app = app
        self.sliders: Dict[str, LabeledSlider] = {}
        
        layout = QVBoxLayout(self)
        
        # Channel selector
        rgb_group = QGroupBox("RGB Channels")
        rgb_layout = QVBoxLayout()
        self.channel_selector = ChannelSelector(app.function_names)
        self.channel_selector.selectionChanged.connect(self.update_sliders)
        rgb_layout.addWidget(self.channel_selector)
        rgb_group.setLayout(rgb_layout)
        layout.addWidget(rgb_group)
        
        # Parameter sliders
        self.slider_group = QGroupBox("Parameters")
        self.slider_layout = QVBoxLayout()
        self.slider_layout.setSpacing(4)
        self.slider_group.setLayout(self.slider_layout)
        layout.addWidget(self.slider_group)
        
        # Description label
        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #888; font-style: italic; padding: 5px;")
        layout.addWidget(self.desc_label)
    
    def update_sliders(self):
        """Update parameter sliders based on selected functions."""
        while self.slider_layout.count():
            item = self.slider_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        
        self.sliders.clear()
        descriptions = []
        
        for channel, combo in self.channel_selector.combos.items():
            func_name = combo.currentText()
            if func_name not in self.app.function_params:
                continue
            params = self.app.function_params[func_name]
            desc = FUNCTION_MAP[func_name]["desc"]
            descriptions.append(f"{channel}: {desc}")
            
            header = QLabel(f"<b>-- {channel} Channel: {func_name} --</b>")
            self.slider_layout.addWidget(header)
            
            for name, (minv, maxv, default) in params.items():
                slider = LabeledSlider(name, minv, maxv, default)
                slider.valueChanged.connect(lambda v, ch=channel: self.app._debounced_generate())
                self.slider_layout.addWidget(slider)
                self.sliders[f"{channel}_{name}"] = slider
        
        self.desc_label.setText("<br>".join(descriptions))
        self.slider_layout.addStretch()
    
    def randomize(self):
        """Randomize all channel selections and sliders."""
        import random
        self.channel_selector.randomize()
        for slider in self.sliders.values():
            slider.setValue(random.uniform(slider.min_val, slider.max_val))


class CustomTab(QWidget):
    """Custom math expression editing tab."""
    
    def __init__(self, app: 'MathArtApp', parent=None):
        super().__init__(parent)
        self.app = app
        self.sliders: Dict[str, LabeledSlider] = {}
        
        layout = QVBoxLayout(self)
        
        # Preset selector
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Formula Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- Custom --")
        for name in FORMULA_PRESETS:
            self.preset_combo.addItem(name)
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        preset_layout.addWidget(self.preset_combo, 1)
        layout.addLayout(preset_layout)
        
        # Formula text editors
        self.r_text = QPlainTextEdit("sin(x*10*a + t)")
        self.g_text = QPlainTextEdit("cos(y*10*b + t)")
        self.b_text = QPlainTextEdit("sin(sqrt(x**2 + y**2)*15*c - t)")
        
        channel_configs = [
            ("Red Channel (R)", self.r_text, "#ff6666", "R"),
            ("Green Channel (G)", self.g_text, "#66ff66", "G"),
            ("Blue Channel (B)", self.b_text, "#6666ff", "B")
        ]
        
        for name, text_edit, color, ch in channel_configs:
            grp = QGroupBox(name)
            grp.setStyleSheet(f"QGroupBox {{ border-color: {color}; }}")
            grp_layout = QVBoxLayout()
            
            btn_layout = QHBoxLayout()
            validate_btn = QPushButton("✓ Validate")
            validate_btn.setObjectName("validate_btn")
            validate_btn.setMaximumWidth(80)
            validate_btn.clicked.connect(
                lambda checked, te=text_edit, c=ch: self.app._validate_channel(te, c)
            )
            btn_layout.addStretch()
            btn_layout.addWidget(validate_btn)
            grp_layout.addLayout(btn_layout)
            
            grp_layout.addWidget(text_edit)
            text_edit.setMaximumHeight(65)
            grp.setLayout(grp_layout)
            layout.addWidget(grp)
        
        # User variables
        var_group = QGroupBox("User Variables (a, b, c, d)")
        var_layout = QVBoxLayout()
        var_layout.setSpacing(4)
        
        for var, default in {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}.items():
            slider = LabeledSlider(var, -5.0, 5.0, default)
            slider.valueChanged.connect(lambda v: self.app._debounced_generate())
            var_layout.addWidget(slider)
            self.sliders[var] = slider
        
        var_group.setLayout(var_layout)
        layout.addWidget(var_group)
        
        # Help section
        help_grp = QGroupBox("Available Functions & Variables")
        help_layout = QVBoxLayout()
        help_text = """
<b>Trigonometric:</b> sin, cos, tan, arcsin, arccos, arctan, arctan2, sinh, cosh, tanh<br>
<b>Exponential/Log:</b> exp, exp2, log, log2, log10, log1p, expm1<br>
<b>Powers:</b> sqrt, square, power, pow, cbrt<br>
<b>SciPy Special:</b> erf, erfc, gamma, gammaln, beta, betaln<br>
<b>Other:</b> abs, sign, floor, ceil, round, clip, where<br><br>
<b>Variables:</b> x, y, r (radius), theta (angle), t (time)<br>
<b>User vars:</b> a, b, c, d (adjustable with sliders)<br>
<b>Constants:</b> pi, e, tau, phi, TWO_PI, HALF_PI, SQRT2
"""
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("font-size: 11px; padding: 5px;")
        help_layout.addWidget(help_label)
        help_grp.setLayout(help_layout)
        layout.addWidget(help_grp)
    
    def load_preset(self, text: str):
        """Load a formula preset."""
        if text == "-- Custom --":
            return
        
        if text in FORMULA_PRESETS:
            preset = FORMULA_PRESETS[text]
            self.r_text.setPlainText(preset["R"])
            self.g_text.setPlainText(preset["G"])
            self.b_text.setPlainText(preset["B"])
            
            if "vars" in preset:
                for var_name, value in preset["vars"].items():
                    if var_name in self.sliders:
                        self.sliders[var_name].setValue(value)
            
            self.app.generate_image()
    
    def randomize(self):
        """Randomize user variable sliders."""
        import random
        for slider in self.sliders.values():
            slider.setValue(random.uniform(slider.min_val, slider.max_val))


class SettingsPanel(QGroupBox):
    """General settings panel."""
    
    def __init__(self, parent=None):
        super().__init__("General Settings", parent)
        layout = QGridLayout()
        
        # Resolution preset
        layout.addWidget(QLabel("Resolution:"), 0, 0)
        self.resolution_combo = QComboBox()
        for name in RESOLUTION_PRESETS:
            self.resolution_combo.addItem(name)
        self.resolution_combo.setCurrentText("SD (512x512)")
        self.resolution_combo.currentTextChanged.connect(self._on_preset_changed)
        layout.addWidget(self.resolution_combo, 0, 1)
        
        # Width/Height
        self.width_spin = QSpinBox()
        self.width_spin.setRange(MIN_RESOLUTION, MAX_RESOLUTION)
        self.width_spin.setValue(DEFAULT_WIDTH)
        self.width_spin.valueChanged.connect(self._on_resolution_changed)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(MIN_RESOLUTION, MAX_RESOLUTION)
        self.height_spin.setValue(DEFAULT_HEIGHT)
        self.height_spin.valueChanged.connect(self._on_resolution_changed)
        
        layout.addWidget(QLabel("Width:"), 1, 0)
        layout.addWidget(self.width_spin, 1, 1)
        layout.addWidget(QLabel("Height:"), 2, 0)
        layout.addWidget(self.height_spin, 2, 1)
        
        # Scale
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(MIN_SCALE, MAX_SCALE)
        self.scale_spin.setValue(DEFAULT_SCALE)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setDecimals(2)
        
        layout.addWidget(QLabel("Scale:"), 3, 0)
        layout.addWidget(self.scale_spin, 3, 1)
        
        # Preview resolution option
        self.preview_check = QCheckBox("Use preview resolution during editing")
        self.preview_check.setToolTip("Use half resolution for faster feedback while adjusting sliders")
        self.preview_check.setChecked(True)
        layout.addWidget(self.preview_check, 4, 0, 1, 2)
        
        self.setLayout(layout)
    
    def _on_preset_changed(self, text: str):
        """Handle resolution preset selection."""
        if text in RESOLUTION_PRESETS and RESOLUTION_PRESETS[text] is not None:
            w, h = RESOLUTION_PRESETS[text]
            self.width_spin.setValue(w)
            self.height_spin.setValue(h)
    
    def _on_resolution_changed(self):
        """Handle manual resolution change."""
        w, h = self.width_spin.value(), self.height_spin.value()
        for name, size in RESOLUTION_PRESETS.items():
            if size == (w, h):
                self.resolution_combo.blockSignals(True)
                self.resolution_combo.setCurrentText(name)
                self.resolution_combo.blockSignals(False)
                return
        self.resolution_combo.blockSignals(True)
        self.resolution_combo.setCurrentText("Custom")
        self.resolution_combo.blockSignals(False)


class AnimationPanel(QGroupBox):
    """Animation controls panel."""
    
    def __init__(self, parent=None):
        super().__init__("Animation", parent)
        layout = QVBoxLayout()
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.animate_btn = QPushButton("▶ Animate")
        self.animate_btn.setCheckable(True)
        self.animate_btn.setToolTip(f"Toggle animation ({SHORTCUTS['animate_toggle']})")
        
        self.step_btn = QPushButton("⏭ Step")
        self.step_btn.setObjectName("step_btn")
        self.step_btn.setToolTip(f"Step forward ({SHORTCUTS['step']})")
        
        self.reset_time_btn = QPushButton("⏮ Reset")
        self.reset_time_btn.setObjectName("reset_btn")
        self.reset_time_btn.setToolTip(f"Reset time ({SHORTCUTS['reset_time']})")
        
        btn_layout.addWidget(self.animate_btn)
        btn_layout.addWidget(self.step_btn)
        btn_layout.addWidget(self.reset_time_btn)
        layout.addLayout(btn_layout)
        
        # Speed slider
        self.speed_slider = LabeledSlider("Speed", MIN_SPEED_MS, MAX_SPEED_MS, DEFAULT_SPEED_MS)
        self.speed_slider.precision = 0
        self.speed_slider.label.setText(f"Speed: {DEFAULT_SPEED_MS}ms")
        layout.addWidget(self.speed_slider)
        
        # Time step
        self.timestep_slider = LabeledSlider("Time Step", 0.001, 0.5, TIME_STEP)
        layout.addWidget(self.timestep_slider)
        
        # Time display
        self.time_label = create_time_label()
        layout.addWidget(self.time_label)
        
        self.setLayout(layout)


class PostProcessPanel(QGroupBox):
    """Post-processing controls panel."""
    
    def __init__(self, app: 'MathArtApp', parent=None):
        super().__init__("Post-Processing", parent)
        self.app = app
        layout = QGridLayout()
        
        # Colormap
        layout.addWidget(QLabel("Color Map:"), 0, 0)
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(COLORMAPS.keys())
        layout.addWidget(self.colormap_combo, 0, 1)
        
        # Sliders
        self.brightness_slider = LabeledSlider("Brightness", 0.1, 3.0, 1.0)
        layout.addWidget(self.brightness_slider, 1, 0, 1, 2)
        
        self.contrast_slider = LabeledSlider("Contrast", 0.1, 3.0, 1.0)
        layout.addWidget(self.contrast_slider, 2, 0, 1, 2)
        
        self.saturation_slider = LabeledSlider("Saturation", 0.0, 3.0, 1.0)
        layout.addWidget(self.saturation_slider, 3, 0, 1, 2)
        
        self.gamma_slider = LabeledSlider("Gamma", 0.1, 3.0, 1.0)
        layout.addWidget(self.gamma_slider, 4, 0, 1, 2)
        
        # Reset button
        reset_btn = QPushButton("Reset All")
        reset_btn.setMaximumWidth(80)
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn, 5, 1)
        
        self.setLayout(layout)
    
    def reset_all(self):
        """Reset all post-processing to defaults."""
        self.colormap_combo.setCurrentText("None (RGB)")
        self.brightness_slider.setValue(1.0)
        self.contrast_slider.setValue(1.0)
        self.saturation_slider.setValue(1.0)
        self.gamma_slider.setValue(1.0)
        self.app.generate_image()


class ButtonBar(QWidget):
    """Action buttons bar."""
    
    def __init__(self, app: 'MathArtApp', parent=None):
        super().__init__(parent)
        self.app = app
        layout = QHBoxLayout(self)
        
        self.generate_btn = ImageButton(
            "⚡ Generate", 
            f"Generate image ({SHORTCUTS['generate']})"
        )
        
        self.random_btn = ImageButton(
            "🎲 Random",
            f"Randomize all settings ({SHORTCUTS['random']})",
            "random_btn"
        )
        
        self.copy_btn = ImageButton(
            "📋 Copy",
            f"Copy formulas to clipboard ({SHORTCUTS['copy_formula']})",
            "copy_btn"
        )
        
        self.save_btn = ImageButton(
            "💾 Save",
            f"Save image ({SHORTCUTS['save']})"
        )
        
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.random_btn)
        layout.addWidget(self.copy_btn)
        layout.addWidget(self.save_btn)