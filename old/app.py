import sys
import logging
import time
import numpy as np
import scipy.special

# -------------------------------
# LOGGING SETUP
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("MathArtStudio")

logger.info("="*50)
logger.info("Starting Math Art Studio")
logger.info("="*50)
logger.info(f"Python Version: {sys.version}")
logger.info(f"NumPy Version:  {np.__version__}")
logger.info(f"SciPy Version:  {scipy.__version__}")

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QDoubleSpinBox, QFileDialog, QGroupBox, QSlider, 
    QScrollArea, QTabWidget, QPlainTextEdit, QGridLayout, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage

logger.info("PySide6 GUI modules imported successfully.")

# -------------------------------
# SAFE MATH DICT BUILDER & VERIFIER
# -------------------------------
def build_and_verify_safe_dict():
    """Dynamically builds the safe dictionary and logs missing functions."""
    logger.info("Building SAFE_DICT from NumPy and SciPy...")
    safe = {"__builtins__": {}, "np": np}
    
    # Define expected mappings: "Alias": "Module_Attribute"
    numpy_mappings = {
        # Basic trig
        "sin": "sin", "cos": "cos", "tan": "tan",
        # Inverse trig
        "arcsin": "arcsin", "arccos": "arccos", "arctan": "arctan", "arctan2": "arctan2",
        # Hyperbolic
        "sinh": "sinh", "cosh": "cosh", "tanh": "tanh",
        "arcsinh": "arcsinh", "arccosh": "arccosh", "arctanh": "arctanh",
        # Exponential/Log
        "exp": "exp", "exp2": "exp2", "log": "log", "log2": "log2", "log10": "log10",
        "log1p": "log1p", "expm1": "expm1",
        # Powers
        "sqrt": "sqrt", "square": "square", "power": "power", "pow": "power", "cbrt": "cbrt",
        # Rounding
        "floor": "floor", "ceil": "ceil", "round": "round", "trunc": "trunc", "rint": "rint", "fix": "fix",
        # Absolute/Sign
        "abs": "abs", "sign": "sign", "positive": "positive", "negative": "negative",
        # Modulo
        "mod": "mod", "fmod": "fmod", "remainder": "remainder", "divmod": "divmod",
        # Min/Max
        "minimum": "minimum", "maximum": "maximum", "fmin": "fmin", "fmax": "fmax", "clip": "clip",
        # Comparison
        "equal": "equal", "not_equal": "not_equal", "less": "less", "less_equal": "less_equal",
        "greater": "greater", "greater_equal": "greater_equal",
        # Logical
        "logical_and": "logical_and", "logical_or": "logical_or", "logical_not": "logical_not", "logical_xor": "logical_xor",
        # Where/Select
        "where": "where", "select": "select",
        # Misc
        "sum": "sum", "prod": "prod", "mean": "mean", "min": "min", "max": "max",
        "hypot": "hypot", "deg2rad": "deg2rad", "rad2deg": "rad2deg", "unwrap": "unwrap"
    }
    
    scipy_mappings = {
        "erf": "erf", "erfc": "erfc", "gamma": "gamma", "gammaln": "gammaln"
    }
    
    missing_numpy = []
    for alias, attr in numpy_mappings.items():
        func = getattr(np, attr, None)
        if callable(func):
            safe[alias] = func
        else:
            missing_numpy.append(f"np.{attr}")
            logger.warning(f"Missing NumPy function: np.{attr} (Alias: {alias})")
            
    missing_scipy = []
    for alias, attr in scipy_mappings.items():
        func = getattr(scipy.special, attr, None)
        if callable(func):
            safe[alias] = func
        else:
            missing_scipy.append(f"scipy.special.{attr}")
            logger.warning(f"Missing SciPy function: scipy.special.{attr} (Alias: {alias})")

    # Constants
    safe["pi"] = np.pi
    safe["e"] = np.e
    safe["inf"] = np.inf
    safe["nan"] = np.nan
    safe["tau"] = np.pi * 2
    safe["phi"] = (1 + np.sqrt(5)) / 2

    if not missing_numpy and not missing_scipy:
        logger.info("Successfully imported and mapped ALL math functions.")
    else:
        logger.error(f"Failed to import - NumPy: {missing_numpy}, SciPy: {missing_scipy}")
        
    return safe

SAFE_DICT = build_and_verify_safe_dict()

