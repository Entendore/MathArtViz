# gif_export.py - GIF export with threaded generation
import os
import logging
import numpy as np
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger("MathArtStudio.GIF")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("Pillow not installed — GIF export disabled. Run: pip install Pillow")


class GifWorker(QThread):
    """Worker thread that generates frames and saves a GIF."""

    progress = Signal(int, int)        # current_frame, total_frames
    frame_generated = Signal(int)      # frame index done
    finished_ok = Signal(str)          # output path
    error = Signal(str)                # error message

    def __init__(self, app_ref, output_path, num_frames, fps,
                 ping_pong=False, use_full_res=True):
        super().__init__()
        self.app = app_ref
        self.output_path = output_path
        self.num_frames = num_frames
        self.fps = fps
        self.ping_pong = ping_pong
        self.use_full_res = use_full_res
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):
        if not HAS_PIL:
            self.error.emit(
                "Pillow is required for GIF export.\n"
                "Install it with: pip install Pillow"
            )
            return

        try:
            # Determine resolution
            if self.use_full_res:
                w = self.app.settings_panel.width_spin.value()
                h = self.app.settings_panel.height_spin.value()
            else:
                w = max(32, self.app.settings_panel.width_spin.value() // 2)
                h = max(32, self.app.settings_panel.height_spin.value() // 2)

            timestep = self.app.animation_panel.timestep_slider.value()
            frames = []
            total = self.num_frames

            for i in range(total):
                if self._abort:
                    self.error.emit("Export cancelled by user.")
                    return

                t = i * timestep
                img_array = generate_frame(self.app, w, h, t)
                pil_img = Image.fromarray(img_array, mode='RGB')
                frames.append(pil_img)
                self.progress.emit(i + 1, total)
                self.frame_generated.emit(i + 1)

            # Ping-pong: append reversed frames (excluding endpoints)
            if self.ping_pong and len(frames) > 2:
                frames = frames + frames[-2:0:-1]

            duration_ms = max(1, int(1000 / self.fps))
            frames[0].save(
                self.output_path,
                save_all=True,
                append_images=frames[1:],
                duration=duration_ms,
                loop=0,
                optimize=True,
            )

            file_size = os.path.getsize(self.output_path)
            size_str = _format_size(file_size)
            actual_frames = len(frames)
            self.finished_ok.emit(
                f"Saved {actual_frames} frames ({size_str}) → {self.output_path}"
            )
            logger.info(f"GIF exported: {self.output_path} ({actual_frames} frames, {size_str})")

        except Exception as e:
            logger.error(f"GIF export failed: {e}", exc_info=True)
            self.error.emit(str(e))


def _format_size(bytes_size):
    """Format bytes to human-readable string."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"


# Import at bottom to avoid circular dependency
from generators import generate_frame