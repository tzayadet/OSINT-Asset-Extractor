# OSINT Asset Extractor

Prototipo de escritorio en Python para recopilar recursos públicos enlazados desde una URL y guardarlos localmente. Incluye una interfaz gráfica basada en CustomTkinter y una versión web experimental.

## Componentes

- `OSINT-Asset-Extractor.py`: aplicación de escritorio.
- `index.html`: interfaz web experimental.
- `LICENSE`: licencia del proyecto.

## Requisitos de la aplicación de escritorio

Python 3.11+ y las dependencias:

```bash
python -m pip install customtkinter yt-dlp requests beautifulsoup4
```

## Ejecución

```bash
python OSINT-Asset-Extractor.py
```

Introduce una URL, selecciona los tipos de recursos y el directorio de salida. La aplicación utiliza solicitudes HTTP y extracción de enlaces; el módulo de medios emplea yt-dlp.

## Consideraciones

- La extracción depende de la estructura y accesibilidad del sitio.
- La interfaz web utiliza servicios proxy CORS de terceros; no envíes a través de ellos contenido privado, autenticado o sensible.
- Respeta robots.txt cuando corresponda, condiciones del servicio, derechos de autor y límites de frecuencia.
- Limita las pruebas a sitios propios o para los que tengas autorización.
- El proyecto es un prototipo, no un crawler exhaustivo ni una plataforma de inteligencia.

## Licencia

Consulta [LICENSE](LICENSE).