# -------------------------------
# TRIG FUNCTION VALIDATION
# -------------------------------
def validate_trig_functions():
    """Actively tests trig functions with dummy arrays to ensure they are vectorized and working."""
    logger.info("Validating Trigonometric functions with test arrays...")
    test_x = np.array([0.5, 1.0])
    test_y = np.array([0.5, 1.0])
    
    trig_funcs = [
        'sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan', 'arctan2', 
        'sinh', 'cosh', 'tanh', 'arcsinh', 'arccosh', 'arctanh'
    ]
    
    all_passed = True
    for fname in trig_funcs:
        if fname not in SAFE_DICT or not callable(SAFE_DICT[fname]):
            logger.error(f"  [FAIL] {fname} is missing or not callable!")
            all_passed = False
            continue
            
        try:
            if fname == 'arctan2':
                result = SAFE_DICT[fname](test_x, test_y)
            else:
                result = SAFE_DICT[fname](test_x)
            
            if isinstance(result, np.ndarray) and result.shape == test_x.shape:
                logger.info(f"  [OK]   {fname}")
            else:
                logger.error(f"  [FAIL] {fname} did not return a valid numpy array.")
                all_passed = False
        except Exception as e:
            logger.error(f"  [FAIL] {fname} crashed during test: {e}")
            all_passed = False
            
    if all_passed:
        logger.info("All trigonometric functions validated successfully.")
    else:
        logger.error("Some trigonometric functions failed validation!")

validate_trig_functions()
logger.info("="*50)


# -------------------------------
# FUNCTION MAP (For Presets Tab)
# -------------------------------
# (Keeping previous definitions for brevity, they remain unchanged)
def mandelbrot_func(x, y, rng=None, params=None):
    c = (x + 1j * y) * params["zoom"] + complex(params["center_x"], params["center_y"])
    z = np.zeros_like(c, dtype=complex)
    img = np.zeros(c.shape, dtype=np.float64)
    max_iter = int(params["max_iter"])
    for _ in range(max_iter):
        mask = np.abs(z) <= 2
        z[mask] = z[mask]**2 + c[mask]
        img[mask] += 1
    return np.clip((img / max_iter) * 2 - 1, -1, 1) * params["amplitude"]

def julia_func(x, y, rng=None, params=None):
    c = complex(params["c_real"], params["c_imag"])
    z = (x + 1j * y) * params["zoom"]
    img = np.zeros(z.shape, dtype=np.float64)
    max_iter = int(params["max_iter"])
    for _ in range(max_iter):
        mask = np.abs(z) <= 2
        z[mask] = z[mask]**2 + c
        img[mask] += 1
    return np.clip((img / max_iter) * 2 - 1, -1, 1) * params["amplitude"]

def interference_func(x, y, rng=None, params=None):
    result = np.zeros_like(x)
    num_sources = int(params["num_sources"])
    for i in range(num_sources):
        angle = 2 * np.pi * i / num_sources + params["angle_offset"]
        sx, sy = params["radius"] * np.cos(angle), params["radius"] * np.sin(angle)
        dist = np.sqrt((x - sx)**2 + (y - sy)**2)
        result += np.sin(dist * params["frequency"] + params["phase"])
    return result / num_sources * params["amplitude"]

def spiral_func(x, y, rng=None, params=None):
    r = np.sqrt(x**2 + y**2) + 0.001
    theta = np.arctan2(y, x)
    spiral = np.sin(theta * params["arms"] + r * params["frequency"] + params["phase"])
    return spiral * params["amplitude"] * np.exp(-r * params["decay"])

def diamond_func(x, y, rng=None, params=None):
    pattern = np.sin((x + y) * params["frequency"] + params["phase"]) * \
              np.cos((x - y) * params["frequency"] * params["ratio"] + params["phase2"])
    return pattern * params["amplitude"]

def moire_func(x, y, rng=None, params=None):
    grid1 = np.sin(x * params["freq1"]) * np.sin(y * params["freq1"])
    grid2 = np.sin((x + params["offset_x"]) * params["freq2"]) * np.sin((y + params["offset_y"]) * params["freq2"])
    return (grid1 + grid2) * params["amplitude"] / 2

def wave_interference_func(x, y, rng=None, params=None):
    angle1, angle2, k = params["angle1"], params["angle2"], params["frequency"]
    wave1 = np.sin(k * (x * np.cos(angle1) + y * np.sin(angle1)) + params["phase1"])
    wave2 = np.sin(k * (x * np.cos(angle2) + y * np.sin(angle2)) + params["phase2"])
    return (wave1 + wave2) * params["amplitude"] / 2

def ripple_func(x, y, rng=None, params=None):
    result, num = np.zeros_like(x), int(params["sources"])
    for i in range(num):
        ox = params["spread"] * np.cos(2 * np.pi * i / num)
        oy = params["spread"] * np.sin(2 * np.pi * i / num)
        r = np.sqrt((x - ox)**2 + (y - oy)**2)
        result += np.sin(r * params["frequency"] - params["speed"] * 5) / (1 + r * params["damping"])
    return result * params["amplitude"]

