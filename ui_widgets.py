# ui_widgets.py - Minimalist UI widgets
import random
from typing import Dict, Optional, TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QPlainTextEdit, QProgressBar, QSlider, QFrame
)
from PySide6.QtCore import Qt, Signal

from config import (
    RESOLUTION_PRESETS, MIN_RESOLUTION, MAX_RESOLUTION,
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_SCALE, MIN_SCALE, MAX_SCALE,
    DEFAULT_SPEED_MS, MIN_SPEED_MS, MAX_SPEED_MS, TIME_STEP, SHORTCUTS,
    SLIDER_PRECISION, FORMULA_PRESETS, COLORMAPS,
    GIF_DEFAULT_FRAMES, GIF_MIN_FRAMES, GIF_MAX_FRAMES,
    GIF_DEFAULT_FPS, GIF_MIN_FPS, GIF_MAX_FPS,
)
from presets import FUNCTION_MAP

if TYPE_CHECKING:
    from app import MathArtApp


# ═══════════════════════════════════
#  Components
# ═══════════════════════════════════

class LabeledSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, name, min_val, max_val, default_val, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.precision = 3
        self._name = name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.label = QLabel(f"{name} {default_val:.{self.precision}f}")
        self.label.setFixedWidth(100)
        self.label.setStyleSheet("color: #555; font-size: 11px;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(SLIDER_PRECISION)
        self.slider.setValue(self._f2s(default_val))
        self.slider.valueChanged.connect(self._on_change)

        layout.addWidget(self.label)
        layout.addWidget(self.slider, 1)

    def _f2s(self, v):
        if self.max_val == self.min_val:
            return 0
        return int(
            (max(self.min_val, min(self.max_val, v)) - self.min_val)
            / (self.max_val - self.min_val) * SLIDER_PRECISION
        )

    def _s2f(self, v):
        return self.min_val + (self.max_val - self.min_val) * v / SLIDER_PRECISION

    def _on_change(self, v):
        fv = self._s2f(v)
        self.label.setText(f"{self._name} {fv:.{self.precision}f}")
        self.valueChanged.emit(fv)

    def value(self):
        return self._s2f(self.slider.value())

    def setValue(self, v):
        c = max(self.min_val, min(self.max_val, v))
        self.slider.blockSignals(True)
        self.slider.setValue(self._f2s(c))
        self.slider.blockSignals(False)
        self.label.setText(f"{self._name} {c:.{self.precision}f}")

    def setEnabled(self, e):
        self.slider.setEnabled(e)
        self.label.setEnabled(e)


class ProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(2)
        self.progress_bar.hide()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #333; font-size: 10px;")
        layout.addWidget(self.status_label, 1)
        layout.addWidget(self.progress_bar, 3)

    def show_progress(self, m=""):
        self.status_label.setText(m)
        self.status_label.setStyleSheet("color: #444; font-size: 10px;")
        self.progress_bar.show()
        self.progress_bar.setValue(0)

    def update_progress(self, v, m=""):
        self.progress_bar.setValue(min(100, max(0, v)))
        if m:
            self.status_label.setText(m)

    def hide_progress(self, m=""):
        self.progress_bar.hide()
        self.status_label.setText(m)
        self.status_label.setStyleSheet("color: #333; font-size: 10px;")

    def set_status(self, m):
        self.status_label.setText(m)


class ImageButton(QPushButton):
    def __init__(self, text, tooltip="", obj_name="", parent=None):
        super().__init__(text, parent)
        self.setToolTip(tooltip)
        if obj_name:
            self.setObjectName(obj_name)
        self.setFixedHeight(24)


class ChannelSelector(QWidget):
    selectionChanged = Signal()

    def __init__(self, function_names, parent=None):
        super().__init__(parent)
        self.function_names = function_names
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.setVerticalSpacing(3)
        self.combos = {}
        for row, (k, c) in enumerate([("R", "#664444"), ("G", "#446644"), ("B", "#444466")]):
            lbl = QLabel(k)
            lbl.setFixedWidth(14)
            lbl.setStyleSheet(f"color: {c}; font-weight: 700; font-size: 12px;")
            cb = QComboBox()
            cb.addItems(self.function_names)
            cb.currentTextChanged.connect(self.selectionChanged.emit)
            layout.addWidget(lbl, row, 0)
            layout.addWidget(cb, row, 1)
            self.combos[k] = cb

    def currentFunctions(self):
        return {k: c.currentText() for k, c in self.combos.items()}

    def setFunction(self, ch, n):
        if ch in self.combos:
            idx = self.combos[ch].findText(n)
            if idx >= 0:
                self.combos[ch].setCurrentIndex(idx)

    def randomize(self):
        for c in self.combos.values():
            c.setCurrentIndex(random.randint(0, len(self.function_names) - 1))


def create_info_label():
    l = QLabel("")
    l.setObjectName("info_label")
    l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return l


def create_error_label():
    l = QLabel("")
    l.setObjectName("error_label")
    l.setWordWrap(True)
    l.setMaximumHeight(36)
    return l


def create_time_label():
    l = QLabel("t = 0.000")
    l.setObjectName("time_label")
    l.setAlignment(Qt.AlignCenter)
    return l


def create_hover_label():
    l = QLabel("")
    l.setObjectName("hover_label")
    l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    return l


# ═══════════════════════════════════
#  Tabs
# ═══════════════════════════════════

class PresetsTab(QWidget):
    def __init__(self, app: 'MathArtApp', parent=None):
        super().__init__(parent)
        self.app = app
        self.sliders: Dict[str, LabeledSlider] = {}
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 4, 0, 0)

        self.channel_selector = ChannelSelector(app.function_names)
        self.channel_selector.selectionChanged.connect(self.update_sliders)
        layout.addWidget(self.channel_selector)

        self.slider_container = QWidget()
        self.slider_layout = QVBoxLayout(self.slider_container)
        self.slider_layout.setSpacing(1)
        self.slider_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.slider_container, 1)

    def update_sliders(self):
        while self.slider_layout.count():
            it = self.slider_layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        self.sliders.clear()

        for ch, combo in self.channel_selector.combos.items():
            fn = combo.currentText()
            if fn not in self.app.function_params:
                continue
            params = FUNCTION_MAP[fn]["params"]
            lbl = QLabel(f"{ch} · {fn}")
            lbl.setStyleSheet("color: #444; font-size: 10px; padding-top: 4px;")
            self.slider_layout.addWidget(lbl)
            for n, (minv, maxv, d) in params.items():
                s = LabeledSlider(n, minv, maxv, d)
                s.valueChanged.connect(lambda v, c=ch: self.app._debounced_generate())
                self.slider_layout.addWidget(s)
                self.sliders[f"{ch}_{n}"] = s

        self.slider_layout.addStretch()

    def randomize(self):
        self.channel_selector.randomize()
        for s in self.sliders.values():
            s.setValue(random.uniform(s.min_val, s.max_val))


