# Legacy — E-REDES Selenium extractor (2023–2024)

This folder holds the **original E-REDES data extractor**, written in **2023–2024** as
the first approach to pull grid/energy indicators from the E-REDES open-data site.

At the time, extraction was done with a **Selenium bot** (`eredes_data.py`,
`eredes_metadata.py`) that drove a headless browser, simulated the clicks needed to
navigate the catalog, and downloaded the exported files automatically.

## Why it is here and not in the active pipeline

Shortly before this was built, E-REDES had already launched its **official open-data
portal with a public API** (November 2022) — I simply wasn't aware of it back then, so I
solved the problem by scraping. That API is the sensible way to ingest E-REDES data today,
so the Selenium approach is **no longer part of the active pipeline**.

It is kept here, unchanged, as a **sample of working with Selenium** (headless driver
setup, explicit waits, element location, and concurrent downloads).

## Notes

- The code is preserved **as-is**. It was moved out of `app/indicators_data/eredes/` without
  modification, so the relative path math inside it (e.g. the `..` hops used to locate the
  project root) is **not adjusted** for this new location — it is not meant to run from here.
- Replacing this extractor with the official E-REDES API is a planned, separate task; the
  rest of the E-REDES pipeline (processing / loading) still lives under
  `app/indicators_data/eredes/`.
