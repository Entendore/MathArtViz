# image_preview.py - Image preview with zoom/pan/hover
import numpy as np
from typing import Optional
from PySide6.QtWidgets import QScrollArea, QLabel, QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QPoint, Signal
from PySide6.QtGui import QPixmap, QImage


class ImagePreviewWidget(QScrollArea):
    hoverInfo = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._img_data: Optional[np.ndarray] = None
        self._zoom_factor = 1.0
        self._fit_to_window = True
        self._dragging = False
        self._drag_start = QPoint()

        container = QWidget()
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setAlignment(Qt.AlignCenter)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(100, 100)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._set_placeholder()
        cl.addWidget(self.label)

        self.setWidget(container)
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea{border:none;background:#080808;}")
        self.setCursor(Qt.CrossCursor)

        self._rtimer = QTimer()
        self._rtimer.setSingleShot(True)
        self._rtimer.setInterval(80)
        self._rtimer.timeout.connect(self._update_display)
        self.setMouseTracking(True)

    def _set_placeholder(self):
        self.label.setText("")
        self.label.setStyleSheet("background:#080808;border:none;")
        self.label.setMinimumSize(100, 100)
        self.label.setMaximumSize(16777215, 16777215)

    def setImage(self, img_array: np.ndarray):
        self._img_data = (
            np.ascontiguousarray(img_array)
            if not img_array.flags['C_CONTIGUOUS'] else img_array.copy()
        )
        self._update_display()

    def _update_display(self):
        if self._img_data is None:
            return
        h, w = self._img_data.shape[:2]
        c = self._img_data.shape[2] if self._img_data.ndim == 3 else 3
        d = self._img_data[:, :, :3] if c >= 3 else np.stack([self._img_data] * 3, axis=2)
        qimg = QImage(d.data, w, h, 3 * w, QImage.Format.Format_RGB888)

        if self._fit_to_window:
            target = self.viewport().size()
            if target.width() < 10:
                target = self.label.minimumSize()
            pm = QPixmap.fromImage(qimg).scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            nw = max(1, int(w * self._zoom_factor))
            nh = max(1, int(h * self._zoom_factor))
            pm = QPixmap.fromImage(qimg).scaled(nw, nh, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.label.setStyleSheet("background:#080808;border:none;")
        self.label.setPixmap(pm)
        self.label.setMinimumSize(pm.size())
        self.label.setMaximumSize(pm.size())

    def zoomIn(self):
        self._fit_to_window = False
        self._zoom_factor = min(self._zoom_factor * 1.25, 20.0)
        self._update_display()

    def zoomOut(self):
        self._fit_to_window = False
        self._zoom_factor = max(self._zoom_factor / 1.25, 0.05)
        self._update_display()

    def fitToWindow(self):
        self._fit_to_window = True
        self._zoom_factor = 1.0
        self._set_placeholder()
        if self._img_data is not None:
            self._update_display()

    def zoomToActual(self):
        self._fit_to_window = False
        self._zoom_factor = 1.0
        self._update_display()

    def wheelEvent(self, event):
        (self.zoomIn() if event.angleDelta().y() > 0 else self.zoomOut())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() in (Qt.MiddleButton, Qt.RightButton):
            self._dragging = True
            self._drag_start = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self._dragging:
            d = pos - self._drag_start
            self._drag_start = pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - d.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - d.y())
            event.accept()
        else:
            info = self._hover(pos)
            self.hoverInfo.emit(info if info else "")
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() in (Qt.MiddleButton, Qt.RightButton):
            self._dragging = False
            self.setCursor(Qt.CrossCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.fitToWindow()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def leaveEvent(self, event):
        self.hoverInfo.emit("")
        super().leaveEvent(event)

    def _hover(self, wp):
        if not self._img_data or not self.label.pixmap():
            return None
        lp = self.label.mapFrom(self, wp)
        pm = self.label.pixmap()
        lr = self.label.rect()
        pr = pm.rect()
        xo = (lr.width() - pr.width()) // 2
        yo = (lr.height() - pr.height()) // 2
        px, py = lp.x() - xo, lp.y() - yo
        if px < 0 or py < 0 or px >= pr.width() or py >= pr.height():
            return None
        h, w = self._img_data.shape[:2]
        ox = max(0, min(w - 1, int(px * w / pr.width())))
        oy = max(0, min(h - 1, int(py * h / pr.height())))
        r, g, b = self._img_data[oy, ox, :3]
        z = "fit" if self._fit_to_window else f"{self._zoom_factor:.1f}x"
        return f"{ox},{oy}  {r},{g},{b}  {z}"

    def getImageData(self) -> Optional[np.ndarray]:
        return self._img_data.copy() if self._img_data is not None else None

    def clear(self):
        self._img_data = None
        self._set_placeholder()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._img_data is not None and self._fit_to_window:
            self._rtimer.start()