def checkerboard_func(x, y, rng=None, params=None):
    cx = np.tanh(np.sin(x * params["freq_x"]) * params["sharpness"])
    cy = np.tanh(np.sin(y * params["freq_y"]) * params["sharpness"])
    return (cx * cy) * params["amplitude"]

def voronoi_approx_func(x, y, rng=None, params=None):
    num_points, scale = int(params["num_cells"]), params["scale"]
    min_dist = np.ones_like(x) * 100
    np.random.seed(42)
    for _ in range(num_points):
        px, py = np.random.uniform(-scale, scale), np.random.uniform(-scale, scale)
        min_dist = np.minimum(min_dist, np.sqrt((x - px)**2 + (y - py)**2))
    return np.clip(1.0 - min_dist * params["frequency"], -1, 1) * params["amplitude"]

FUNCTION_MAP = {
    "Sine Wave": {"func": lambda x, y, rng=None, params=None: np.sin(x*params["frequency"]+params["phase"])*params["amplitude"], "desc":"Sine wave along X-axis", "params":{"frequency":(1,50,10),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0)}},
    "Radial Wave": {"func": lambda x, y, rng=None, params=None: np.sin(np.sqrt(x**2+y**2)*params["frequency"]+params["phase"])*params["amplitude"], "desc":"Concentric radial waves", "params":{"frequency":(1,50,10),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0)}},
    "Plasma": {"func": lambda x, y, rng=None, params=None: (np.sin(x*params["freq1"]+params["phase1"])+np.sin(y*params["freq2"]+params["phase2"])+np.sin((x+y)*params["freq3"]+params["phase3"]))*params["amplitude"]/3.0, "desc":"Classic procedural plasma", "params":{"freq1":(1,50,5),"freq2":(1,50,10),"freq3":(1,50,15),"phase1":(0,6.28,0.0),"phase2":(0,6.28,0.0),"phase3":(0,6.28,0.0),"amplitude":(0.1,2.0,1.0)}},
    "Fractal (Mandelbrot)": {"func": mandelbrot_func, "desc":"True iterative Mandelbrot fractal", "params":{"max_iter":(5,150,30),"zoom":(0.5,5.0,1.5),"center_x":(-2.0,2.0,-0.5),"center_y":(-2.0,2.0,0.0),"amplitude":(0.1,2.0,1.0)}},
    "Fractal (Julia)": {"func": julia_func, "desc":"Julia set fractal", "params":{"max_iter":(5,150,30),"zoom":(0.5,3.0,1.0),"c_real":(-2.0,2.0,-0.7),"c_imag":(-2.0,2.0,0.27),"amplitude":(0.1,2.0,1.0)}},
    "Interference": {"func": interference_func, "desc":"Multi-source wave interference", "params":{"num_sources":(2,8,3),"frequency":(5,100,30),"radius":(0.1,2.0,0.5),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0),"angle_offset":(0,6.28,0.0)}},
    "Spiral": {"func": spiral_func, "desc":"Logarithmic spiral pattern", "params":{"arms":(1,10,3),"frequency":(5,50,15),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0),"decay":(0.0,5.0,0.5)}},
    "Diamond Wave": {"func": diamond_func, "desc":"Diamond/checkerboard pattern", "params":{"frequency":(1,30,8),"ratio":(0.1,3.0,1.0),"amplitude":(0.1,2.0,1.0),"phase":(0,6.28,0.0),"phase2":(0,6.28,0.0)}},
    "Moiré Pattern": {"func": moire_func, "desc":"Overlapping grid interference", "params":{"freq1":(5,50,20),"freq2":(5,50,21),"offset_x":(-1.0,1.0,0.1),"offset_y":(-1.0,1.0,0.1),"amplitude":(0.1,2.0,1.0)}},
    "Plane Wave": {"func": wave_interference_func, "desc":"Two crossing plane waves", "params":{"frequency":(5,80,20),"angle1":(0,6.28,0.0),"angle2":(0,6.28,1.57),"amplitude":(0.1,2.0,1.0),"phase1":(0,6.28,0.0),"phase2":(0,6.28,0.0)}},
    "Water Ripple": {"func": ripple_func, "desc":"Multiple water ripple sources", "params":{"sources":(1,6,2),"frequency":(10,80,30),"spread":(0.2,1.5,0.5),"speed":(0.1,3.0,1.0),"damping":(0.1,5.0,1.0),"amplitude":(0.1,2.0,1.0)}},
    "Smooth Checker": {"func": checkerboard_func, "desc":"Smooth-edged checkerboard", "params":{"freq_x":(1,20,4),"freq_y":(1,20,4),"sharpness":(1,20,5),"amplitude":(0.1,2.0,1.0)}},
    "Voronoi Approx": {"func": voronoi_approx_func, "desc":"Distance-field Voronoi cells", "params":{"num_cells":(5,50,15),"scale":(0.5,3.0,1.5),"frequency":(1,10,3),"amplitude":(0.1,2.0,1.0)}}
}

