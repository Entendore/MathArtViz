# app.py - Main application
import sys
import logging
import time
import random
import scipy
import numpy as np
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTabWidget, QScrollArea, QMenuBar, QMenu, QStatusBar,
    QMessageBox, QFileDialog, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QElapsedTimer
from PySide6.QtGui import QAction, QKeySequence, QImage

from config import (
    APP_NAME, APP_VERSION, DARK_STYLE, EXPORT_FORMATS,
    MIN_RESOLUTION, SHORTCUTS
)
from generators import generate_frame, generate_full_resolution
from presets import FUNCTION_MAP
from ui_widgets import (
    ProgressBar, create_info_label, create_error_label,
    create_hover_label, PresetsTab, CustomTab, SettingsPanel,
    AnimationPanel, PostProcessPanel, GifExportPanel,
    TimelineScrubber, ButtonBar
)
from image_preview import ImagePreviewWidget
from gif_export import GifWorker, HAS_PIL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("MathArtStudio")


class MathArtApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}")
        self.resize(1440, 880)
        self.setMinimumSize(800, 500)

        self.time_value = 0.0
        self.is_generating = False
        self.auto_locked = False
        self.function_map = {k: v["func"] for k, v in FUNCTION_MAP.items()}
        self.function_params = {k: v["params"] for k, v in FUNCTION_MAP.items()}
        self.function_names = list(self.function_map.keys())
        self._pending_generate = False
        self._gif_worker: Optional[GifWorker] = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self._gen_timer = QTimer()
        self._gen_timer.setSingleShot(True)
        self._gen_timer.setInterval(20)
        self._gen_timer.timeout.connect(self._do_generate)

        self._create_menu_bar()
        self._create_widgets()
        self._connect_signals()
        self._setup_shortcuts()

        QTimer.singleShot(150, self.generate_image)
        logger.info(f"{APP_NAME} v{APP_VERSION} ready")

    # ── Menu ──
    def _create_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        mb = self.menu_bar

        file_m = QMenu("File", mb)
        self._act(file_m, "Save Image…", SHORTCUTS["save"], self.save_image)
        file_m.addSeparator()
        if HAS_PIL:
            self._act(file_m, "Export GIF…", SHORTCUTS["export_gif"], self._start_gif_export)
            file_m.addSeparator()
        self._act(file_m, "Exit", "Ctrl+Q", self.close)
        mb.addMenu(file_m)

        edit_m = QMenu("Edit", mb)
        self._act(edit_m, "Copy Formulas", SHORTCUTS["copy_formula"], self.copy_formulas)
        edit_m.addSeparator()
        self._act(edit_m, "Randomize", SHORTCUTS["random"], self.randomize_presets)
        self._act(edit_m, "Toggle Auto-Lock", SHORTCUTS["toggle_lock"],
                  lambda: self.button_bar.lock_btn.toggle())
        mb.addMenu(edit_m)

        view_m = QMenu("View", mb)
        self._act(view_m, "Fullscreen", SHORTCUTS["fullscreen"], self.toggle_fullscreen)
        view_m.addSeparator()
        self._act(view_m, "Zoom In", SHORTCUTS["zoom_in"], lambda: self.image_preview.zoomIn())
        self._act(view_m, "Zoom Out", SHORTCUTS["zoom_out"], lambda: self.image_preview.zoomOut())
        self._act(view_m, "Fit", SHORTCUTS["fit_to_window"], lambda: self.image_preview.fitToWindow())
        self._act(view_m, "1:1", "Ctrl+1", lambda: self.image_preview.zoomToActual())
        mb.addMenu(view_m)

        anim_m = QMenu("Animate", mb)
        self._act(anim_m, "Play/Pause", SHORTCUTS["animate_toggle"], self.toggle_animation)
        self._act(anim_m, "Step", SHORTCUTS["step"], self.step_animation)
        self._act(anim_m, "Reset", SHORTCUTS["reset_time"], self.reset_time)
        mb.addMenu(anim_m)

        help_m = QMenu("Help", mb)
        self._act(help_m, "About", "", self.show_about)
        self._act(help_m, "Shortcuts", "", self.show_shortcuts)
        mb.addMenu(help_m)

    def _act(self, menu, text, shortcut, cb):
        a = QAction(text, self)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        a.triggered.connect(cb)
        menu.addAction(a)

    # ── Widgets ──
    def _create_widgets(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.menu_bar)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        # Left panel
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(340)
        left_scroll.setMaximumWidth(500)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setSpacing(0)
        ll.setContentsMargins(10, 8, 10, 8)

        self.tabs = QTabWidget()
        self.tabs.setFixedHeight(320)
        self.tabs.documentMode = True
        self.presets_tab = PresetsTab(self)
        self.custom_tab = CustomTab(self)
        self.tabs.addTab(self.presets_tab, "Presets")
        self.tabs.addTab(self.custom_tab, "Custom")
        ll.addWidget(self.tabs)

        self.settings_panel = SettingsPanel()
        ll.addWidget(self.settings_panel)

        self.animation_panel = AnimationPanel()
        ll.addWidget(self.animation_panel)

        self.postprocess_panel = PostProcessPanel(self)
        ll.addWidget(self.postprocess_panel)

        self.gif_panel = GifExportPanel()
        if not HAS_PIL:
            self.gif_panel.setEnabled(False)
            self.gif_panel.setToolTip("pip install Pillow")
        ll.addWidget(self.gif_panel)

        self.button_bar = ButtonBar(self)
        ll.addWidget(self.button_bar)

        self.progress = ProgressBar()
        ll.addWidget(self.progress)

        ll.addStretch()
        left_scroll.setWidget(left)
        splitter.addWidget(left_scroll)

        # Right panel
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(4, 4, 4, 2)
        rl.setSpacing(2)

        self.image_preview = ImagePreviewWidget()
        self.image_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        rl.addWidget(self.image_preview, 1)

        self.timeline = TimelineScrubber()
        rl.addWidget(self.timeline)

        # Bottom status row
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        status_row.setContentsMargins(0, 2, 0, 0)

        self.hover_label = create_hover_label()

        self.error_label = create_error_label()
        self.error_label.setMaximumWidth(260)

        self.success_label = QLabel("")
        self.success_label.setObjectName("success_label")
        self.success_label.setMaximumWidth(120)

        self.info_label = create_info_label()

        status_row.addWidget(self.hover_label, 1)
        status_row.addWidget(self.error_label)
        status_row.addWidget(self.success_label)
        status_row.addWidget(self.info_label)
        rl.addLayout(status_row)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([420, 1000])

        root.addWidget(splitter, 1)

        self.status_bar = QStatusBar()
        root.addWidget(self.status_bar)

        self.setLayout(root)
        self._update_timeline_range()
        self.presets_tab.update_sliders()

    # ── Signals ──
    def _connect_signals(self):
        self.animation_panel.animate_btn.clicked.connect(self.toggle_animation)
        self.animation_panel.step_btn.clicked.connect(self.step_animation)
        self.animation_panel.reset_time_btn.clicked.connect(self.reset_time)
        self.animation_panel.speed_slider.valueChanged.connect(self._on_speed_changed)

        self.postprocess_panel.colormap_combo.currentTextChanged.connect(
            lambda: self._debounced_generate())
        for s in [self.postprocess_panel.brightness_slider,
                   self.postprocess_panel.contrast_slider,
                   self.postprocess_panel.saturation_slider,
                   self.postprocess_panel.gamma_slider]:
            s.valueChanged.connect(lambda v: self._debounced_generate())

        self.gif_panel.exportRequested.connect(self._start_gif_export)
        self.gif_panel.frames_spin.valueChanged.connect(self._update_timeline_range)

        self.timeline.timeChanged.connect(self._on_timeline_scrub)

        self.button_bar.generate_btn.clicked.connect(self.generate_image)
        self.button_bar.random_btn.clicked.connect(self.randomize_presets)
        self.button_bar.copy_btn.clicked.connect(self.copy_formulas)
        self.button_bar.save_btn.clicked.connect(self.save_image)
        self.button_bar.lock_btn.toggled.connect(self._on_lock_toggled)

        self.image_preview.hoverInfo.connect(self.hover_label.setText)

    def _setup_shortcuts(self):
        for sc, fn in [
            (SHORTCUTS["generate"], self.generate_image),
            (SHORTCUTS["validate"], self._validate_current_tab),
        ]:
            a = QAction(self)
            a.setShortcut(QKeySequence(sc))
            a.triggered.connect(fn)
            self.addAction(a)

    # ── Helpers ──
    def _debounced_generate(self):
        if self.auto_locked:
            return
        self._pending_generate = True
        if not self._gen_timer.isActive():
            self._gen_timer.start()

    def _do_generate(self):
        if self._pending_generate:
            self._pending_generate = False
            self.generate_image()

    def _on_speed_changed(self, v):
        self.animation_panel.speed_slider.label.setText(f"{int(v)}ms")
        if self.timer.isActive():
            self.timer.setInterval(int(v))

    def _on_lock_toggled(self, checked):
        self.auto_locked = checked
        btn = self.button_bar.lock_btn
        if checked:
            btn.setText("Locked")
            self.status_bar.showMessage("Auto-gen paused", 2000)
        else:
            btn.setText("Auto")
            self.status_bar.showMessage("Auto-gen on", 1500)
            self.generate_image()

    def _update_timeline_range(self):
        self.timeline.set_range(self.gif_panel.get_timeline_max_time())

    def _on_timeline_scrub(self, t):
        if self.timer.isActive():
            self.timer.stop()
            self.animation_panel.animate_btn.setChecked(False)
            self.animation_panel.animate_btn.setText("Play")
        self.time_value = t
        self._update_time_display()
        self.timeline.set_time(t)
        self.generate_image(True)

    def _validate_channel(self, text_edit, channel):
        from math_engine import math_engine
        expr = text_edit.toPlainText()
        valid, message = math_engine.validate_expression(expr)
        if valid:
            self.success_label.setText(f"{channel} ok")
            self.error_label.setText("")
            text_edit.setStyleSheet(
                "background-color:#0a0a0a;color:#508060;border:1px solid #2a4a3a;border-radius:2px;"
                "font-family:'JetBrains Mono','Consolas',monospace;font-size:12px;padding:4px 6px;")
        else:
            self.error_label.setText(f"{channel}: {message}")
            self.success_label.setText("")
            text_edit.setStyleSheet(
                "background-color:#0a0a0a;color:#a04040;border:1px solid #4a2a2a;border-radius:2px;"
                "font-family:'JetBrains Mono','Consolas',monospace;font-size:12px;padding:4px 6px;")
        QTimer.singleShot(3000, lambda: text_edit.setStyleSheet(""))

    def _validate_current_tab(self):
        if self.tabs.currentIndex() == 1:
            for ch, te in [("R", self.custom_tab.r_text),
                           ("G", self.custom_tab.g_text),
                           ("B", self.custom_tab.b_text)]:
                self._validate_channel(te, ch)

    # ── Generate ──
    def generate_image(self, force_full_res: bool = False):
        if self.is_generating:
            return
        self.is_generating = True
        self._pending_generate = False
        self._gen_timer.stop()
        self.error_label.setText("")
        self.success_label.setText("")
        self.progress.show_progress("…")
        QApplication.processEvents()

        elapsed = QElapsedTimer()
        elapsed.start()

        try:
            w = self.settings_panel.width_spin.value()
            h = self.settings_panel.height_spin.value()

            use_preview = (
                self.settings_panel.preview_check.isChecked()
                and not force_full_res
                and not self.timer.isActive()
            )
            if use_preview:
                w = max(MIN_RESOLUTION, w // 2)
                h = max(MIN_RESOLUTION, h // 2)

            QApplication.processEvents()

            img_array = generate_frame(self, w, h, self.time_value)
            self.image_preview.setImage(img_array)
            self.timeline.set_time(self.time_value)

            ms = elapsed.elapsed()
            mode = "Custom" if self.tabs.currentIndex() == 1 else "Preset"
            tag = "½" if use_preview else ""
            self.progress.hide_progress(f"{w}×{h}{tag} {ms:.0f}ms")
            self.info_label.setText(f"{mode} {w}×{h} {ms:.0f}ms")
            self.status_bar.showMessage(f"{w}×{h} in {ms:.0f}ms", 3000)

        except Exception as e:
            logger.error(f"Gen failed: {e}", exc_info=True)
            self.error_label.setText(str(e))
            self.progress.hide_progress("err")
        finally:
            self.is_generating = False

    def randomize_presets(self):
        self.presets_tab.randomize()
        self.custom_tab.randomize()
        from config import COLORMAPS
        self.postprocess_panel.colormap_combo.setCurrentIndex(
            random.randint(0, len(COLORMAPS) - 1))
        self.generate_image()

    def copy_formulas(self):
        if self.tabs.currentIndex() == 1:
            text = (f"R: {self.custom_tab.r_text.toPlainText()}\n"
                    f"G: {self.custom_tab.g_text.toPlainText()}\n"
                    f"B: {self.custom_tab.b_text.toPlainText()}")
        else:
            f = self.presets_tab.channel_selector.currentFunctions()
            text = f"R: {f['R']}\nG: {f['G']}\nB: {f['B']}"
        QApplication.clipboard().setText(text)
        self.status_bar.showMessage("Copied", 2000)

    def save_image(self):
        img_data = self.image_preview.getImageData()
        if not img_data:
            QMessageBox.warning(self, "No Image", "Generate an image first.")
            return
        if self.settings_panel.preview_check.isChecked():
            r = QMessageBox.question(
                self, "Resolution", "Generate full resolution?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if r == QMessageBox.Cancel:
                return
            if r == QMessageBox.Yes:
                self.progress.show_progress("…")
                QApplication.processEvents()
                try:
                    img_data = generate_full_resolution(self)
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
                    return

        filters = ";;".join(f"{n} (*.{ext})" for n, (ext, _) in EXPORT_FORMATS.items())
        path, _ = QFileDialog.getSaveFileName(
            self, "Save", f"art_{int(time.time())}.png", filters)
        if not path:
            return
        try:
            h, w = img_data.shape[:2]
            qimg = QImage(np.ascontiguousarray(img_data).data, w, h, 3 * w,
                          QImage.Format.Format_RGB888)
            ext = path.rsplit('.', 1)[-1].lower()
            quality = 100
            for _, (f, q) in EXPORT_FORMATS.items():
                if f == ext:
                    quality = q
                    break
            fmt = "JPEG" if ext in ('jpg', 'jpeg') else ext.upper()
            if not qimg.save(path, fmt, quality):
                raise RuntimeError("Save failed")
            self.status_bar.showMessage(f"Saved {path}", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ── Animation ──
    def toggle_animation(self):
        checked = self.animation_panel.animate_btn.isChecked()
        if checked:
            self.timer.start(int(self.animation_panel.speed_slider.value()))
            self.animation_panel.animate_btn.setText("Pause")
        else:
            self.timer.stop()
            self.animation_panel.animate_btn.setText("Play")

    def step_animation(self):
        self.time_value += self.animation_panel.timestep_slider.value()
        self._update_time_display()
        self.generate_image(True)

    def reset_time(self):
        self.time_value = 0.0
        self._update_time_display()
        self.timeline.set_time(0)
        self.generate_image()

    def update_animation(self):
        if self.is_generating:
            return
        self.time_value += self.animation_panel.timestep_slider.value()
        self._update_time_display()
        self.generate_image()

    def _update_time_display(self):
        self.animation_panel.time_label.setText(f"t = {self.time_value:.3f}")

    # ── GIF ──
    def _start_gif_export(self):
        if not HAS_PIL:
            QMessageBox.warning(self, "Missing", "pip install Pillow")
            return
        if self.timer.isActive():
            self.toggle_animation()

        path, _ = QFileDialog.getSaveFileName(
            self, "Export GIF", f"art_{int(time.time())}.gif", "GIF (*.gif)")
        if not path:
            return

        self.time_value = 0.0
        self._update_time_display()
        self.timeline.set_time(0)

        self._gif_worker = GifWorker(
            self, path,
            self.gif_panel.frames_spin.value(),
            self.gif_panel.fps_spin.value(),
            self.gif_panel.ping_pong_check.isChecked(),
            self.gif_panel.full_res_check.isChecked()
        )
        self.gif_panel.set_worker(self._gif_worker)
        self._gif_worker.progress.connect(self.gif_panel.update_progress)
        self._gif_worker.finished_ok.connect(self._on_gif_done)
        self._gif_worker.error.connect(self._on_gif_error)
        self._gif_worker.frame_generated.connect(self._on_gif_frame)
        self.gif_panel.show_exporting()
        self._gif_worker.start()
        self.status_bar.showMessage("Exporting…", 0)

    def _on_gif_frame(self, idx):
        total = self.gif_panel.frames_spin.value()
        if idx % max(1, total // 15) == 1 or idx == total:
            t = (idx - 1) * self.animation_panel.timestep_slider.value()
            self.time_value = t
            self._update_time_display()
            self.timeline.set_time(t)
            try:
                w = max(MIN_RESOLUTION, self.settings_panel.width_spin.value() // 2)
                h = max(MIN_RESOLUTION, self.settings_panel.height_spin.value() // 2)
                self.image_preview.setImage(generate_frame(self, w, h, t))
            except Exception:
                pass

    def _on_gif_done(self, msg):
        self.gif_panel.show_done(msg)
        self.status_bar.showMessage(msg, 6000)

    def _on_gif_error(self, msg):
        self.gif_panel.show_error(msg)
        self.status_bar.showMessage(f"GIF failed: {msg}", 4000)

    # ── Misc ──
    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def show_about(self):
        QMessageBox.about(self, "About",
                          f"<h2>{APP_NAME}</h2><p>v{APP_VERSION}</p>"
                          f"<p>Mathematical art generator.</p>")

    def show_shortcuts(self):
        rows = "".join(
            f"<tr><td style='padding:2px 12px 2px 0;color:#888;'>{a.replace('_',' ').title()}"
            f"</td><td style='color:#555;'><code>{s}</code></td></tr>"
            for a, s in SHORTCUTS.items())
        QMessageBox.information(self, "Shortcuts",
                                f"<table style='font-size:12px;'>{rows}</table>")

    def closeEvent(self, event):
        self.timer.stop()
        self._gen_timer.stop()
        if self._gif_worker and self._gif_worker.isRunning():
            self._gif_worker.abort()
            self._gif_worker.wait(2000)
        super().closeEvent(event)


if __name__ == "__main__":
    logger.info("=" * 40)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info("=" * 40)
    logger.info(f"Python {sys.version}")
    logger.info(f"NumPy {np.__version__}  SciPy {scipy.__version__}")
    logger.info(f"Pillow {'✓' if HAS_PIL else '✗'}")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)

    window = MathArtApp()
    window.show()
    sys.exit(app.exec())