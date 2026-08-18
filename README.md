# Portugal Energy Transition

![Python](https://img.shields.io/badge/language-python-blue)
![Repo size](https://img.shields.io/github/repo-size/rogernogueraplanesas/portugal-energy-transition)
![Last commit](https://img.shields.io/github/last-commit/rogernogueraplanesas/portugal-energy-transition)

Data project on **Portugal's energy transition and the regional adoption of renewables**,
using distribution-grid data from **E-REDES** and placing it in a European context with
**socioeconomic indicators from Eurostat**.

## Research question

> **Is the adoption of renewables across Portuguese regions associated with socioeconomic
> factors, and how does Portugal compare with the broader European pattern?**

The idea is to cross regional grid/energy data for Portugal (E-REDES) with socioeconomic
indicators (Eurostat) to see whether renewable adoption tracks factors such as income,
population or economic activity — and to benchmark Portugal against other European regions.

## Background

This project started in **2023–2024** as work done during an **internship** (early in my
data-science path). That first version worked but was limited; I put real effort into its
documentation (several READMEs, images, a data-flow GIF).

In **2026** I'm picking it back up **on my own, as a personal / portfolio project** — with
no relation to that company or to any formal studies. The goal now is to turn the existing
multi-source ingestion work into a clean analytical project.

## Roadmap

The work is organized in phases. **Only the current phase is active** — the rest are planned.

1. **Phase 1 — EDA (current):** exploratory analysis of the E-REDES × Eurostat data to
   probe the research question above.
2. **Phase 2 — ML pipeline (planned):** modelling on top of the cleaned data.
3. **Phase 3 — Refactor (planned):** production hardening — type hints, tests, and a CLI.

## Data sources

| Source | Role |
|---|---|
| [E-REDES](https://e-redes.opendatasoft.com/explore/?sort=modified) | Portuguese distribution-grid / energy indicators (analytical core) |
| [Eurostat](https://ec.europa.eu/eurostat/data/database) | European socioeconomic indicators (context / comparison) |
| [INE Portugal](https://www.ine.pt/) | Portuguese national statistics |
| [World Bank](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) | Additional macro indicators |

Data is stored in **SQLite** for now. Detailed, per-source method notes live in [`docs/`](docs/).

## Project structure (indicative)

> This layout is inherited from the original build and is a **starting point** — it may be
> reorganized as the analytical phases progress.

```
portugal-energy-transition/
├── app/
│   ├── api/                  # FastAPI layer from the original build (auth, data, users)
│   ├── db/                   # SQLite creation/loading + E-R diagrams
│   ├── indicators_data/      # Core: extraction → processing → loading, per source
│   │   ├── eredes/           #   E-REDES   (processing / loading; see legacy/ for old extractor)
│   │   ├── eurostat/         #   Eurostat  (extraction / processing / loading)
│   │   ├── ine/              #   INE PT    (extraction / processing / loading)
│   │   ├── worldbank/        #   World Bank(extraction / processing / loading)
│   │   └── data_main.py      #   orchestrator
│   └── utils/                # Location codes (dicofre/zip), NUTS levels, method PDFs
├── docs/                     # Per-source guides (*.md) and images
├── legacy/                   # Retired approaches kept as samples
│   └── eredes-selenium-extractor/   # 2023–2024 Selenium bot (superseded by E-REDES API)
├── requirements.txt
└── README.md
```

Each source follows the same pattern: `data_extraction/` → `data_processing/` → `data_load/`,
plus a `*_main.py` orchestrator.

## Setup

```bash
pip install -r requirements.txt
```

> A virtual environment (venv) is recommended.

## Notes

- The **E-REDES Selenium extractor** used in 2023–2024 now lives under
  [`legacy/`](legacy/eredes-selenium-extractor/); E-REDES has since offered an official
  open-data API, which is the intended way to ingest its data going forward.
- Git history from the original build is kept as-is.
