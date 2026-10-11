import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QDoubleSpinBox, QFileDialog, QGroupBox, QSlider, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage

# -------------------------------
# FUNCTION MAP
# -------------------------------
def mandelbrot_func(x, y, rng=None, params=None):
    """True iterative Mandelbrot set calculation"""
    c = (x + 1j * y) * params["zoom"] + complex(params["center_x"], params["center_y"])
    z = np.zeros_like(c, dtype=complex)
    img = np.zeros(c.shape, dtype=np.float64)
    
    max_iter = int(params["max_iter"])
    for _ in range(max_iter):
        mask = np.abs(z) <= 2
        z[mask] = z[mask]**2 + c[mask]
        img[mask] += 1
        
    # Normalize to -1, 1 range
    return np.clip((img / max_iter) * 2 - 1, -1, 1) * params["amplitude"]

FUNCTION_MAP = {
    "Sine Wave": {
        "func": lambda x, y, rng=None, params=None: np.sin(x*params["frequency"]+params["phase"])*params["amplitude"],
        "desc":"Sine wave along X-axis",
        "params":{"frequency":(1,50,10),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0)}
    },
    "Cosine Wave": {
        "func": lambda x, y, rng=None, params=None: np.cos(x*params["frequency"]+params["phase"])*params["amplitude"],
        "desc":"Cosine wave along X-axis",
        "params":{"frequency":(1,50,10),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0)}
    },
    "Radial Wave": {
        "func": lambda x, y, rng=None, params=None: np.sin(np.sqrt(x**2+y**2)*params["frequency"]+params["phase"])*params["amplitude"],
        "desc":"Concentric radial waves",
        "params":{"frequency":(1,50,10),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0)}
    },
    "Lissajous": {
        "func": lambda x, y, rng=None, params=None: np.sin(x*params["freq_x"] + params["phase_x"])*np.cos(y*params["freq_y"] + params["phase_y"])*params["amplitude"],
        "desc":"Lissajous curve interference pattern",
        "params":{"freq_x":(1,50,10),"freq_y":(1,50,10),"phase_x":(0,6.28,0.0),"phase_y":(0,6.28,0.0),"amplitude":(0.1,2.0,1.0)}
    },
    "Plasma": {
        "func": lambda x, y, rng=None, params=None: (
            np.sin(x*params["freq1"]+params["phase1"])+
            np.sin(y*params["freq2"]+params["phase2"])+
            np.sin((x+y)*params["freq3"]+params["phase3"])
        )*params["amplitude"]/3.0,
        "desc":"Classic procedural plasma pattern",
        "params":{"freq1":(1,50,5),"freq2":(1,50,10),"freq3":(1,50,15),
                  "phase1":(0,6.28,0.0),"phase2":(0,6.28,0.0),"phase3":(0,6.28,0.0),
                  "amplitude":(0.1,2.0,1.0)}
    },
    "Fractal (Mandelbrot)": {
        "func": mandelbrot_func,
        "desc":"True iterative Mandelbrot fractal",
        "params":{"max_iter":(5,150,30),"zoom":(0.5,5.0,1.5),"center_x":(-2.0,2.0,-0.5),"center_y":(-2.0,2.0,0.0),"amplitude":(0.1,2.0,1.0)}
    },
    "Spiral Interference": {
        "func": lambda x, y, rng=None, params=None: np.sin(np.sqrt(x**2+y**2)*params["freq_radial"]+np.arctan2(y,x)*params["freq_angular"]+params["phase"])*params["amplitude"],
        "desc":"Spiral waves with adjustable radial & angular frequency",
        "params":{"freq_radial":(1,30,10),"freq_angular":(1,50,20),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0)}
    },
    "Ripple Interference": {
        "func": lambda x, y, rng=None, params=None: np.sin(np.sqrt(x**2+y**2)*params["radial_freq"])*np.cos(x*params["freq_x"]+y*params["freq_y"])*params["amplitude"],
        "desc":"Ripple pattern with X/Y interference",
        "params":{"radial_freq":(1,50,20),"freq_x":(0,50,10),"freq_y":(0,50,10),"amplitude":(0.1,2.0,1.0)}
    },
    "Fractal Rings": {
        "func": lambda x, y, rng=None, params=None: np.sin(np.sqrt(x**2+y**2)*params["frequency"])*np.sin(np.sqrt(np.abs(x*y))*params["scale"])*params["amplitude"],
        "desc":"Concentric fractal-like rings",
        "params":{"frequency":(5,50,20),"scale":(0.1,10,1.0),"amplitude":(0.1,2.0,1.0)}
    }
}

