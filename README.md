<p align="center">
  <img src="https://img.shields.io/badge/OSINT-ASSET_COLLECTION_WORKBENCH-101010?style=for-the-badge&labelColor=050805&color=00FF41" alt="OSINT Asset Collection"/>
  <img src="https://img.shields.io/badge/PYTHON-DESKTOP_%2F_WEB-101010?style=for-the-badge&logo=python&logoColor=00FF41" alt="Python"/>
</p>

# OSINT Asset Collection Workbench

A Python desktop utility for collecting publicly linked resources from an explicitly supplied URL. It includes a CustomTkinter interface and an experimental browser-based interface.

<p align="center">
  <a href="https://tzayadet.github.io/OSINT-Asset-Extractor/"><strong>LIVE WEB SHOWCASE ↗</strong></a> ·
  <a href="https://github.com/tzayadet/OSINT-Asset-Extractor"><strong>SOURCE CODE</strong></a>
</p>

[![Python validation](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/python-syntax.yml/badge.svg)](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/python-syntax.yml) · [![Static deployment](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/static.yml/badge.svg)](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/static.yml)

## Features

- Extracts publicly linked documents, images and other resources from a supplied page.
- Supports PDF, presentation, document and archive links.
- Collects images referenced by HTML image elements.
- Supports media downloads through `yt-dlp`, with playlist handling disabled and a size limit.
- Caps direct asset discovery at 500 candidates and direct downloads at 250 MB each.
- Uses stable extractor/ID-based media filenames, limits media downloads to 1 GB and supports cooperative cancellation.
- Includes a browser experiment subject to the target site's CORS policy.

## Run locally

**Requirements:** Python 3.11+ and the packages in `requirements.txt`.

```bash
python -m venv .venv
```

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python OSINT-Asset-Extractor.py
```

**Linux / macOS**
```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python OSINT-Asset-Extractor.py
```

## Project layout

| Path | Purpose |
|---|---|
| `OSINT-Asset-Extractor.py` | Desktop application |
| `index.html` | Experimental browser interface |
| `vendor/` | Locally hosted JSZip library and licence |
| `requirements.txt` | Python dependencies |
| `.github/workflows/static.yml` | Static showcase deployment |

## Showcase

The [web showcase](https://tzayadet.github.io/OSINT-Asset-Extractor/) is an experimental browser interface, not a complete mirror of the desktop application. Browser requests are subject to CORS; the page does not use third-party CORS proxies.

## Network behaviour and limitations

The desktop client rejects private, local, reserved and unresolved destinations for direct HTTP page/resource requests and revalidates redirects. This does not fully prevent DNS rebinding because validation is not pinned to the eventual connection. The `yt-dlp` media path has its own network behaviour and must not be treated as covered by the same destination controls; the application logs this distinction before starting media extraction.

The application does not execute page JavaScript or crawl an entire site recursively. Collection depends on the source page's structure and the resources it exposes.

## Validation

The Python workflow compiles the application and runs regression tests for URL scope validation, including malformed, oversized and non-public destinations:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

## Deployment

GitHub Pages publishes the static browser showcase only. The desktop application requires Python and a compatible local environment.

## Responsible use

Collect only resources you are authorised to access and download. Respect site terms, copyright and applicable privacy rules. Public accessibility does not automatically grant redistribution rights.

## License

See [LICENSE](LICENSE).
