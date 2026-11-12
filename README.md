# OSINT Asset Extractor

Aplicación de escritorio en Python para recopilar recursos enlazados desde una página web y guardarlos localmente. Incluye una interfaz CustomTkinter y una interfaz web experimental.

## Componentes

- `OSINT-Asset-Extractor.py`: aplicación de escritorio.
- `index.html`: interfaz web experimental.
- `requirements.txt`: dependencias de Python.
- `.github/workflows/static.yml`: publicación del contenido estático configurado para GitHub Pages.

## Requisitos

- Python 3.11 o superior.
- Las dependencias declaradas en `requirements.txt`.
- Conexión a Internet para consultar páginas y descargar recursos.

## Instalación y ejecución

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python OSINT-Asset-Extractor.py
```

Linux / macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python OSINT-Asset-Extractor.py
```

Introduce una URL HTTP/HTTPS, el tipo de recurso y el directorio de salida. La aplicación puede:

- Descargar vídeo o audio mediante `yt-dlp`.
- Extraer enlaces directos a PDF, presentaciones, documentos y archivos comprimidos.
- Recoger imágenes referenciadas mediante etiquetas HTML `img`.
- Evitar sobrescribir nombres de archivo existentes.
- Cancelar el proceso de forma cooperativa.

## Alcance técnico

- Analiza el HTML de la página inicial; no ejecuta JavaScript ni recorre de forma recursiva todo el sitio.
- No requiere ni implementa autenticación para páginas privadas.
- Los recursos se descargan secuencialmente; no hay un ajuste de concurrencia.
- La extracción depende de la estructura, accesibilidad y políticas del sitio.
- Las actualizaciones de la interfaz se procesan en el hilo principal de Tkinter.
- La cancelación se aplica entre operaciones y durante la escritura de recursos; una solicitud de red ya iniciada puede tardar hasta alcanzar su timeout.

## Uso responsable y seguridad

Utiliza la aplicación únicamente sobre sitios y recursos para los que tengas autorización. El programa no aplica una lista de alcance ni bloquea automáticamente direcciones privadas o internas presentes en los enlaces de la página. No lo utilices con páginas no confiables ni como sustituto de un crawler con controles de alcance.

Respeta las condiciones del servicio, los derechos de autor, robots.txt cuando corresponda y los límites de frecuencia. No introduzcas credenciales, cookies de sesión ni información privada.

La interfaz web experimental utiliza servicios proxy CORS de terceros. No envíes por esos servicios contenido privado, autenticado o sensible.

## Limitaciones

Es una utilidad de escritorio experimental, no una plataforma de inteligencia, un crawler exhaustivo ni un sistema de adquisición forense. Los recursos recogidos no se validan por autenticidad ni seguridad.

## Licencia

Consulta [LICENSE](LICENSE).
