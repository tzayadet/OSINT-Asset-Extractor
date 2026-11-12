# OSINT Asset Collection Workbench

A Python desktop utility for collecting publicly linked resources from an explicitly supplied URL. It includes a CustomTkinter interface and an experimental browser-based interface.

<p align="center">
  <a href="https://tzayadet.github.io/OSINT-Asset-Extractor/"><img src="https://img.shields.io/badge/WEB_SHOWCASE-OPEN-00a86b?style=flat-square" alt="Web showcase"></a>
  <a href="https://github.com/tzayadet/OSINT-Asset-Extractor"><img src="https://img.shields.io/badge/SOURCE-GITHUB-161b22?style=flat-square&logo=github" alt="Source"></a>
</p>

[![Python validation](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/python-syntax.yml/badge.svg)](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/python-syntax.yml) · [![Static deployment](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/static.yml/badge.svg)](https://github.com/tzayadet/OSINT-Asset-Extractor/actions/workflows/static.yml)

## What it does

- Extracts publicly linked documents, images and other resources from a supplied page.
- Supports PDF, presentation, document and archive links.
- Collects images referenced by HTML image elements.
- Supports media downloads through `yt-dlp`, with playlist handling disabled and a size limit.
- Avoids overwriting existing filenames and supports cooperative cancellation.
- Provides a browser experiment that depends on the target site's CORS policy.

## Run locally

**Requirements:** Python 3.11 or later and the packages in `requirements.txt`.

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

## Project structure

| Path | Purpose |
|---|---|
| `OSINT-Asset-Extractor.py` | Desktop application |
| `index.html` | Experimental browser interface |
| `vendor/` | Locally hosted JSZip library and license |
| `requirements.txt` | Python dependencies |
| `.github/workflows/static.yml` | Static showcase deployment |

## Showcase

The [web showcase](https://tzayadet.github.io/OSINT-Asset-Extractor/) is an experimental browser interface, not a complete mirror of the desktop application. Browser requests are subject to CORS; the page does not use third-party CORS proxies.

## Network safety and limitations

The desktop client rejects private, local, reserved and unresolved destinations for its direct HTTP page/resource requests and revalidates redirects. This does not fully prevent DNS rebinding because validation is not pinned to the eventual connection. The `yt-dlp` media path has its own network behaviour and must not be treated as covered by the same exhaustive destination controls.

The application does not execute page JavaScript or crawl an entire site recursively. Collection depends on the source page's structure and access policies. Do not enter private URLs, session cookies, credentials or sensitive material.

Use only against sites and resources you are authorized to access. Respect service terms, copyright, robots policies where applicable and reasonable request rates.

## Tests

```bash
python -m unittest discover -s tests -v
python -m compileall -q .
```

## License

See [LICENSE](LICENSE) for the repository's licensing terms.