# -------------------------------
# Image generation
# -------------------------------
def generate_color_image(width, height, r_func, g_func, b_func, r_params, g_params, b_params, scale=1.0, offset=0.0, seed=None):
    rng = np.random.default_rng(seed) if seed is not None else None
    x = np.linspace(-1, 1, width) * scale + offset
    y = np.linspace(-1, 1, height) * scale + offset
    xv, yv = np.meshgrid(x, y)
    
    r = np.clip((r_func(xv, yv, rng, r_params) + 1) * 127.5, 0, 255).astype(np.uint8)
    g = np.clip((g_func(xv, yv, rng, g_params) + 1) * 127.5, 0, 255).astype(np.uint8)
    b = np.clip((b_func(xv, yv, rng, b_params) + 1) * 127.5, 0, 255).astype(np.uint8)
    return np.stack([r, g, b], axis=2)

# -------------------------------
# Dark Theme Stylesheet
# -------------------------------
DARK_STYLE = """
QWidget { background-color: #1e1e1e; color: #d4d4d4; font-size: 13px; }
QGroupBox { 
    border: 1px solid #444; border-radius: 5px; margin-top: 10px; padding-top: 15px; font-weight: bold; 
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
QPushButton { 
    background-color: #007acc; color: white; border: none; border-radius: 4px; padding: 8px 16px; font-weight: bold;
}
QPushButton:hover { background-color: #005f9e; }
QPushButton:checked { background-color: #d32f2f; }
QComboBox, QSpinBox, QDoubleSpinBox { 
    background-color: #2d2d2d; border: 1px solid #444; border-radius: 3px; padding: 4px; 
}
QSlider::groove:horizontal { height: 6px; background: #444; border-radius: 3px; }
QSlider::handle:horizontal { background: #007acc; width: 14px; margin: -4px 0; border-radius: 7px; }
QScrollArea { border: none; }
"""

