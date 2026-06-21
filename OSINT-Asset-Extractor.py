import customtkinter as ctk
import yt_dlp, requests, os, threading, re, time
from bs4 import BeautifulSoup
from tkinter import filedialog
from urllib.parse import urljoin, urlparse
from datetime import datetime

# Configuración de tema enterprise oscuro
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class OSINTExtractor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OSINT Asset Extractor v2.1")
        self.geometry("950x600")
        self.configure(fg_color="#121212")
        self.resizable(True, True)
        
        self.is_running = False
        self._init_vars()
        self._build_ui()

    def _init_vars(self):
        self.target_url = ctk.StringVar()
        self.file_type = ctk.StringVar(value="ALL")
        self.save_path = ctk.StringVar(value=os.path.join(os.getcwd(), "extracted_assets"))
        self.threads = ctk.StringVar(value="4")
        self.timeout = ctk.StringVar(value="10")

    def _build_ui(self):
        # Panel Izquierdo: Configuración
        left_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=0, width=300)
        left_frame.pack(side="left", fill="y", padx=0, pady=0)
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="CONFIGURACIÓN", font=("Segoe UI", 12, "bold"), text_color="#888888").pack(pady=(20, 10), padx=20, anchor="w")
        
        self._add_entry(left_frame, "Objetivo (URL):", self.target_url, "https://")
        self._add_dropdown(left_frame, "Filtro de Activos:", self.file_type, ["ALL", "VIDEO", "PDF", "PPT", "IMG", "DOC"])
        self._add_entry(left_frame, "Directorio de Salida:", self.save_path, "C:/...", readonly=True, browse=True)
        self._add_entry(left_frame, "Hilos (Threads):", self.threads, "4")
        self._add_entry(left_frame, "Timeout (seg):", self.timeout, "10")

        # Botones de control
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=30, padx=20, fill="x")
        
        self.btn_start = ctk.CTkButton(btn_frame, text="INICIAR EXTRACCIÓN", fg_color="#2d2d2d", hover_color="#3d3d3d", border_width=1, border_color="#444444", command=self._toggle_task)
        self.btn_start.pack(fill="x", pady=5)
        
        self.btn_clear = ctk.CTkButton(btn_frame, text="LIMPIAR CONSOLA", fg_color="#2d2d2d", hover_color="#3d3d3d", border_width=1, border_color="#444444", command=self._clear_log)
        self.btn_clear.pack(fill="x", pady=5)

        # Panel Derecho: Consola / Telemetría
        right_frame = ctk.CTkFrame(self, fg_color="#0d0d0d", corner_radius=0)
        right_frame.pack(side="right", fill="both", expand=True)

        header = ctk.CTkFrame(right_frame, fg_color="#1a1a1a", height=30)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="TELEMETRÍA Y LOGS DE EJECUCIÓN", font=("Consolas", 11), text_color="#666666").pack(side="left", padx=10, pady=5)
        
        self.status_indicator = ctk.CTkLabel(header, text="● IDLE", font=("Consolas", 11), text_color="#555555")
        self.status_indicator.pack(side="right", padx=10, pady=5)

        self.console = ctk.CTkTextbox(right_frame, fg_color="#0d0d0d", font=("Consolas", 12), text_color="#cccccc", state="disabled", wrap="word")
        self.console.pack(fill="both", expand=True, padx=5, pady=5)

    def _add_entry(self, parent, label_text, var, placeholder, readonly=False, browse=False):
        ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 11), text_color="#aaaaaa").pack(pady=(10, 2), padx=20, anchor="w")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(padx=20, pady=(0, 10), fill="x")
        
        entry = ctk.CTkEntry(frame, textvariable=var, placeholder_text=placeholder, fg_color="#252525", border_color="#333333", font=("Consolas", 11))
        if readonly: entry.configure(state="readonly")
        entry.pack(side="left", fill="x", expand=True)
        
        if browse:
            ctk.CTkButton(frame, text="...", width=30, fg_color="#252525", hover_color="#333333", command=lambda: self._browse_dir(var)).pack(side="right", padx=(5,0))

    def _add_dropdown(self, parent, label_text, var, values):
        ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 11), text_color="#aaaaaa").pack(pady=(10, 2), padx=20, anchor="w")
        ctk.CTkOptionMenu(parent, variable=var, values=values, fg_color="#252525", button_color="#333333", button_hover_color="#444444", dropdown_fg_color="#1e1e1e", font=("Consolas", 11)).pack(padx=20, pady=(0, 10), fill="x")

    def _browse_dir(self, var):
        path = filedialog.askdirectory()
        if path: var.set(path)

    def _log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = "#cccccc"
        if level == "ERROR": color = "#cf6679"
        elif level == "SUCCESS": color = "#81c784"
        elif level == "WARN": color = "#ffb74d"
        
        self.console.configure(state="normal")
        self.console.insert("end", f"[{timestamp}] [{level}] {msg}\n", level)
        self.console.tag_config(level, foreground=color)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _clear_log(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def _toggle_task(self):
        if not self.is_running:
            if not self.target_url.get():
                self._log("URL objetivo no definida.", "ERROR")
                return
            self.is_running = True
            self.btn_start.configure(text="DETENER PROCESO", fg_color="#3a1c1c", hover_color="#4a2c2c", border_color="#cf6679")
            self.status_indicator.configure(text="● RUNNING", text_color="#81c784")
            threading.Thread(target=self._execute_extraction, daemon=True).start()
        else:
            self.is_running = False
            self.btn_start.configure(text="INICIAR EXTRACCIÓN", fg_color="#2d2d2d", hover_color="#3d3d3d", border_color="#444444")
            self.status_indicator.configure(text="● ABORTED", text_color="#ffb74d")
            self._log("Proceso detenido por el operador.", "WARN")

    def _execute_extraction(self):
        url = self.target_url.get()
        f_type = self.file_type.get()
        out_dir = self.save_path.get()
        os.makedirs(out_dir, exist_ok=True)
        
        self._log(f"Iniciando vector de extracción: {url}")
        self._log(f"Filtros: {f_type} | Hilos: {self.threads.get()} | Timeout: {self.timeout.get()}s")

        try:
            if f_type in ["ALL", "VIDEO"]:
                self._log("Desplegando módulo de medios (yt-dlp)...", "WARN")
                ydl_opts = {
                    'outtmpl': f'{out_dir}/%(title)s.%(ext)s', 
                    'quiet': True, 
                    'no_warnings': True,
                    'socket_timeout': int(self.timeout.get())
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try: 
                        ydl.download([url])
                        self._log("Módulo de medios completado.", "SUCCESS")
                    except Exception as e:
                        self._log(f"Fallo en módulo de medios: {e}", "ERROR")

            if f_type in ["ALL", "PDF", "PPT", "IMG", "DOC"]:
                self._log("Rastreando estructura DOM y enlaces directos...")
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
                r = requests.get(url, headers=headers, timeout=int(self.timeout.get()))
                r.raise_for_status()
                soup = BeautifulSoup(r.text, 'html.parser')
                
                extensions = {
                    'PDF': ['.pdf'], 'PPT': ['.ppt', '.pptx'], 'IMG': ['.jpg', '.png', '.jpeg', '.gif', '.webp'], 
                    'DOC': ['.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']
                }
                targets = extensions.get(f_type, sum(extensions.values(), []))
                
                links_found = 0
                for link in soup.find_all('a', href=True):
                    if not self.is_running: break
                    href = link['href']
                    if any(href.lower().endswith(ext) for ext in targets):
                        links_found += 1
                        self._download_file(urljoin(url, href), out_dir)
                        
                if f_type == "IMG":
                    for img in soup.find_all('img', src=True):
                        if not self.is_running: break
                        self._download_file(urljoin(url, img['src']), out_dir)
                
                self._log(f"Rastreo DOM finalizado. {links_found} enlaces procesados.", "SUCCESS")

            if self.is_running:
                self._log("Extracción finalizada. Activos asegurados en directorio.", "SUCCESS")
                self.status_indicator.configure(text="● COMPLETE", text_color="#81c784")
                
        except Exception as e:
            self._log(f"Error crítico en el vector: {e}", "ERROR")
            self.status_indicator.configure(text="● FAILED", text_color="#cf6679")
        finally:
            self.is_running = False
            self.btn_start.configure(text="INICIAR EXTRACCIÓN", fg_color="#2d2d2d", hover_color="#3d3d3d", border_color="#444444")

    def _download_file(self, file_url, out_dir):
        try:
            filename = os.path.basename(urlparse(file_url).path)
            if not filename or '.' not in filename: return
            filepath = os.path.join(out_dir, filename)
            
            r = requests.get(file_url, stream=True, timeout=int(self.timeout.get()))
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(8192):
                    if not self.is_running: return
                    if chunk: f.write(chunk)
            self._log(f"Activo descargado: {filename}", "SUCCESS")
        except Exception as e:
            self._log(f"Fallo al descargar {os.path.basename(file_url)}: {e}", "ERROR")

if __name__ == "__main__":
    app = OSINTExtractor()
    app.mainloop()