class CustomTab(QWidget):
    def __init__(self, app: 'MathArtApp', parent=None):
        super().__init__(parent)
        self.app = app
        self.sliders: Dict[str, LabeledSlider] = {}
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 4, 0, 0)

        # Preset row
        pr = QHBoxLayout()
        pr.setSpacing(6)
        pr.addWidget(QLabel("Preset"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("—")
        for n in FORMULA_PRESETS:
            self.preset_combo.addItem(n)
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        pr.addWidget(self.preset_combo, 1)
        layout.addLayout(pr)

        # Formula editors — ultra compact
        self.r_text = QPlainTextEdit("sin(x*10*a + t)")
        self.g_text = QPlainTextEdit("cos(y*10*b + t)")
        self.b_text = QPlainTextEdit("sin(sqrt(x**2 + y**2)*15*c - t)")

        for label, te, color, ch in [
            ("R", self.r_text, "#664444", "R"),
            ("G", self.g_text, "#446644", "G"),
            ("B", self.b_text, "#444466", "B"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(4)
            lbl = QLabel(label)
            lbl.setFixedWidth(14)
            lbl.setStyleSheet(f"color: {color}; font-weight: 700; font-size: 12px;")
            vb = QPushButton("✓")
            vb.setObjectName("validate_btn")
            vb.setFixedSize(22, 22)
            vb.clicked.connect(lambda ck, t=te, x=ch: self.app._validate_channel(t, x))
            row.addWidget(lbl)
            row.addWidget(te, 1)
            row.addWidget(vb)
            te.setFixedHeight(44)
            layout.addLayout(row)

        # Variables
        vl = QHBoxLayout()
        vl.setSpacing(6)
        for v, d in {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}.items():
            s = LabeledSlider(v, -5.0, 5.0, d)
            s.label.setFixedWidth(36)
            s.valueChanged.connect(lambda val: self.app._debounced_generate())
            vl.addWidget(s)
            self.sliders[v] = s
        layout.addLayout(vl)

        # Help — collapsed
        help_lbl = QLabel(
            "<span style='color:#333;font-size:10px;'>"
            "sin cos tan atan2 sinh cosh tanh exp log log2 sqrt abs · "
            "erf gamma · x y r θ t · a b c d · pi e tau phi"
            "</span>"
        )
        help_lbl.setWordWrap(True)
        layout.addWidget(help_lbl)

    def load_preset(self, t):
        if t == "—":
            return
        if t in FORMULA_PRESETS:
            p = FORMULA_PRESETS[t]
            self.r_text.setPlainText(p["R"])
            self.g_text.setPlainText(p["G"])
            self.b_text.setPlainText(p["B"])
            for v, val in p.get("vars", {}).items():
                if v in self.sliders:
                    self.sliders[v].setValue(val)
            self.app.generate_image()

    def randomize(self):
        for s in self.sliders.values():
            s.setValue(random.uniform(s.min_val, s.max_val))


# ═══════════════════════════════════
#  Panels
# ═══════════════════════════════════

class SettingsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Resolution", parent)
        layout = QGridLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 10, 0, 4)

        self.resolution_combo = QComboBox()
        for n in RESOLUTION_PRESETS:
            self.resolution_combo.addItem(n)
        self.resolution_combo.setCurrentText("512×512")
        self.resolution_combo.currentTextChanged.connect(self._preset_changed)
        layout.addWidget(self.resolution_combo, 0, 0, 1, 2)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(MIN_RESOLUTION, MAX_RESOLUTION)
        self.width_spin.setValue(DEFAULT_WIDTH)
        self.width_spin.valueChanged.connect(self._res_changed)
        self.width_spin.setPrefix("W ")
        self.width_spin.setFixedWidth(90)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(MIN_RESOLUTION, MAX_RESOLUTION)
        self.height_spin.setValue(DEFAULT_HEIGHT)
        self.height_spin.valueChanged.connect(self._res_changed)
        self.height_spin.setPrefix("H ")
        self.height_spin.setFixedWidth(90)

        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(MIN_SCALE, MAX_SCALE)
        self.scale_spin.setValue(DEFAULT_SCALE)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setDecimals(2)
        self.scale_spin.setPrefix("× ")
        self.scale_spin.setFixedWidth(80)

        layout.addWidget(self.width_spin, 1, 0)
        layout.addWidget(self.height_spin, 1, 1)
        layout.addWidget(self.scale_spin, 2, 0)

        self.preview_check = QCheckBox("Half-res preview")
        self.preview_check.setChecked(True)
        layout.addWidget(self.preview_check, 2, 1)
        self.setLayout(layout)

    def _preset_changed(self, t):
        if t in RESOLUTION_PRESETS and RESOLUTION_PRESETS[t]:
            self.width_spin.setValue(RESOLUTION_PRESETS[t][0])
            self.height_spin.setValue(RESOLUTION_PRESETS[t][1])

    def _res_changed(self):
        w, h = self.width_spin.value(), self.height_spin.value()
        for n, s in RESOLUTION_PRESETS.items():
            if s == (w, h):
                self.resolution_combo.blockSignals(True)
                self.resolution_combo.setCurrentText(n)
                self.resolution_combo.blockSignals(False)
                return
        self.resolution_combo.blockSignals(True)
        self.resolution_combo.setCurrentText("Custom")
        self.resolution_combo.blockSignals(False)


class AnimationPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Animate", parent)
        layout = QHBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 10, 0, 4)

        self.animate_btn = QPushButton("Play")
        self.animate_btn.setCheckable(True)
        self.animate_btn.setFixedWidth(44)
        self.animate_btn.setToolTip(f"Space")

        self.step_btn = QPushButton("Step")
        self.step_btn.setObjectName("step_btn")
        self.step_btn.setFixedWidth(38)
        self.step_btn.setToolTip(f"{SHORTCUTS['step']}")

        self.reset_time_btn = QPushButton("0")
        self.reset_time_btn.setObjectName("reset_btn")
        self.reset_time_btn.setFixedWidth(26)
        self.reset_time_btn.setToolTip("Reset time")

        self.speed_slider = LabeledSlider("ms", MIN_SPEED_MS, MAX_SPEED_MS, DEFAULT_SPEED_MS)
        self.speed_slider.precision = 0
        self.speed_slider.label.setFixedWidth(30)
        self.speed_slider.label.setText(f"{DEFAULT_SPEED_MS}ms")

        self.timestep_slider = LabeledSlider("dt", 0.001, 0.5, TIME_STEP)
        self.timestep_slider.label.setFixedWidth(30)

        self.time_label = create_time_label()
        self.time_label.setFixedWidth(80)

        layout.addWidget(self.animate_btn)
        layout.addWidget(self.step_btn)
        layout.addWidget(self.reset_time_btn)
        layout.addWidget(self.speed_slider, 1)
        layout.addWidget(self.timestep_slider, 1)
        layout.addWidget(self.time_label)
        self.setLayout(layout)


class PostProcessPanel(QGroupBox):
    def __init__(self, app: 'MathArtApp', parent=None):
        super().__init__("Post-Process", parent)
        self.app = app
        layout = QGridLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(0, 10, 0, 4)

        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(COLORMAPS.keys())
        self.colormap_combo.setFixedWidth(100)
        layout.addWidget(self.colormap_combo, 0, 0)

        self.brightness_slider = LabeledSlider("Bri", 0.1, 3.0, 1.0)
        layout.addWidget(self.brightness_slider, 0, 1)
        self.contrast_slider = LabeledSlider("Con", 0.1, 3.0, 1.0)
        layout.addWidget(self.contrast_slider, 0, 2)
        self.saturation_slider = LabeledSlider("Sat", 0.0, 3.0, 1.0)
        layout.addWidget(self.saturation_slider, 1, 1)
        self.gamma_slider = LabeledSlider("Gam", 0.1, 3.0, 1.0)
        layout.addWidget(self.gamma_slider, 1, 2)

        reset_btn = QPushButton("R")
        reset_btn.setFixedSize(22, 22)
        reset_btn.setToolTip("Reset all")
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn, 0, 3)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        self.setLayout(layout)

    def reset_all(self):
        self.colormap_combo.setCurrentText("RGB")
        for s in [self.brightness_slider, self.contrast_slider,
                   self.saturation_slider, self.gamma_slider]:
            s.setValue(1.0)
        self.app.generate_image()


class GifExportPanel(QGroupBox):
    exportRequested = Signal()

    def __init__(self, parent=None):
        super().__init__("GIF", parent)
        layout = QHBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(0, 10, 0, 4)

        layout.addWidget(QLabel("Frames"))
        self.frames_spin = QSpinBox()
        self.frames_spin.setRange(GIF_MIN_FRAMES, GIF_MAX_FRAMES)
        self.frames_spin.setValue(GIF_DEFAULT_FRAMES)
        self.frames_spin.setFixedWidth(54)
        layout.addWidget(self.frames_spin)

        layout.addWidget(QLabel("FPS"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(GIF_MIN_FPS, GIF_MAX_FPS)
        self.fps_spin.setValue(GIF_DEFAULT_FPS)
        self.fps_spin.setFixedWidth(42)
        layout.addWidget(self.fps_spin)

        self.duration_label = QLabel()
        self.duration_label.setStyleSheet("color: #333; font-size: 10px;")
        layout.addWidget(self.duration_label)

        self.ping_pong_check = QCheckBox("PP")
        self.ping_pong_check.setToolTip("Ping-pong")
        layout.addWidget(self.ping_pong_check)

        self.full_res_check = QCheckBox("Full")
        self.full_res_check.setToolTip("Full resolution")
        layout.addWidget(self.full_res_check)

        self.export_btn = QPushButton("Export")
        self.export_btn.setObjectName("gif_btn")
        self.export_btn.setFixedWidth(52)
        self.export_btn.clicked.connect(self.exportRequested.emit)
        layout.addWidget(self.export_btn)

        self.cancel_btn = QPushButton("×")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setFixedWidth(22)
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)

        self.gif_progress = QProgressBar()
        self.gif_progress.setRange(0, 100)
        self.gif_progress.setTextVisible(False)
        self.gif_progress.setMaximumHeight(2)
        self.gif_progress.hide()
        layout.addWidget(self.gif_progress, 1)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #333; font-size: 10px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self._worker = None

        self.frames_spin.valueChanged.connect(self._update_duration)
        self.fps_spin.valueChanged.connect(self._update_duration)
        self.ping_pong_check.stateChanged.connect(self._update_duration)
        self._update_duration()

    def _update_duration(self):
        frames = self.frames_spin.value()
        fps = self.fps_spin.value()
        dur = frames / fps
        if self.ping_pong_check.isChecked() and frames > 2:
            dur = (frames + frames - 2) / fps
        self.duration_label.setText(f"{dur:.1f}s")

    def get_timeline_max_time(self):
        return self.frames_spin.value() * TIME_STEP

    def set_worker(self, worker):
        self._worker = worker

    def _on_cancel(self):
        if self._worker:
            self._worker.abort()

    def show_exporting(self):
        self.export_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.gif_progress.show()
        self.gif_progress.setValue(0)
        self.status_label.setText("…")
        self.status_label.setStyleSheet("color: #555; font-size: 10px;")

    def update_progress(self, current, total):
        pct = int(current / total * 100)
        self.gif_progress.setValue(pct)
        self.status_label.setText(f"{current}/{total}")

    def show_done(self, msg):
        self.export_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.gif_progress.hide()
        self.status_label.setText("done")
        self.status_label.setStyleSheet("color: #408050; font-size: 10px;")

    def show_error(self, msg):
        self.export_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.gif_progress.hide()
        self.status_label.setText("err")
        self.status_label.setStyleSheet("color: #a04040; font-size: 10px;")


class TimelineScrubber(QWidget):
    timeChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(4)

        self.start_label = QLabel("0")
        self.start_label.setObjectName("timeline_label")
        self.start_label.setFixedWidth(20)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setValue(0)
        self.slider.setToolTip("Scrub time")
        self.slider.valueChanged.connect(self._on_slider)

        self.end_label = QLabel("5.0")
        self.end_label.setObjectName("timeline_label")
        self.end_label.setFixedWidth(30)
        self.end_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.start_label)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.end_label)

        self._max_time = 5.0
        self._programmatic = False

    def set_range(self, max_time):
        self._max_time = max(0.01, max_time)
        self.end_label.setText(f"{self._max_time:.1f}")

    def set_time(self, t):
        self._programmatic = True
        pos = int(t / self._max_time * 1000) if self._max_time > 0 else 0
        pos = max(0, min(1000, pos))
        self.slider.setValue(pos)
        self._programmatic = False

    def _on_slider(self, val):
        if self._programmatic:
            return
        t = val / 1000.0 * self._max_time
        self.timeChanged.emit(t)


class ButtonBar(QWidget):
    def __init__(self, app: 'MathArtApp', parent=None):
        super().__init__(parent)
        self.app = app
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        self.lock_btn = ImageButton(
            "Auto", "Toggle auto-gen (Ctrl+L)", "lock_btn"
        )
        self.lock_btn.setCheckable(True)
        self.lock_btn.setFixedWidth(40)

        self.generate_btn = ImageButton(
            "Generate", f"Generate ({SHORTCUTS['generate']})", "generate_btn"
        )
        self.random_btn = ImageButton(
            "Random", f"Random ({SHORTCUTS['random']})", "random_btn"
        )
        self.copy_btn = ImageButton(
            "Copy", f"Copy formulas ({SHORTCUTS['copy_formula']})", "copy_btn"
        )
        self.save_btn = ImageButton(
            "Save", f"Save ({SHORTCUTS['save']})", "save_btn"
        )

        for b in [self.lock_btn, self.generate_btn, self.random_btn,
                   self.copy_btn, self.save_btn]:
            layout.addWidget(b)