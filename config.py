# config.py - Configuration and constants
APP_VERSION = "3.0.0"
APP_NAME = "Math Art Studio"

RESOLUTION_PRESETS = {
    "512×512": (512, 512), "1280×720": (1280, 720),
    "1920×1080": (1920, 1080), "2560×1440": (2560, 1440),
    "3840×2160": (3840, 2160), "1024×1024": (1024, 1024),
    "2048×2048": (2048, 2048), "Custom": None
}

EXPORT_FORMATS = {
    "PNG": ("png", 100), "JPEG (95)": ("jpg", 95),
    "JPEG (80)": ("jpg", 80), "BMP": ("bmp", 100),
}

DEFAULT_SPEED_MS = 50; MIN_SPEED_MS = 10; MAX_SPEED_MS = 200
TIME_STEP = 0.05; SLIDER_PRECISION = 10000
MIN_RESOLUTION = 32; MAX_RESOLUTION = 4096
DEFAULT_WIDTH = 512; DEFAULT_HEIGHT = 512
DEFAULT_SCALE = 1.0; MIN_SCALE = 0.1; MAX_SCALE = 20.0

GIF_DEFAULT_FRAMES = 60; GIF_MIN_FRAMES = 2; GIF_MAX_FRAMES = 300
GIF_DEFAULT_FPS = 20; GIF_MIN_FPS = 1; GIF_MAX_FPS = 60

SHORTCUTS = {
    "generate": "Ctrl+G", "animate_toggle": "Space", "step": "Ctrl+Right",
    "reset_time": "Ctrl+R", "random": "Ctrl+Shift+R", "save": "Ctrl+S",
    "fullscreen": "F11", "copy_formula": "Ctrl+C", "validate": "Ctrl+Enter",
    "zoom_in": "Ctrl+=", "zoom_out": "Ctrl+-", "fit_to_window": "Ctrl+0",
    "export_gif": "Ctrl+Shift+G", "toggle_lock": "Ctrl+L",
}

COLORMAPS = {
    "RGB": None, "Grayscale": "grayscale", "Sepia": "sepia",
    "Thermal": "thermal", "Ocean": "ocean", "Neon": "neon",
    "Invert": "inverted", "Vintage": "vintage", "Cyberpunk": "cyberpunk",
    "Sunset": "sunset", "Forest": "forest", "Ice": "ice",
}

