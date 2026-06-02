# C3S seasonal precipitation — skill & forecast viewer

Single static HTML file. Pick an **issued month**, a **valid trimester** (only seasons that
start 1–3 months after the issued month are selectable), and a **forecast region**. See the
C3S multi-system 3-month precipitation **correlation** (skill, 1993–2016 hindcast) and
**current forecast**, then each provider's skill map — classify good/ok/bad and the forecasts
regroup by your classification. Drag/scroll to frame the maps.

Pulls straight from ECMWF / Copernicus. No data infrastructure, no build, no Python,
**no `fetch()` and therefore no CORS dependency** — it's only `<img>` + `<iframe>`.

## Deploy on GitHub Pages (matches the org `docs/` convention)
1. Copy `index.html` + `.nojekyll` into the repo's `docs/` folder.
2. Settings → Pages → Source: *Deploy from a branch*, folder `/docs`.
3. Open `https://ocha-dap.github.io/<repo>/`.

## How it works (all verified live against the servers)
- **Skill maps**: static PNGs from the C3S verification gallery
  `sites.ecmwf.int/cxep/c3s-seasonal-verification/...monthly.3m.fcmonth<L>.tp.corr.png`,
  shown as `<img>` and dragged/zoomed. Provider system tokens are the latest C3S systems
  (confirmed against the gallery): ecmwf_s51, ukmo_s610, meteo_france_s9, dwd_s22, cmcc_s4,
  ncep_s2, jma_s4, eccc_s5, bom_s2. The verification `fcmonth` is the lead to the **last**
  month of the 3-month window (= leadtime + 2).
- **Forecasts**: the C3S charts are interactive "player" plots with no static image URL,
  so each is an **embedded** OpenCharts player (`climate.copernicus.eu/charts/embed/
  c3s_seasonal/c3s_seasonal_spatial_<centre>_rain_3m?...&area=<region>`). Framing is allowed
  (no X-Frame-Options / CSP). Region area codes: Africa=area11, North America=area06,
  Pacific Islands=area31, Global=area08, etc. Each forecast renders in a fixed-size wrapper
  scaled to fit, so all tiles share the same internal layout (and the same pan/zoom).
- **Classification is manual.** The verification server blocks cross-origin canvas pixel
  reads, so a browser can't auto-read the skill colour — set each provider good/ok/bad with
  the dropdown; the grouped forecasts update live.

## Framing the maps
- **Drag** any skill map (or the C3S forecast map) to pan; **scroll** to zoom toward the cursor.
  Separate **reset** buttons restore the default view for skill and forecast.
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

## Notes / gaps
- **Multi-system skill** uses the year-versioned token `C3Smm_s{year}` (`MULTI_CANDS`): the map
  starts at the newest year and cascades to older ones on error, showing "n/a" only if none
  resolve. Bump `MULTI_CANDS` as new cycles appear.
- **Classification is manual** — the verification server blocks cross-origin canvas pixel reads,
  so the browser can't auto-read the skill colour. Automating it would mean computing skill
  offline and shipping a small precomputed JSON for the app to pre-fill the dropdowns (still
  fully static, no live infra).
- **Skill loads first**: skill PNGs are `fetchpriority=high` and the multi skill map renders
  before everything; forecast iframes are `fetchpriority=low` + lazy.