# -------------------------------
# PySide6 App
# -------------------------------
class MathArtApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procedural Math Visual Generator")
        self.resize(1200, 800)

        self.function_map = {k: v["func"] for k, v in FUNCTION_MAP.items()}
        self.function_desc = {k: v["desc"] for k, v in FUNCTION_MAP.items()}
        self.function_params = {k: v["params"] for k, v in FUNCTION_MAP.items()}
        self.function_names = list(self.function_map.keys())

        self.offset_value = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        self.r_param_sliders = {}
        self.g_param_sliders = {}
        self.b_param_sliders = {}
        self._img_data = None  # Prevents garbage collection crashing QImage

        self.create_widgets()

    def create_widgets(self):
        # Main Horizontal Layout (Controls Left, Image Right)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- SCROLL AREA FOR CONTROLS ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(450)
        scroll.setMinimumWidth(350)
        
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setSpacing(10)

        # RGB combo boxes
        rgb_group = QGroupBox("RGB Channels")
        rgb_layout = QVBoxLayout()
        
        self.r_combo = self._create_channel_combo("Red", "#ff5555")
        self.g_combo = self._create_channel_combo("Green", "#55ff55")
        self.b_combo = self._create_channel_combo("Blue", "#5555ff")

        self.r_combo.currentTextChanged.connect(lambda: self.update_sliders("R"))
        self.g_combo.currentTextChanged.connect(lambda: self.update_sliders("G"))
        self.b_combo.currentTextChanged.connect(lambda: self.update_sliders("B"))

        rgb_layout.addLayout(self._wrap_combo("Red:", self.r_combo))
        rgb_layout.addLayout(self._wrap_combo("Green:", self.g_combo))
        rgb_layout.addLayout(self._wrap_combo("Blue:", self.b_combo))
        rgb_group.setLayout(rgb_layout)
        control_layout.addWidget(rgb_group)

        # Dynamic Slider Groups
        self.r_slider_group = QGroupBox("Red Parameters")
        self.r_slider_layout = QVBoxLayout()
        self.r_slider_group.setLayout(self.r_slider_layout)
        control_layout.addWidget(self.r_slider_group)

        self.g_slider_group = QGroupBox("Green Parameters")
        self.g_slider_layout = QVBoxLayout()
        self.g_slider_group.setLayout(self.g_slider_layout)
        control_layout.addWidget(self.g_slider_group)

        self.b_slider_group = QGroupBox("Blue Parameters")
        self.b_slider_layout = QVBoxLayout()
        self.b_slider_group.setLayout(self.b_slider_layout)
        control_layout.addWidget(self.b_slider_group)

        # General parameters
        param_group = QGroupBox("General Parameters")
        param_layout = QGridLayout()
        
        self.width_spin = self._create_spin(QSpinBox, 32, 4096, 512)
        self.height_spin = self._create_spin(QSpinBox, 32, 4096, 512)
        self.scale_spin = self._create_spin(QDoubleSpinBox, 0.01, 20.0, 1.0, 0.01)
        self.offset_spin = self._create_spin(QDoubleSpinBox, -10.0, 10.0, 0.0, 0.1)
        self.seed_spin = self._create_spin(QSpinBox, 0, 1000000, 0)

        param_layout.addWidget(QLabel("Width:"), 0, 0); param_layout.addWidget(self.width_spin, 0, 1)
        param_layout.addWidget(QLabel("Height:"), 1, 0); param_layout.addWidget(self.height_spin, 1, 1)
        param_layout.addWidget(QLabel("Scale:"), 2, 0); param_layout.addWidget(self.scale_spin, 2, 1)
        param_layout.addWidget(QLabel("Offset:"), 3, 0); param_layout.addWidget(self.offset_spin, 3, 1)
        param_layout.addWidget(QLabel("Seed:"), 4, 0); param_layout.addWidget(self.seed_spin, 4, 1)
        param_group.setLayout(param_layout)
        control_layout.addWidget(param_group)

        # Animation parameters
        anim_group = QGroupBox("Animation")
        anim_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_label = QLabel("Speed: 50ms")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(f"Speed: {v}ms"))
        anim_layout.addWidget(self.speed_label)
        anim_layout.addWidget(self.speed_slider)
        anim_group.setLayout(anim_layout)
        control_layout.addWidget(anim_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("⚡ Generate")
        self.generate_btn.clicked.connect(self.generate_image)
        
        self.animate_btn = QPushButton("▶ Animate")
        self.animate_btn.setCheckable(True)
        self.animate_btn.clicked.connect(self.toggle_animation)
        
        self.save_btn = QPushButton("💾 Save Image")
        self.save_btn.clicked.connect(self.save_image)
        
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.animate_btn)
        btn_layout.addWidget(self.save_btn)
        control_layout.addLayout(btn_layout)

        control_layout.addStretch() # Push everything to the top
        scroll.setWidget(control_widget)
        main_layout.addWidget(scroll)

        # --- IMAGE DISPLAY ---
        self.img_label = QLabel("Generate an image to begin")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background-color: #111; border: 1px solid #333; border-radius: 5px;")
        self.img_label.setMinimumSize(512, 512)
        main_layout.addWidget(self.img_label, 1) # Stretch factor 1 to take remaining space

        self.setLayout(main_layout)
        
        # Initialize sliders
        self.update_sliders("R")
        self.update_sliders("G")
        self.update_sliders("B")

    def _create_spin(self, spin_type, min_val, max_val, default, step=1):
        spin = spin_type()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        if isinstance(spin, QDoubleSpinBox):
            spin.setSingleStep(step)
            spin.setDecimals(3 if step < 0.01 else 2)
        return spin

    def _create_channel_combo(self, color_name, color_hex):
        combo = QComboBox()
        combo.addItems(self.function_names)
        combo.setStyleSheet(f"QComboBox {{ border: 1px solid {color_hex}; }}")
        return combo

    def _wrap_combo(self, text, combo):
        layout = QHBoxLayout()
        label = QLabel(text)
        label.setMinimumWidth(50)
        layout.addWidget(label)
        layout.addWidget(combo, 1)
        return layout

    def update_sliders(self, channel):
        if channel == "R": layout = self.r_slider_layout; combo = self.r_combo; sliders = self.r_param_sliders
        elif channel == "G": layout = self.g_slider_layout; combo = self.g_combo; sliders = self.g_param_sliders
        else: layout = self.b_slider_layout; combo = self.b_combo; sliders = self.b_param_sliders

        # Clear existing sliders safely
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clean up sub-layouts
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()
        sliders.clear()

        params = self.function_params[combo.currentText()]
        for name, (minv, maxv, default) in params.items():
            slider_layout = QHBoxLayout()
            
            # Calculate initial slider position mapped to 0-10000 for high precision
            initial_val = int((default - minv) / (maxv - minv) * 10000) if maxv != minv else 0
            
            label = QLabel(f"{name}: {default:.3f}")
            label.setMinimumWidth(120)
            
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(10000)
            slider.setValue(initial_val)
            
            # Lambda updated for precision (10000 steps)
            slider.valueChanged.connect(
                lambda val, l=label, n=name, mn=minv, mx=maxv: l.setText(f"{n}: {mn + (mx - mn) * val / 10000:.3f}")
            )
            
            slider_layout.addWidget(label)
            slider_layout.addWidget(slider, 1)
            layout.addLayout(slider_layout)
            sliders[name] = (slider, minv, maxv)

    def get_params_from_sliders(self, sliders):
        # Calculate actual float value from 10000-step slider
        return {name: minv + (maxv - minv) * slider.value() / 10000 for name, (slider, minv, maxv) in sliders.items()}

    def generate_image(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        scale = self.scale_spin.value()
        offset = self.offset_spin.value() + self.offset_value
        seed = self.seed_spin.value() if self.seed_spin.value() > 0 else None
        
        r_func = self.function_map[self.r_combo.currentText()]
        g_func = self.function_map[self.g_combo.currentText()]
        b_func = self.function_map[self.b_combo.currentText()]
        
        r_params = self.get_params_from_sliders(self.r_param_sliders)
        g_params = self.get_params_from_sliders(self.g_param_sliders)
        b_params = self.get_params_from_sliders(self.b_param_sliders)
        
        img_array = generate_color_image(width, height, r_func, g_func, b_func, r_params, g_params, b_params, scale, offset, seed)
        self.display_image(img_array)

    def display_image(self, img_array):
        # Crucial Fix: Keep a reference to the array so QImage doesn't get garbage collected
        self._img_data = img_array
        h, w, c = self._img_data.shape
        bytes_per_line = 3 * w
        
        qimg = QImage(self._img_data.data, w, h, bytes_per_line, QImage.Format.RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        # Scale pixmap to fit the label while keeping aspect ratio
        self.img_label.setPixmap(pixmap.scaled(
            self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def save_image(self):
        if self.img_label.pixmap() is None:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "math_art.png", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if file_path:
            # Save the original full-resolution data, not the scaled preview
            h, w, c = self._img_data.shape
            qimg = QImage(self._img_data.data, w, h, 3 * w, QImage.Format.RGB888)
            qimg.save(file_path)

    def toggle_animation(self, checked):
        if checked:
            self.timer.start(self.speed_slider.value())
            self.animate_btn.setText("⏸ Stop")
            self.generate_btn.setEnabled(False)
        else:
            self.timer.stop()
            self.animate_btn.setText("▶ Animate")
            self.generate_btn.setEnabled(True)

    def update_animation(self):
        self.offset_value += 0.02
        self.generate_image()
        
        # Dynamically adjust timer speed if user changes slider during animation
        if self.timer.isActive():
            self.timer.setInterval(self.speed_slider.value())

    # Allow the image preview to resize properly when the window is resized
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._img_data is not None:
            h, w, c = self._img_data.shape
            qimg = QImage(self._img_data.data, w, h, 3 * w, QImage.Format.RGB888)
            self.img_label.setPixmap(QPixmap.fromImage(qimg).scaled(
                self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE) # Apply modern dark theme
    window = MathArtApp()
    window.show()
    sys.exit(app.exec())