# (Using a subset of presets here to keep code size manageable, you can copy all from previous)
FORMULA_PRESETS = {
    "Psychedelic Swirl": {"R": "sin(x*10*a + t) * cos(y*10*b + t)", "G": "cos(sqrt(x**2 + y**2)*15*c - t)", "B": "sin(atan2(y, x)*5*d + t)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0}},
    "Electric Storm": {"R": "sin(x*x*a*20 + y*y*b*20) * cos(t)", "G": "cos(x*y*20*c + t*2)", "B": "sin(sqrt(abs(x*a) + abs(y*b))*15 - t)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Black Hole": {"R": "sin(1/(sqrt(x**2+y**2)*a+0.05) - t*2) * exp(-sqrt(x**2+y**2))", "G": "cos(atan2(y,x)*5 + 1/(sqrt(x**2+y**2)*a+0.05) - t)", "B": "sin(1/(sqrt(x**2+y**2)*a+0.05) + t*2) * exp(-sqrt(x**2+y**2)*0.5)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Scipy Error Function": {"R": "erf(x*5*a + t) * exp(-y**2*5)", "G": "erf(y*5*b - t) * exp(-x**2*5)", "B": "erf(sqrt(x**2+y**2)*5*c - t*2)", "vars": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}},
    "Hyperbolic Warp": {"R": "tanh(sin(x*10*a + t)*3)", "G": "sinh(cos(y*10*b - t)*0.5)", "B": "cosh(sqrt(x**2+y**2)*5*c) - 1", "vars": {"a": 1.0, "b": 1.0, "c": 0.5, "d": 0.0}}
}

COLORMAPS = {
    "None (RGB)": None, "Grayscale": "grayscale", "Sepia": "sepia", "Thermal": "thermal",
    "Ocean": "ocean", "Neon": "neon", "Inverted": "inverted", "Vintage": "vintage", "Cyberpunk": "cyberpunk"
}

def apply_colormap(img_array, colormap_name):
    if not colormap_name or colormap_name == "None (RGB)": return img_array
    img = img_array.astype(np.float32) / 255.0
    cmap_effects = {
        "grayscale": np.stack([np.mean(img, axis=2)]*3, axis=2),
        "sepia": np.stack([img[:,:,0]*0.393+img[:,:,1]*0.769+img[:,:,2]*0.189, img[:,:,0]*0.349+img[:,:,1]*0.686+img[:,:,2]*0.168, img[:,:,0]*0.272+img[:,:,1]*0.534+img[:,:,2]*0.131], axis=2),
        "thermal": np.stack([np.clip(np.mean(img, axis=2)*3, 0, 1), np.clip(np.mean(img, axis=2)*3-1, 0, 1), np.clip(np.mean(img, axis=2)*3-2, 0, 1)], axis=2),
        "ocean": np.stack([np.clip(np.mean(img, axis=2)*0.2, 0, 1), np.clip(np.mean(img, axis=2)*0.5+0.2, 0, 1), np.clip(np.mean(img, axis=2)*0.8+0.2, 0, 1)], axis=2),
        "neon": np.stack([np.clip(img[:,:,0]*1.5, 0, 1), np.clip(img[:,:,1]*0.5+0.5, 0, 1), np.clip(img[:,:,2]*1.5, 0, 1)], axis=2),
        "inverted": 1.0 - img,
        "vintage": np.stack([img[:,:,0]*0.6+0.2, img[:,:,1]*0.5+0.15, img[:,:,2]*0.4+0.1], axis=2),
        "cyberpunk": np.stack([np.clip(img[:,:,0]*1.5+img[:,:,2]*0.3, 0, 1), img[:,:,1]*0.3, np.clip(img[:,:,2]*1.8+img[:,:,0]*0.2, 0, 1)], axis=2)
    }
    return np.clip(cmap_effects.get(colormap_name, img) * 255, 0, 255).astype(np.uint8)

def eval_math_expr(expr, xv, yv, user_vars, t_val):
    local_dict = {"x": xv, "y": yv, "t": t_val, "r": np.sqrt(xv**2 + yv**2), "theta": np.arctan2(yv, xv), "TWO_PI": np.pi * 2, **user_vars}
    try:
        result = eval(expr, SAFE_DICT, local_dict)
        if isinstance(result, (int, float)): result = np.full_like(xv, result)
        if isinstance(result, tuple): result = result[0] 
        return np.clip(np.float64(result), -1.0, 1.0)
    except Exception as e:
        logger.error(f"Math Eval Error: {e} | Expression: {expr}")
        raise ValueError(f"Error: {e}")

# -------------------------------
# DARK THEME & APP
# -------------------------------
DARK_STYLE = """
QWidget { background-color: #1e1e1e; color: #d4d4d4; font-size: 13px; }
QGroupBox { border: 1px solid #444; border-radius: 5px; margin-top: 10px; padding-top: 15px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
QPushButton { background-color: #007acc; color: white; border: none; border-radius: 4px; padding: 8px 16px; font-weight: bold; }
QPushButton:hover { background-color: #005f9e; } QPushButton:checked { background-color: #d32f2f; }
QPushButton#random_btn { background-color: #7b2d8e; } QPushButton#random_btn:hover { background-color: #5c1d6e; }
QPushButton#step_btn { background-color: #2d7b4f; } QPushButton#reset_btn { background-color: #7b5c2d; }
QComboBox, QSpinBox, QDoubleSpinBox { background-color: #2d2d2d; border: 1px solid #444; border-radius: 3px; padding: 4px; }
QSlider::groove:horizontal { height: 6px; background: #444; border-radius: 3px; }
QSlider::handle:horizontal { background: #007acc; width: 14px; margin: -4px 0; border-radius: 7px; }
QScrollArea, QTabWidget::pane { border: none; }
QTabBar::tab { background: #2d2d2d; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px;}
QTabBar::tab:selected { background: #007acc; color: white; }
QPlainTextEdit { background-color: #111; color: #4ec9b0; border: 1px solid #444; border-radius: 3px; font-family: Consolas, monospace; font-size: 14px; padding: 5px;}
QLabel#error_label { color: #ff5555; font-weight: bold; } QLabel#info_label { color: #888; font-size: 11px; }
"""

class MathArtApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Math Art Studio (SciPy + Logging)")
        self.resize(1400, 900)
        self.function_map = {k: v["func"] for k, v in FUNCTION_MAP.items()}
        self.function_params = {k: v["params"] for k, v in FUNCTION_MAP.items()}
        self.function_names = list(self.function_map.keys())
        self.time_value = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.preset_sliders = {}
        self.custom_sliders = {}
        self._img_data = None
        self._img_pixmap = None
        self.create_widgets()
        self.generate_image()

    def create_widgets(self):
        main_layout = QHBoxLayout(); main_layout.setContentsMargins(10, 10, 10, 10); main_layout.setSpacing(10)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setMaximumWidth(520); scroll.setMinimumWidth(420)
        control_widget = QWidget(); control_layout = QVBoxLayout(control_widget); control_layout.setSpacing(10)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_presets_tab(), "🎨 Presets")
        self.tabs.addTab(self.create_custom_tab(), "✏️ Custom Math")
        control_layout.addWidget(self.tabs)
        control_layout.addWidget(self.create_settings_group())
        control_layout.addWidget(self.create_animation_group())
        control_layout.addWidget(self.create_postprocess_group())
        control_layout.addLayout(self.create_buttons())
        control_layout.addStretch()
        scroll.setWidget(control_widget); main_layout.addWidget(scroll)

        right_layout = QVBoxLayout()
        self.error_label = QLabel(""); self.error_label.setObjectName("error_label"); self.error_label.setWordWrap(True); self.error_label.setMaximumHeight(40)
        self.img_label = QLabel("Generating..."); self.img_label.setAlignment(Qt.AlignCenter); self.img_label.setStyleSheet("background-color: #111; border: 1px solid #333; border-radius: 5px;"); self.img_label.setMinimumSize(512, 512); self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.info_label = QLabel("Ready"); self.info_label.setObjectName("info_label"); self.info_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.img_label, 1); right_layout.addWidget(self.error_label); right_layout.addWidget(self.info_label)
        main_layout.addLayout(right_layout, 1)
        self.setLayout(main_layout); self.update_preset_sliders()

    def create_presets_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        rgb_group = QGroupBox("RGB Channels"); rgb_layout = QGridLayout()
        self.r_combo = QComboBox(); self.r_combo.addItems(self.function_names)
        self.g_combo = QComboBox(); self.g_combo.addItems(self.function_names)
        self.b_combo = QComboBox(); self.b_combo.addItems(self.function_names)
        self.r_combo.currentTextChanged.connect(self.update_preset_sliders); self.g_combo.currentTextChanged.connect(self.update_preset_sliders); self.b_combo.currentTextChanged.connect(self.update_preset_sliders)
        rgb_layout.addWidget(QLabel("Red:"), 0, 0); rgb_layout.addWidget(self.r_combo, 0, 1)
        rgb_layout.addWidget(QLabel("Green:"), 1, 0); rgb_layout.addWidget(self.g_combo, 1, 1)
        rgb_layout.addWidget(QLabel("Blue:"), 2, 0); rgb_layout.addWidget(self.b_combo, 2, 1)
        rgb_group.setLayout(rgb_layout); layout.addWidget(rgb_group)
        self.preset_slider_group = QGroupBox("Parameters"); self.preset_slider_layout = QVBoxLayout(); self.preset_slider_group.setLayout(self.preset_slider_layout); layout.addWidget(self.preset_slider_group)
        return tab

    def update_preset_sliders(self):
        while self.preset_slider_layout.count():
            item = self.preset_slider_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()
        self.preset_sliders.clear()
        for channel, combo in [("R", self.r_combo), ("G", self.g_combo), ("B", self.b_combo)]:
            func_name = combo.currentText(); params = self.function_params[func_name]; desc = FUNCTION_MAP[func_name]["desc"]
            self.preset_slider_layout.addWidget(QLabel(f"<b>-- {channel} Channel: {func_name} --</b>"))
            self.preset_slider_layout.addWidget(QLabel(f"<i>{desc}</i>"))
            for name, (minv, maxv, default) in params.items():
                slider, label = self._add_dynamic_slider(self.preset_slider_layout, name, minv, maxv, default)
                self.preset_sliders[f"{channel}_{name}"] = (slider, minv, maxv)
        self.preset_slider_layout.addStretch()

    def create_custom_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        preset_layout = QHBoxLayout(); preset_layout.addWidget(QLabel("Formula Preset:"))
        self.formula_preset_combo = QComboBox(); self.formula_preset_combo.addItem("-- Custom --")
        for name in FORMULA_PRESETS: self.formula_preset_combo.addItem(name)
        self.formula_preset_combo.currentTextChanged.connect(self.load_formula_preset)
        preset_layout.addWidget(self.formula_preset_combo, 1); layout.addLayout(preset_layout)
        
        self.r_text = QPlainTextEdit("sin(x*10*a + t)"); self.g_text = QPlainTextEdit("cos(y*10*b + t)"); self.b_text = QPlainTextEdit("sin(sqrt(x**2 + y**2)*15*c - t)")
        for name, text_edit in [("Red Channel (R)", self.r_text), ("Green Channel (G)", self.g_text), ("Blue Channel (B)", self.b_text)]:
            grp = QGroupBox(name); grp_layout = QVBoxLayout(); grp_layout.addWidget(text_edit); text_edit.setMaximumHeight(65); grp.setLayout(grp_layout); layout.addWidget(grp)

        var_group = QGroupBox("User Variables (a, b, c, d)"); var_layout = QGridLayout(); self.custom_sliders = {}
        for i, (var, default) in enumerate({"a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0}.items()):
            slider, label = self._add_dynamic_slider(var_layout, var, -5.0, 5.0, default, is_row=True, row=i)
            self.custom_sliders[var] = (slider, -5.0, 5.0)
        var_group.setLayout(var_layout); layout.addWidget(var_group)
        
        help_grp = QGroupBox("Available Functions")
        help_layout = QVBoxLayout()
        help_layout.addWidget(QLabel("<b>Trig/Exp:</b> sin, cos, tan, arcsin, arccos, arctan, arctan2, sinh, cosh, tanh, exp, log<br><b>SciPy:</b> erf, erfc, gamma, gammaln<br><b>Vars:</b> x, y, r, theta, t, a, b, c, d, pi, e, phi"))
        help_grp.setLayout(help_layout); layout.addWidget(help_grp)
        return tab

    def load_formula_preset(self, text):
        if text == "-- Custom --": return
        if text in FORMULA_PRESETS:
            preset = FORMULA_PRESETS[text]
            self.r_text.setPlainText(preset["R"]); self.g_text.setPlainText(preset["G"]); self.b_text.setPlainText(preset["B"])
            if "vars" in preset:
                for var_name, value in preset["vars"].items():
                    if var_name in self.custom_sliders:
                        slider, minv, maxv = self.custom_sliders[var_name]
                        slider.setValue(int((value - minv) / (maxv - minv) * 10000) if maxv != minv else 0)

    def _add_dynamic_slider(self, layout, name, minv, maxv, default, is_row=False, row=0):
        label = QLabel(f"{name}: {default:.3f}"); label.setMinimumWidth(100)
        slider = QSlider(Qt.Horizontal); slider.setMinimum(0); slider.setMaximum(10000)
        slider.setValue(int((default - minv) / (maxv - minv) * 10000) if maxv != minv else 0)
        slider.valueChanged.connect(lambda val, l=label, n=name, mn=minv, mx=maxv: l.setText(f"{n}: {mn + (mx - mn) * val / 10000:.3f}"))
        if is_row: layout.addWidget(label, row, 0); layout.addWidget(slider, row, 1)
        else: h_layout = QHBoxLayout(); h_layout.addWidget(label); h_layout.addWidget(slider, 1); layout.addLayout(h_layout)
        return slider, label

    def create_settings_group(self):
        grp = QGroupBox("General Settings"); layout = QGridLayout()
        self.width_spin = self._make_spin(QSpinBox, 32, 4096, 512); self.height_spin = self._make_spin(QSpinBox, 32, 4096, 512); self.scale_spin = self._make_spin(QDoubleSpinBox, 0.1, 20.0, 1.0, 0.1)
        layout.addWidget(QLabel("Width:"), 0, 0); layout.addWidget(self.width_spin, 0, 1)
        layout.addWidget(QLabel("Height:"), 1, 0); layout.addWidget(self.height_spin, 1, 1)
        layout.addWidget(QLabel("Scale:"), 2, 0); layout.addWidget(self.scale_spin, 2, 1)
        grp.setLayout(layout); return grp

    def create_animation_group(self):
        grp = QGroupBox("Animation"); layout = QVBoxLayout(); btn_layout = QHBoxLayout()
        self.animate_btn = QPushButton("▶ Animate"); self.animate_btn.setCheckable(True); self.animate_btn.clicked.connect(self.toggle_animation)
        self.step_btn = QPushButton("⏭ Step"); self.step_btn.setObjectName("step_btn"); self.step_btn.clicked.connect(self.step_animation)
        self.reset_time_btn = QPushButton("⏮ Reset t"); self.reset_time_btn.setObjectName("reset_btn"); self.reset_time_btn.clicked.connect(self.reset_time)
        btn_layout.addWidget(self.animate_btn); btn_layout.addWidget(self.step_btn); btn_layout.addWidget(self.reset_time_btn); layout.addLayout(btn_layout)
        speed_layout = QHBoxLayout(); self.speed_slider = QSlider(Qt.Horizontal); self.speed_slider.setRange(1, 100); self.speed_slider.setValue(50)
        self.speed_label = QLabel("Speed: 50ms"); self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(f"Speed: {v}ms"))
        speed_layout.addWidget(self.speed_label); speed_layout.addWidget(self.speed_slider); layout.addLayout(speed_layout)
        self.time_display = QLabel("t = 0.000"); self.time_display.setStyleSheet("color: #aaa; font-family: monospace;"); layout.addWidget(self.time_display)
        grp.setLayout(layout); return grp

    def create_postprocess_group(self):
        grp = QGroupBox("Post-Processing"); layout = QGridLayout()
        layout.addWidget(QLabel("Color Map:"), 0, 0); self.colormap_combo = QComboBox(); self.colormap_combo.addItems(COLORMAPS.keys()); self.colormap_combo.currentTextChanged.connect(lambda: self.generate_image()); layout.addWidget(self.colormap_combo, 0, 1)
        self.brightness_slider = QSlider(Qt.Horizontal); self.brightness_slider.setRange(50, 200); self.brightness_slider.setValue(100); self.brightness_label = QLabel("Bright: 100%"); self.brightness_slider.valueChanged.connect(lambda v: (self.brightness_label.setText(f"Bright: {v}%"), self.generate_image())[1])
        self.contrast_slider = QSlider(Qt.Horizontal); self.contrast_slider.setRange(50, 200); self.contrast_slider.setValue(100); self.contrast_label = QLabel("Contrast: 100%"); self.contrast_slider.valueChanged.connect(lambda v: (self.contrast_label.setText(f"Contrast: {v}%"), self.generate_image())[1])
        layout.addWidget(self.brightness_label, 1, 0); layout.addWidget(self.brightness_slider, 1, 1)
        layout.addWidget(self.contrast_label, 2, 0); layout.addWidget(self.contrast_slider, 2, 1)
        grp.setLayout(layout); return grp

    def create_buttons(self):
        layout = QHBoxLayout()
        self.generate_btn = QPushButton("⚡ Generate"); self.generate_btn.clicked.connect(self.generate_image)
        self.random_btn = QPushButton("🎲 Random"); self.random_btn.setObjectName("random_btn"); self.random_btn.clicked.connect(self.randomize_presets)
        self.save_btn = QPushButton("💾 Save"); self.save_btn.clicked.connect(self.save_image)
        layout.addWidget(self.generate_btn); layout.addWidget(self.random_btn); layout.addWidget(self.save_btn)
        return layout

    def _make_spin(self, spin_type, min_val, max_val, default, step=1):
        spin = spin_type(); spin.setRange(min_val, max_val); spin.setValue(default)
        if isinstance(spin, QDoubleSpinBox): spin.setSingleStep(step)
        return spin

    def randomize_presets(self):
        import random
        for combo in [self.r_combo, self.g_combo, self.b_combo]: combo.setCurrentIndex(random.randint(0, len(self.function_names) - 1))
        for key, (slider, minv, maxv) in self.preset_sliders.items(): slider.setValue(random.randint(0, 10000))
        for name, (slider, minv, maxv) in self.custom_sliders.items(): slider.setValue(random.randint(0, 10000))
        self.generate_image()

    def generate_image(self):
        self.error_label.setText("")
        start_time = time.time()
        try:
            width, height, scale = self.width_spin.value(), self.height_spin.value(), self.scale_spin.value()
            logger.info(f"Generating Image: {width}x{height} | Scale: {scale} | t: {self.time_value:.3f}")
            
            x, y = np.linspace(-1, 1, width) * scale, np.linspace(-1, 1, height) * scale
            xv, yv = np.meshgrid(x, y)

            is_custom = self.tabs.currentIndex() == 1
            img_array = self._generate_custom(xv, yv) if is_custom else self._generate_presets(xv, yv)
                
            brightness, contrast = self.brightness_slider.value() / 100.0, self.contrast_slider.value() / 100.0
            img_array = (img_array.astype(np.float32) * brightness).clip(0, 255)
            if contrast != 1.0: img_array = ((img_array - 128) * contrast + 128).clip(0, 255)
            
            self.display_image(apply_colormap(img_array.astype(np.uint8), self.colormap_combo.currentText()))
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Generation Successful in {elapsed:.2f} ms")
            self.info_label.setText(f"Generated: {width}×{height} | {elapsed:.1f}ms | t = {self.time_value:.3f}")
        except Exception as e:
            logger.error(f"Generation Failed: {str(e)}")
            self.error_label.setText(str(e))

    def _generate_presets(self, xv, yv):
        funcs = {"R": self.function_map[self.r_combo.currentText()], "G": self.function_map[self.g_combo.currentText()], "B": self.function_map[self.b_combo.currentText()]}
        channels = []
        for ch, func in funcs.items():
            params = {k.split('_', 1)[1]: v[0].value()/10000 * (v[2]-v[1]) + v[1] for k, v in self.preset_sliders.items() if k.startswith(f"{ch}_")}
            channels.append(np.clip((func(xv, yv, None, params) + 1) * 127.5, 0, 255).astype(np.uint8))
        return np.stack(channels, axis=2)

    def _generate_custom(self, xv, yv):
        user_vars = {name: minv + (maxv - minv) * slider.value() / 10000 for name, (slider, minv, maxv) in self.custom_sliders.items()}
        channels = []
        for expr in [self.r_text.toPlainText(), self.g_text.toPlainText(), self.b_text.toPlainText()]:
            if not expr.strip(): channels.append(np.zeros(xv.shape, dtype=np.uint8))
            else: channels.append(np.clip((eval_math_expr(expr, xv, yv, user_vars, self.time_value) + 1) * 127.5, 0, 255).astype(np.uint8))
        return np.stack(channels, axis=2)

    def display_image(self, img_array):
        self._img_data = img_array.copy()
        h, w, c = self._img_data.shape
        qimg = QImage(self._img_data.data, w, h, 3 * w, QImage.Format.Format_RGB888)
        self._img_pixmap = QPixmap.fromImage(qimg).scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setPixmap(self._img_pixmap)

    def save_image(self):
        if self._img_data is None: return QMessageBox.warning(self, "No Image", "Generate an image first!")
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "math_art.png", "PNG (*.png);;JPEG (*.jpg)")
        if file_path: 
            h, w, c = self._img_data.shape
            QImage(self._img_data.data, w, h, 3 * w, QImage.Format.Format_RGB888).save(file_path)
            logger.info(f"Image saved to {file_path}")

    def toggle_animation(self, checked):
        if checked: self.timer.start(self.speed_slider.value()); self.animate_btn.setText("⏸ Stop"); logger.info("Animation Started")
        else: self.timer.stop(); self.animate_btn.setText("▶ Animate"); logger.info("Animation Stopped")

    def step_animation(self):
        self.time_value += 0.05; self.time_display.setText(f"t = {self.time_value:.3f}"); self.generate_image()

    def reset_time(self):
        self.time_value = 0.0; self.time_display.setText(f"t = {self.time_value:.3f}"); self.generate_image()

    def update_animation(self):
        self.time_value += 0.05; self.time_display.setText(f"t = {self.time_value:.3f}"); self.generate_image()
        if self.timer.isActive(): self.timer.setInterval(self.speed_slider.value())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._img_data is not None:
            h, w, c = self._img_data.shape
            self._img_pixmap = QPixmap.fromImage(QImage(self._img_data.data, w, h, 3 * w, QImage.Format.Format_RGB888)).scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_label.setPixmap(self._img_pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)
    window = MathArtApp()
    logger.info("Launching GUI...")
    window.show()
    sys.exit(app.exec())