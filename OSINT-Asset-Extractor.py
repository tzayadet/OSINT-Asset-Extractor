#!/usr/bin/env python3
"""Desktop utility for collecting linked public assets from an authorized URL."""

from __future__ import annotations

import os
import queue
import re
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
from urllib.parse import urljoin, urlparse

import customtkinter as ctk
import requests
import yt_dlp
from bs4 import BeautifulSoup

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

EXTENSIONS = {
    "PDF": (".pdf",),
    "PPT": (".ppt", ".pptx"),
    "IMG": (".jpg", ".jpeg", ".png", ".gif", ".webp"),
    "DOC": (".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar"),
}
ALL_EXTENSIONS = tuple(ext for values in EXTENSIONS.values() for ext in values)


class OSINTExtractor(ctk.CTk):
    """Tkinter UI; all widget updates are marshalled onto the main thread."""

    def __init__(self):
        super().__init__()
        self.title("OSINT Asset Extractor")
        self.geometry("950x600")
        self.minsize(760, 480)
        self.configure(fg_color="#121212")
        self.resizable(True, True)

        self.is_running = False
        self.stop_event = threading.Event()
        self.ui_queue: queue.Queue = queue.Queue()

        self._init_vars()
        self._build_ui()
        self.after(100, self._drain_ui_queue)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_vars(self):
        self.target_url = ctk.StringVar()
        self.file_type = ctk.StringVar(value="ALL")
        self.save_path = ctk.StringVar(
            value=os.path.join(os.getcwd(), "extracted_assets")
        )
        self.timeout = ctk.StringVar(value="10")

    def _build_ui(self):
        left_frame = ctk.CTkFrame(
            self, fg_color="#1e1e1e", corner_radius=0, width=300
        )
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)

        ctk.CTkLabel(
            left_frame,
            text="CONFIGURACIÓN",
            font=("Segoe UI", 12, "bold"),
            text_color="#888888",
        ).pack(pady=(20, 10), padx=20, anchor="w")

        self._add_entry(left_frame, "URL autorizada:", self.target_url, "https://")
        self._add_dropdown(
            left_frame,
            "Filtro de activos:",
            self.file_type,
            ["ALL", "VIDEO", "PDF", "PPT", "IMG", "DOC"],
        )
        self._add_entry(
            left_frame,
            "Directorio de salida:",
            self.save_path,
            "C:/...",
            readonly=True,
            browse=True,
        )
        self._add_entry(
            left_frame, "Timeout (segundos):", self.timeout, "10"
        )

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=30, padx=20, fill="x")

        self.btn_start = ctk.CTkButton(
            btn_frame,
            text="INICIAR EXTRACCIÓN",
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            border_width=1,
            border_color="#444444",
            command=self._toggle_task,
        )
        self.btn_start.pack(fill="x", pady=5)

        self.btn_clear = ctk.CTkButton(
            btn_frame,
            text="LIMPIAR CONSOLA",
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            border_width=1,
            border_color="#444444",
            command=self._clear_log,
        )
        self.btn_clear.pack(fill="x", pady=5)

        right_frame = ctk.CTkFrame(self, fg_color="#0d0d0d", corner_radius=0)
        right_frame.pack(side="right", fill="both", expand=True)

        header = ctk.CTkFrame(right_frame, fg_color="#1a1a1a", height=30)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="TELEMETRÍA Y LOGS DE EJECUCIÓN",
            font=("Consolas", 11),
            text_color="#666666",
        ).pack(side="left", padx=10, pady=5)

        self.status_indicator = ctk.CTkLabel(
            header,
            text="● IDLE",
            font=("Consolas", 11),
            text_color="#555555",
        )
        self.status_indicator.pack(side="right", padx=10, pady=5)

        self.console = ctk.CTkTextbox(
            right_frame,
            fg_color="#0d0d0d",
            font=("Consolas", 12),
            text_color="#cccccc",
            state="disabled",
            wrap="word",
        )
        self.console.pack(fill="both", expand=True, padx=5, pady=5)

    def _add_entry(
        self, parent, label_text, variable, placeholder,
        readonly=False, browse=False
    ):
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Segoe UI", 11),
            text_color="#aaaaaa",
        ).pack(pady=(10, 2), padx=20, anchor="w")

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(padx=20, pady=(0, 10), fill="x")

        entry = ctk.CTkEntry(
            frame,
            textvariable=variable,
            placeholder_text=placeholder,
            fg_color="#252525",
            border_color="#333333",
            font=("Consolas", 11),
        )
        if readonly:
            entry.configure(state="readonly")
        entry.pack(side="left", fill="x", expand=True)

        if browse:
            ctk.CTkButton(
                frame,
                text="...",
                width=30,
                fg_color="#252525",
                hover_color="#333333",
                command=lambda: self._browse_dir(variable),
            ).pack(side="right", padx=(5, 0))

    def _add_dropdown(self, parent, label_text, variable, values):
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Segoe UI", 11),
            text_color="#aaaaaa",
        ).pack(pady=(10, 2), padx=20, anchor="w")

        ctk.CTkOptionMenu(
            parent,
            variable=variable,
            values=values,
            fg_color="#252525",
            button_color="#333333",
            button_hover_color="#444444",
            dropdown_fg_color="#1e1e1e",
            font=("Consolas", 11),
        ).pack(padx=20, pady=(0, 10), fill="x")

    def _browse_dir(self, variable):
        path = filedialog.askdirectory()
        if path:
            variable.set(path)

    def _log(self, message, level="INFO"):
        """Queue log messages; worker threads never touch Tk widgets."""
        self.ui_queue.put(("log", message, level))

    def _set_status(self, text, color):
        self.ui_queue.put(("status", text, color))

    def _set_button(self, text, disabled=False):
        self.ui_queue.put(("button", text, disabled))

    def _append_log(self, message, level):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "#cccccc",
            "ERROR": "#cf6679",
            "SUCCESS": "#81c784",
            "WARN": "#ffb74d",
        }
        self.console.configure(state="normal")
        self.console.insert(
            "end", f"[{timestamp}] [{level}] {message}\n", level
        )
        self.console.tag_config(level, foreground=colors.get(level, "#cccccc"))
        self.console.see("end")
        self.console.configure(state="disabled")

    def _drain_ui_queue(self):
        try:
            while True:
                item = self.ui_queue.get_nowait()
                kind = item[0]

                if kind == "log":
                    self._append_log(item[1], item[2])
                elif kind == "status":
                    self.status_indicator.configure(
                        text=f"● {item[1]}", text_color=item[2]
                    )
                elif kind == "button":
                    if item[1] == "INICIAR EXTRACCIÓN" and not item[2]:
                        self.btn_start.configure(
                            text=item[1],
                            state="normal",
                            fg_color="#2d2d2d",
                            hover_color="#3d3d3d",
                            border_color="#444444",
                        )
                    else:
                        self.btn_start.configure(
                            text=item[1],
                            state="disabled" if item[2] else "normal",
                        )
        except queue.Empty:
            pass
        finally:
            if self.winfo_exists():
                self.after(100, self._drain_ui_queue)

    def _clear_log(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    @staticmethod
    def _validate_url(url):
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def _toggle_task(self):
        if self.is_running:
            if not self.stop_event.is_set():
                self.stop_event.set()
                self.btn_start.configure(
                    text="CANCELANDO...",
                    state="disabled",
                )
                self.status_indicator.configure(
                    text="● STOPPING", text_color="#ffb74d"
                )
                self._log(
                    "Cancelación solicitada; se detendrá la operación en curso.",
                    "WARN",
                )
            return

        url = self.target_url.get().strip()
        if not self._validate_url(url):
            self._log("Introduce una URL HTTP o HTTPS válida.", "ERROR")
            return

        try:
            timeout = int(self.timeout.get())
            if not 1 <= timeout <= 120:
                raise ValueError
        except ValueError:
            self._log("El timeout debe ser un entero entre 1 y 120 segundos.", "ERROR")
            return

        config = {
            "url": url,
            "file_type": self.file_type.get(),
            "output_dir": self.save_path.get(),
            "timeout": timeout,
        }

        self.stop_event.clear()
        self.is_running = True
        self.btn_start.configure(
            text="DETENER PROCESO",
            state="normal",
            fg_color="#3a1c1c",
            hover_color="#4a2c2c",
            border_color="#cf6679",
        )
        self.status_indicator.configure(
            text="● RUNNING", text_color="#81c784"
        )

        threading.Thread(
            target=self._execute_extraction,
            args=(config,),
            daemon=True,
        ).start()

    def _execute_extraction(self, config):
        url = config["url"]
        file_type = config["file_type"]
        output_dir = config["output_dir"]
        timeout = config["timeout"]

        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            self._log(f"Iniciando extracción autorizada: {url}")
            self._log(
                f"Filtro: {file_type} | Timeout: {timeout}s"
            )

            if file_type in {"ALL", "VIDEO"} and not self.stop_event.is_set():
                self._log("Iniciando módulo multimedia (yt-dlp)...", "WARN")

                def cancel_hook(_progress):
                    if self.stop_event.is_set():
                        raise yt_dlp.utils.DownloadError(
                            "Cancelado por el operador"
                        )

                ydl_options = {
                    "outtmpl": str(Path(output_dir) / "%(title)s.%(ext)s"),
                    "quiet": True,
                    "no_warnings": True,
                    "socket_timeout": timeout,
                    "progress_hooks": [cancel_hook],
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_options) as downloader:
                        downloader.download([url])
                    if not self.stop_event.is_set():
                        self._log("Módulo multimedia completado.", "SUCCESS")
                except yt_dlp.utils.DownloadError as exc:
                    if not self.stop_event.is_set():
                        self._log(f"Fallo en módulo multimedia: {exc}", "ERROR")

            if (
                file_type in {"ALL", "PDF", "PPT", "IMG", "DOC"}
                and not self.stop_event.is_set()
            ):
                self._extract_page_assets(url, file_type, output_dir, timeout)

            if self.stop_event.is_set():
                self._set_status("ABORTED", "#ffb74d")
                self._log("Proceso cancelado por el operador.", "WARN")
            else:
                self._set_status("COMPLETE", "#81c784")
                self._log("Extracción finalizada.", "SUCCESS")

        except Exception as exc:
            self._set_status("FAILED", "#cf6679")
            self._log(f"Error durante la extracción: {exc}", "ERROR")
        finally:
            self.is_running = False
            self._set_button("INICIAR EXTRACCIÓN")

    def _extract_page_assets(self, url, file_type, output_dir, timeout):
        self._log("Analizando enlaces de la página...")
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        extensions = (
            ALL_EXTENSIONS if file_type == "ALL" else EXTENSIONS.get(file_type, ())
        )
        candidates = set()

        for link in soup.find_all("a", href=True):
            asset_url = urljoin(url, link["href"])
            path = urlparse(asset_url).path.lower()
            if path.endswith(extensions):
                candidates.add(asset_url)

        if file_type in {"ALL", "IMG"}:
            for image in soup.find_all("img", src=True):
                candidates.add(urljoin(url, image["src"]))

        downloaded = 0
        for asset_url in sorted(candidates):
            if self.stop_event.is_set():
                break
            if self._download_file(asset_url, output_dir, timeout):
                downloaded += 1

        self._log(
            f"Análisis DOM terminado. {downloaded} recursos descargados.",
            "SUCCESS",
        )

    def _download_file(self, file_url, output_dir, timeout):
        parsed = urlparse(file_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            self._log("Recurso omitido: esquema de URL no permitido.", "WARN")
            return False

        filename = os.path.basename(parsed.path)
        filename = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._")
        if not filename or "." not in filename:
            return False

        output_path = Path(output_dir) / filename
        stem, suffix = output_path.stem, output_path.suffix
        counter = 1
        while output_path.exists():
            output_path = Path(output_dir) / f"{stem}_{counter}{suffix}"
            counter += 1

        try:
            with requests.get(
                file_url,
                headers={"User-Agent": USER_AGENT},
                stream=True,
                timeout=timeout,
            ) as response:
                response.raise_for_status()
                with output_path.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=8192):
                        if self.stop_event.is_set():
                            handle.close()
                            output_path.unlink(missing_ok=True)
                            return False
                        if chunk:
                            handle.write(chunk)

            self._log(f"Recurso descargado: {output_path.name}", "SUCCESS")
            return True

        except requests.RequestException as exc:
            output_path.unlink(missing_ok=True)
            self._log(f"No se pudo descargar {filename}: {exc}", "ERROR")
            return False
        except OSError as exc:
            output_path.unlink(missing_ok=True)
            self._log(f"No se pudo guardar {filename}: {exc}", "ERROR")
            return False

    def _on_close(self):
        if self.is_running:
            self.stop_event.set()
        self.destroy()


if __name__ == "__main__":
    app = OSINTExtractor()
    app.mainloop()
