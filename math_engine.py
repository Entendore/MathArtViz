# math_engine.py - Safe math evaluation engine
import logging
import numpy as np
import scipy.special

logger = logging.getLogger("MathArtStudio.MathEngine")

class MathEngine:
    _instance = None
    _safe_dict = None
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls); cls._instance._initialized = False
        return cls._instance
    def __init__(self):
        if not self._initialized: self._safe_dict = self._build_safe_dict(); self._initialized = True
    def _build_safe_dict(self):
        safe = {"__builtins__": {}}
        for alias, attr in {"sin": "sin", "cos": "cos", "tan": "tan", "arcsin": "arcsin", "arccos": "arccos", "arctan": "arctan", "arctan2": "arctan2", "sinh": "sinh", "cosh": "cosh", "tanh": "tanh", "arcsinh": "arcsinh", "arccosh": "arccosh", "arctanh": "arctanh", "exp": "exp", "exp2": "exp2", "log": "log", "log2": "log2", "log10": "log10", "log1p": "log1p", "expm1": "expm1", "sqrt": "sqrt", "square": "square", "power": "power", "pow": "power", "cbrt": "cbrt", "floor": "floor", "ceil": "ceil", "round": "round", "trunc": "trunc", "rint": "rint", "fix": "fix", "abs": "abs", "sign": "sign", "positive": "positive", "negative": "negative", "mod": "mod", "fmod": "fmod", "remainder": "remainder", "divmod": "divmod", "minimum": "minimum", "maximum": "maximum", "fmin": "fmin", "fmax": "fmax", "clip": "clip", "equal": "equal", "not_equal": "not_equal", "less": "less", "less_equal": "less_equal", "greater": "greater", "greater_equal": "greater_equal", "logical_and": "logical_and", "logical_or": "logical_or", "logical_not": "logical_not", "logical_xor": "logical_xor", "where": "where", "select": "select", "sum": "sum", "prod": "prod", "mean": "mean", "min": "min", "max": "max", "hypot": "hypot", "deg2rad": "deg2rad", "rad2deg": "rad2deg", "unwrap": "unwrap", "conj": "conj", "real": "real", "imag": "imag", "angle": "angle", "isnan": "isnan", "isinf": "isinf", "isfinite": "isfinite", "nan_to_num": "nan_to_num"}.items():
            if callable(getattr(np, attr, None)): safe[alias] = getattr(np, attr)
        for alias, attr in {"erf": "erf", "erfc": "erfc", "gamma": "gamma", "gammaln": "gammaln", "beta": "beta", "betaln": "betaln"}.items():
            if callable(getattr(scipy.special, attr, None)): safe[alias] = getattr(scipy.special, attr)
        safe.update({"np": np, "pi": np.pi, "e": np.e, "inf": np.inf, "nan": np.nan, "tau": np.pi * 2, "phi": (1 + np.sqrt(5)) / 2, "TWO_PI": np.pi * 2, "HALF_PI": np.pi / 2, "SQRT2": np.sqrt(2), "LN2": np.log(2), "LN10": np.log(10)})
        return safe
    def validate_expression(self, expr: str) -> tuple[bool, str]:
        if not expr or not expr.strip(): return False, "Expression is empty"
        for p in ['import', 'exec', 'eval', 'compile', 'open', '__import__', 'getattr', 'setattr', 'delattr', 'globals', 'locals', 'vars', 'dir', 'type', 'input', 'print', 'breakpoint', 'exit', 'quit']:
            if p in expr.lower(): return False, f"Forbidden keyword: '{p}'"
        try:
            tx, ty = np.array([0.5]), np.array([0.5])
            res = eval(expr, self._safe_dict, {"x": tx, "y": ty, "t": 0.0, "r": np.sqrt(tx**2 + ty**2), "theta": np.arctan2(ty, tx), "a": 1.0, "b": 1.0, "c": 1.0, "d": 0.0})
            return (True, "Valid") if isinstance(res, (int, float, np.ndarray)) else (False, f"Invalid result type: {type(res).__name__}")
        except SyntaxError as e: return False, f"Syntax error: {e}"
        except NameError as e: return False, f"Unknown variable: {e}"
        except Exception as e: return False, f"Error: {e}"
    def evaluate(self, expr: str, xv: np.ndarray, yv: np.ndarray, user_vars: dict, t_val: float) -> np.ndarray:
        local_dict = {"x": xv, "y": yv, "t": t_val, "r": np.sqrt(xv**2 + yv**2), "theta": np.arctan2(yv, xv), **user_vars}
        try:
            result = eval(expr, self._safe_dict, local_dict)
            if isinstance(result, (int, float)): result = np.full_like(xv, result)
            if isinstance(result, tuple): result = result[0]
            return np.clip(np.float64(np.nan_to_num(result, nan=0.0, posinf=1.0, neginf=-1.0)), -1.0, 1.0)
        except Exception as e:
            logger.error(f"Math Eval Error: {e}"); raise ValueError(f"Expression error: {e}")

math_engine = MathEngine()