# ui_components.py - Reusable UI components and helper widgets

import logging
from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSlider, QGridLayout, QSizePolicy, QProgressBar, QComboBox
)
from PySide6.QtCore import Qt, Signal
from config import SLIDER_PRECISION

logger = logging.getLogger("MathArtStudio.UI")


class LabeledSlider(QWidget):
    """A slider with a label showing the current value."""
    
    valueChanged = Signal(float)
    
    def __init__(
        self,
        name: str,
        min_val: float,
        max_val: float,
        default_val: float,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.precision = 3
        self._name = name
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)
        
        self.label = QLabel(f"{name}: {default_val:.{self.precision}f}")
        self.label.setMinimumWidth(120)
        self.label.setToolTip(f"{name} range: [{min_val}, {max_val}]")
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(SLIDER_PRECISION)
        self.slider.setValue(self._float_to_slider(default_val))
        self.slider.setToolTip(f"Range: {min_val:.3f} to {max_val:.3f}")
        
        self.slider.valueChanged.connect(self._on_slider_changed)
        
        layout.addWidget(self.label)
        layout.addWidget(self.slider, 1)
    
    def _float_to_slider(self, value: float) -> int:
        """Convert float value to slider integer."""
        if self.max_val == self.min_val:
            return 0
        clamped = max(self.min_val, min(self.max_val, value))
        return int((clamped - self.min_val) / (self.max_val - self.min_val) * SLIDER_PRECISION)
    
    def _slider_to_float(self, slider_val: int) -> float:
        """Convert slider integer to float value."""
        return self.min_val + (self.max_val - self.min_val) * slider_val / SLIDER_PRECISION
    
    def _on_slider_changed(self, slider_val: int):
        """Handle slider value change."""
        float_val = self._slider_to_float(slider_val)
        self.label.setText(f"{self._name}: {float_val:.{self.precision}f}")
        self.valueChanged.emit(float_val)
    
    def value(self) -> float:
        """Get current value as float."""
        return self._slider_to_float(self.slider.value())
    
    def setValue(self, value: float):
        """Set value from float."""
        clamped = max(self.min_val, min(self.max_val, value))
        self.slider.blockSignals(True)
        self.slider.setValue(self._float_to_slider(clamped))
        self.slider.blockSignals(False)
        self.label.setText(f"{self._name}: {clamped:.{self.precision}f}")
    
    def setEnabled(self, enabled: bool):
        """Enable or disable the slider."""
        self.slider.setEnabled(enabled)
        self.label.setEnabled(enabled)


class ProgressBar(QWidget):
    """Progress indicator for image generation."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.hide()
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        
        layout.addWidget(self.status_label, 1)
        layout.addWidget(self.progress_bar, 1)
    
    def show_progress(self, message: str = "Generating..."):
        """Show progress bar with message."""
        self.status_label.setText(message)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
    
    def update_progress(self, value: int, message: str = ""):
        """Update progress value."""
        self.progress_bar.setValue(min(100, max(0, value)))
        if message:
            self.status_label.setText(message)
    
    def hide_progress(self, message: str = ""):
        """Hide progress bar."""
        self.progress_bar.hide()
        self.status_label.setText(message)
    
    def set_status(self, message: str):
        """Set status message only."""
        self.status_label.setText(message)


class ImageButton(QPushButton):
    """A button with icon-like styling for actions."""
    
    def __init__(
        self,
        text: str,
        tooltip: str = "",
        object_name: str = "",
        parent: Optional[QWidget] = None
    ):
        super().__init__(text, parent)
        self.setToolTip(tooltip)
        if object_name:
            self.setObjectName(object_name)
        self.setMinimumHeight(30)


class ChannelSelector(QWidget):
    """Widget for selecting RGB channel functions."""
    
    selectionChanged = Signal()
    
    def __init__(
        self,
        function_names: list,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.function_names = function_names
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self.combos = {}
        labels = [("R", "Red:", "#ff6666"), ("G", "Green:", "#66ff66"), ("B", "Blue:", "#6666ff")]
        
        for row, (key, label_text, color) in enumerate(labels):
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {color}; font-weight: bold;")
            label.setMinimumWidth(50)
            
            combo = QComboBox()
            combo.addItems(self.function_names)
            combo.currentTextChanged.connect(self.selectionChanged.emit)
            
            layout.addWidget(label, row, 0)
            layout.addWidget(combo, row, 1)
            self.combos[key] = combo
    
    def currentFunctions(self) -> Dict[str, str]:
        """Get current selected functions for each channel."""
        return {key: combo.currentText() for key, combo in self.combos.items()}
    
    def setFunction(self, channel: str, name: str):
        """Set a specific channel's function."""
        if channel in self.combos:
            idx = self.combos[channel].findText(name)
            if idx >= 0:
                self.combos[channel].setCurrentIndex(idx)
    
    def randomize(self):
        """Randomize all channel selections."""
        import random
        for combo in self.combos.values():
            combo.setCurrentIndex(random.randint(0, len(self.function_names) - 1))


def create_info_label() -> QLabel:
    """Create a styled info label."""
    label = QLabel("Ready")
    label.setObjectName("info_label")
    label.setAlignment(Qt.AlignCenter)
    label.setWordWrap(True)
    return label


def create_error_label() -> QLabel:
    """Create a styled error label."""
    label = QLabel("")
    label.setObjectName("error_label")
    label.setWordWrap(True)
    label.setMaximumHeight(60)
    return label


def create_time_label() -> QLabel:
    """Create a styled time display label."""
    label = QLabel("t = 0.000")
    label.setObjectName("time_label")
    label.setAlignment(Qt.AlignCenter)
    return label