FORMULA_PRESETS = {
    "Psychedelic Swirl": {"R": "sin(x*10*a + t) * cos(y*10*b + t)", "G": "cos(sqrt(x**2 + y**2)*15*c - t)", "B": "sin(atan2(y, x)*5*d + t)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0}},
    "Electric Storm": {"R": "sin(x*x*a*20 + y*y*b*20) * cos(t)", "G": "cos(x*y*20*c + t*2)", "B": "sin(sqrt(abs(x*a) + abs(y*b))*15 - t)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Black Hole": {"R": "sin(1/(sqrt(x**2+y**2)*a+0.05) - t*2) * exp(-sqrt(x**2+y**2))", "G": "cos(atan2(y,x)*5 + 1/(sqrt(x**2+y**2)*a+0.05) - t)", "B": "sin(1/(sqrt(x**2+y**2)*a+0.05) + t*2) * exp(-sqrt(x**2+y**2)*0.5)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Error Function": {"R": "erf(x*5*a + t) * exp(-y**2*5)", "G": "erf(y*5*b - t) * exp(-x**2*5)", "B": "erf(sqrt(x**2+y**2)*5*c - t*2)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Hyperbolic Warp": {"R": "tanh(sin(x*10*a + t)*3)", "G": "sinh(cos(y*10*b - t)*0.5)", "B": "cosh(sqrt(x**2+y**2)*5*c) - 1", "vars": {"a": 1.0, "b": 1.0, "c": 0.5, "d": 0.0}},
    "Gamma Field": {"R": "sin(gamma(x*a + 2)*0.1 + t)", "G": "cos(gamma(y*b + 2)*0.1 - t*2)", "B": "sin(gamma(r*c + 2)*0.1 + t)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Polar Rose": {"R": "sin(cos(theta*3 + t)*5*a)", "G": "cos(sin(theta*5 - t)*5*b)", "B": "sin(r*10*c - theta*3 + t)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Fractal Noise": {"R": "sin(x*10*a + sin(y*10*b + t)*3)", "G": "sin(y*10*b + sin(x*10*c - t)*3)", "B": "sin(r*15*d + sin(theta*5 + t)*2)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.7}},
    "Neon Grid": {"R": "exp(-abs(sin(x*10*a + t))*10)", "G": "exp(-abs(sin(y*10*b - t))*10)", "B": "exp(-abs(sin((x+y)*5*c))*10)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Warp Drive": {"R": "sin(x*a*10 + sin(y*20 + t)*0.5)", "G": "sin(y*b*10 + cos(x*20 - t)*0.5)", "B": "sin(r*c*20 - t*3) * exp(-r*2)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
}

DARK_STYLE = """
QWidget {
    background-color: #0e0e0e;
    color: #999;
    font-size: 12px;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}
QWidget::disabled { color: #333; }

/* ── GroupBox ── */
QGroupBox {
    border: none;
    border-top: 1px solid #1e1e1e;
    border-radius: 0;
    margin-top: 14px;
    padding: 10px 0 0 0;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #555;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 0;
    padding: 0 6px 0 0;
}

/* ── Buttons ── */
QPushButton {
    background-color: #1a1a1a;
    color: #888;
    border: 1px solid #252525;
    border-radius: 3px;
    padding: 5px 10px;
    font-weight: 500;
    font-size: 11px;
    min-height: 18px;
}
QPushButton:hover { background-color: #222; color: #bbb; border-color: #333; }
QPushButton:pressed { background-color: #111; }
QPushButton:checked { background-color: #1a1a1a; color: #c94040; border-color: #c94040; }
QPushButton:disabled { background-color: #111; color: #2a2a2a; border-color: #1a1a1a; }

QPushButton#random_btn { color: #9060b0; }
QPushButton#random_btn:hover { background-color: #1f1a24; border-color: #3a2a4a; }
QPushButton#step_btn { color: #408050; }
QPushButton#step_btn:hover { background-color: #141f16; border-color: #2a3a2a; }
QPushButton#reset_btn { color: #906030; }
QPushButton#reset_btn:hover { background-color: #1f1814; border-color: #3a2a1a; }
QPushButton#copy_btn { color: #406090; }
QPushButton#copy_btn:hover { background-color: #14181f; border-color: #1a2a3a; }
QPushButton#validate_btn { color: #408050; }
QPushButton#validate_btn:hover { background-color: #141f16; border-color: #2a3a2a; }
QPushButton#gif_btn { color: #c04040; }
QPushButton#gif_btn:hover { background-color: #1f1414; border-color: #3a1a1a; }
QPushButton#lock_btn:checked { color: #b08020; border-color: #b08020; }
QPushButton#lock_btn:checked:hover { background-color: #1f1a10; }

/* Primary action */
QPushButton#generate_btn {
    background-color: #14303e;
    color: #5090b0;
    border-color: #1a4050;
}
QPushButton#generate_btn:hover {
    background-color: #1a3a4a;
    color: #60a0c0;
    border-color: #205060;
}
QPushButton#save_btn {
    background-color: #14303e;
    color: #5090b0;
    border-color: #1a4050;
}
QPushButton#save_btn:hover {
    background-color: #1a3a4a;
    color: #60a0c0;
    border-color: #205060;
}

/* ── ComboBox & SpinBox ── */
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 2px;
    padding: 3px 6px;
    min-height: 18px;
    color: #888;
    selection-background-color: #1a3040;
    selection-color: #6090b0;
}
QComboBox::drop-down {
    border: none;
    width: 18px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid #444;
    margin-right: 4px;
}
QComboBox QAbstractItemView {
    background-color: #141414;
    border: 1px solid #1e1e1e;
    outline: none;
    selection-background-color: #1a3040;
    selection-color: #6090b0;
}
QComboBox::item { padding: 4px 8px; }
QComboBox::item:selected { background-color: #1a3040; }

/* ── Slider ── */
QSlider::groove:horizontal {
    height: 2px;
    background: #1e1e1e;
    border-radius: 1px;
}
QSlider::handle:horizontal {
    background: #444;
    width: 10px;
    height: 10px;
    margin: -4px 0;
    border-radius: 5px;
}
QSlider::handle:horizontal:hover { background: #555; }
QSlider::sub-page:horizontal {
    background: #1a3040;
    border-radius: 1px;
}

/* ── ScrollArea ── */
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #222;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover { background: #333; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #222;
    min-width: 20px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover { background: #333; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* ── Tabs ── */
QTabWidget::pane {
    border: none;
    border-bottom: 1px solid #1e1e1e;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: #555;
    padding: 7px 14px;
    border: none;
    border-bottom: 1px solid transparent;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.3px;
}
QTabBar::tab:hover { color: #888; }
QTabBar::tab:selected {
    color: #7090a0;
    border-bottom: 1px solid #406070;
}

/* ── Text Edit ── */
QPlainTextEdit {
    background-color: #0a0a0a;
    color: #5a8a70;
    border: 1px solid #1a1a1a;
    border-radius: 2px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 12px;
    padding: 4px 6px;
    selection-background-color: #1a3040;
}
QPlainTextEdit:focus { border-color: #253540; }

/* ── Labels ── */
QLabel#error_label { color: #a04040; font-size: 11px; }
QLabel#success_label { color: #408050; font-size: 11px; }
QLabel#info_label { color: #333; font-size: 10px; }
QLabel#time_label { color: #555; font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 12px; }
QLabel#hover_label { color: #333; font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 10px; }
QLabel#timeline_label { color: #444; font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 10px; }

/* ── Status Bar ── */
QStatusBar {
    background-color: #0a0a0a;
    color: #333;
    border-top: 1px solid #1a1a1a;
    font-size: 10px;
    padding: 1px 6px;
}

/* ── Menu ── */
QMenuBar {
    background-color: #0a0a0a;
    border-bottom: 1px solid #1a1a1a;
    padding: 1px;
}
QMenuBar::item {
    padding: 4px 10px;
    color: #666;
    font-size: 11px;
}
QMenuBar::item:selected { background-color: #141414; color: #aaa; }
QMenu {
    background-color: #111;
    border: 1px solid #1e1e1e;
    padding: 2px;
}
QMenu::item {
    padding: 4px 20px;
    border-radius: 2px;
    font-size: 11px;
    color: #777;
}
QMenu::item:selected { background-color: #1a3040; color: #8ab; }
QMenu::separator { height: 1px; background: #1a1a1a; margin: 3px 6px; }

/* ── Progress ── */
QProgressBar {
    background-color: #141414;
    border: none;
    border-radius: 1px;
    text-align: center;
    height: 2px;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #305060;
    border-radius: 1px;
}

/* ── Checkbox ── */
QCheckBox { spacing: 6px; font-size: 11px; }
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    border: 1px solid #252525;
    border-radius: 2px;
    background-color: #111;
}
QCheckBox::indicator:checked {
    background-color: #305060;
    border-color: #406070;
}

/* ── Splitter ── */
QSplitter::handle { background-color: #141414; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:horizontal:hover { background-color: #253540; }

/* ── Tooltip ── */
QToolTip {
    background-color: #181818;
    color: #888;
    border: 1px solid #252525;
    padding: 4px 8px;
    border-radius: 2px;
    font-size: 11px;
}

/* ── Frame ── */
QFrame#separator {
    background-color: #1a1a1a;
    max-height: 1px;
}
"""