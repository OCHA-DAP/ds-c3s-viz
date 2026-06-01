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

## Config (top of the `<script>`)
- `PROVIDERS` — name, OpenCharts centre code, verification token.
- `COUNTRY` — `{bbox:[lon_min,lat_min,lon_max,lat_max], region:"Africa"}`. Add countries here;
  `region` chooses which continent embed + calibration to use.
- `AREAS` — per region: continent embed `code` (area11, etc.), geographic window `ext`
  `[lonW,lonE,latN,latS]`, and `fit` (where that window sits in the frame). Skill maps always
  use the **global** verification PNG (`SKILL_EXT`/`SKILL_FIT`), regardless of region.
- `REGION_CAL` — per-region calibration: `{sk:{x,y,z}, fc:{x,y,z}}` where `x,y` pan and `z`
  zooms. Shared by every country in the region (a country's position is computed from its bbox;
  pan/zoom fine-tune on top). **These are the baked-in defaults users see** — set them with the
  workflow below.
- Forecast product type (tercile summary / anomaly / etc.) is in the Advanced panel.

## Calibrating regions locally (then pushing the defaults)
The shipped `ext`/`fit`/`REGION_CAL` numbers are guesses. To set real defaults:

1. `python3 tools/serve.py` → open http://localhost:8000
2. Select a country in the region, tick **show centre crosshair**, and tune the skill (left)
   and forecast (right) pan/zoom sliders — they sit right under the two C3S plots — until the
   country sits under the crosshair.
3. Click **save region defaults → file** (only shown on localhost). `tools/serve.py` writes the
   values into the `REGION_CAL` line for that region in `index.html`.
4. Repeat per region, then `git commit` + `git push`. Pages serves the new defaults; the live
   site never calls the save API, so it stays a pure static page.

## Known gaps
- **Multi-system skill map**: its token isn't in the verification gallery under a guessable
  name, so that one panel shows "n/a" (the multi-system *forecast* works). If you find its
  image URL on the verification page, drop the token into `MULTI.verif`.
- **No automated good/ok/bad** (canvas blocked). If you want it automated, compute real skill
  offline with the companion `seasonal_forecast_skill_workflow.py` (CDS hindcast + ERA5
  Spearman), commit a small `skill.json`, and have the app pre-fill the dropdowns from it —
  same static, no live infra.
