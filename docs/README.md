# C3S seasonal precipitation — skill & forecast viewer

Single static HTML file. Pick an **issued month** + **valid trimester**, see the C3S
multi-system 3-month precipitation **correlation** (skill, 1993–2016 hindcast) and
**current forecast**; pick a **country** to get each provider's skill map (classify
good/ok/bad) and the forecasts grouped by your classification.

Pulls straight from ECMWF / Copernicus. No data infrastructure, no build, no Python,
**no `fetch()` and therefore no CORS dependency** — it's only `<img>` + `<iframe>`.

## Deploy on GitHub Pages (matches the org `docs/` convention)
1. Copy `index.html` + `.nojekyll` into the repo's `docs/` folder.
2. Settings → Pages → Source: *Deploy from a branch*, folder `/docs`.
3. Open `https://ocha-dap.github.io/<repo>/`.

## How it works (all verified live against the servers)
- **Skill maps**: static PNGs from the C3S verification gallery
  `sites.ecmwf.int/cxep/c3s-seasonal-verification/...monthly.3m.fcmonth<L>.tp.corr.png`,
  shown as `<img>` and CSS-zoomed toward the country. Provider system tokens are baked in
  (confirmed): ecmwf_s51, ukmo_s603, meteo_france_s9, dwd_s21, cmcc_s35, ncep_s2, jma_s3,
  eccc_s3, bom_s2. 3-month windows are labelled by their first lead month (= leadtime).
- **Forecasts**: the C3S charts are interactive "player" plots with no static image URL,
  so each is an **embedded** OpenCharts product page (`charts.ecmwf.int/products/
  c3s_seasonal_spatial_<centre>_rain_3m?...&area=<region>`). Framing is allowed (no
  X-Frame-Options / CSP). Region is set by area code: Africa=area11, North America=area06,
  Pacific Islands=area31, Global=area08, etc.
- **Classification is manual.** The verification server blocks cross-origin canvas pixel
  reads, so a browser can't auto-read the skill colour — set each provider good/ok/bad with
  the dropdown; the grouped forecasts update live.

## Framing the maps
- **Drag** any skill map (or the C3S forecast map) to pan; **scroll** to zoom toward the cursor.
  There are also zoom sliders and separate **reset** buttons for skill and forecast.
- The view is **shared per type**: panning/zooming any skill map moves all skill maps; the forecast
  pan/zoom moves all forecast maps. Skill and forecast move independently.
- The **forecast region** dropdown picks the continent embed (Africa = area11, etc.); skill maps are
  always the global verification PNG.
- Forecasts render in a fixed-size wrapper (`FXD` px) that's scaled to fit each tile, so the embed's
  internal layout is identical everywhere and the shared pan/zoom lines them all up.

## Config (top of the `<script>`)
- `PROVIDERS` — name, OpenCharts centre code, verification token.
- `AREAS` — region → forecast embed area code. Add regions/countries by adding entries.
- `DEFAULTS` — the starting `{tx,ty,z}` pan/zoom for skill and forecast maps. Drag/zoom to a view
  you like, read the values back off `state.sk`/`state.fc` in the console, and paste them here to
  bake in a default view for everyone.
- Forecast product type (tercile summary / anomaly / etc.) is in the Advanced panel.

## Known gaps
- **Multi-system skill map**: its token isn't in the verification gallery under a guessable
  name, so that one panel shows "n/a" (the multi-system *forecast* works). If you find its
  image URL on the verification page, drop the token into `MULTI.verif`.
- **No automated good/ok/bad** (canvas blocked). If you want it automated, compute real skill
  offline with the companion `seasonal_forecast_skill_workflow.py` (CDS hindcast + ERA5
  Spearman), commit a small `skill.json`, and have the app pre-fill the dropdowns from it —
  same static, no live infra.
