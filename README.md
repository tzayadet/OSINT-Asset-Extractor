# OSINT Asset Collection Workbench

[![Python validation](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/python-syntax.yml/badge.svg)](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/python-syntax.yml) [![GitHub Pages](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/static.yml/badge.svg)](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/static.yml)

**Repository:** OSINT-Asset-Extractor

Aplicación de escritorio en Python para recopilar recursos públicos enlazados desde una URL autorizada y guardarlos localmente. Incluye una interfaz CustomTkinter y una interfaz web experimental.

**Web demo:** https://tzayadet.github.io/OSINT-Asset-Extractor/  
La versión web es experimental y realiza solicitudes directas desde el navegador. El sitio de destino debe permitir CORS; la demo no utiliza proxies CORS externos ni envía URLs a esos servicios. No introduzcas URLs privadas, credenciales, cookies ni contenido sensible.

## Componentes

- `OSINT-Asset-Extractor.py`: aplicación de escritorio.
- `index.html`: interfaz web experimental.
- `vendor/jszip.min.js`: JSZip 3.10.1 autoalojado.
- `vendor/JSZip-LICENSE.txt`: licencia de JSZip.
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

- Descargar vídeo o audio mediante `yt-dlp` (sin listas de reproducción y con límite de tamaño de 1 GB).
- Rechazar destinos privados, locales, reservados o no resolubles en las solicitudes HTTP de la página y los recursos DOM.
- Validar de nuevo cada destino de redirección HTTP antes de seguirlo.
- Limitar el HTML inicial a 5 MB y cada recurso DOM a 250 MB.
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

Utiliza la aplicación únicamente sobre sitios y recursos para los que tengas autorización. El cliente de escritorio valida las direcciones IP resueltas para las solicitudes HTTP iniciales, los recursos DOM y sus redirecciones, y rechaza destinos no públicos. Esta validación no fija la resolución DNS a la conexión (no elimina por completo el riesgo de DNS rebinding) y no constituye un sandbox. La extracción multimedia delegada a yt-dlp usa sus propios mecanismos de red; no debe tratarse como un control de alcance exhaustivo. La demo web tampoco comparte exactamente los mismos controles de red del cliente de escritorio.

Respeta las condiciones del servicio, los derechos de autor, robots.txt cuando corresponda y los límites de frecuencia. No introduzcas credenciales, cookies de sesión ni información privada.

La interfaz web no elude CORS: solo puede leer sitios que permitan solicitudes desde el navegador. Los archivos ZIP se generan localmente con JSZip 3.10.1, incluido en `vendor/`; no se envían a servicios de terceros.

## Limitaciones

Es una utilidad de escritorio experimental, no una plataforma de inteligencia, un crawler exhaustivo ni un sistema de adquisición forense. Los recursos recogidos no se validan por autenticidad ni seguridad.


## Pruebas

```bash
python -m unittest discover -s tests -v
python -m compileall -q .
```

Las pruebas de `asset_security.py` cubren URLs privadas, loopback, link-local, credenciales embebidas, DNS mixto y destinos públicos.

## Licencia

Consulta [LICENSE](LICENSE).
