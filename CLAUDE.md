# ds-c3s-viz — Claude notes

A single static page that shows C3S seasonal precipitation **skill** (hindcast correlation)
next to the current **forecast** for each contributing system, lets you classify systems
good/ok/bad, and regroups the forecasts by that classification.

## What it is
- **One file does everything: `docs/index.html`.** Vanilla JS + CSS inline in `<script>`/`<style>`.
  No framework, no build step, no bundler, no backend. Only sibling is `docs/README.md`.
- **Pure static, no `fetch()`** (so no CORS). Data comes in only via `<img>`, `<iframe>`, and
  `new Image()`. Keep it that way — don't introduce fetch/XHR.

## Deploy (important, non-standard)
- Served by **GitHub Pages from branch `add-c3s-viz`, folder `/docs`** — NOT `main`.
  `main` is intentionally an empty initial commit; the work lives on `add-c3s-viz` and
  **PR #2 is deliberately kept open for review** (do not merge unless asked).
- Site: https://ocha-dap.github.io/ds-c3s-viz/ . **Pushing to `add-c3s-viz` redeploys.**
- Pages was pointed at the branch via `gh api -X PUT repos/OCHA-DAP/ds-c3s-viz/pages -f source.branch=add-c3s-viz -f source.path=/docs`.

## Data sources (no API keys, all public)
- **Skill** = C3S seasonal **verification** PNGs (1993–2016 hindcast correlation):
  `https://sites.ecmwf.int/cxep/c3s-seasonal-verification/plots/stmonth{MM}/{token}_stmonth{MM}_hindcast1993-2016_monthly.3m.fcmonth{L}.tp.corr.png`
  Shown as `<img>`, globally (always the world map), CSS-transformed for pan/zoom.
- **Forecast** = ECMWF **OpenCharts** embed (interactive player), one iframe per system:
  `https://climate.copernicus.eu/charts/embed/c3s_seasonal/c3s_seasonal_spatial_{oc}_rain_3m?area={area}&base_time=...&player_dimension=valid_time&type={type}&valid_time=...`

## Conventions that bit us (read before editing time/skill logic)
- **`fcmonth` = lead to the LAST month of the 3-month window = `leadtime + 2`.** The forecast
  `valid_time` is the FIRST month of the trimester. Getting this wrong shifts the skill map
  ~2 months (we shipped JAS→MJJ once). See `timeSpec()`.
- **Valid trimesters depend on issued month**: only seasons starting 1–3 months after issue are
  valid (May → JJA, JAS, ASO). `updateTrimOptions()` greys out the rest; year-wrap handled.
- **Provider skill tokens must be the latest C3S system** and must exist in the gallery. The
  Confluence "Summary of available data" lists versions, but **the gallery is the source of
  truth** — verify by probing token URLs (higher system number = newer; HTTP 200 = present,
  302 = absent). Current: ecmwf_s51, ukmo_s610, meteo_france_s9, dwd_s22, cmcc_s4, ncep_s2,
  jma_s4, eccc_s5, bom_s2. Multi-system token is year-versioned `C3Smm_s{year}` — the multi
  skill `<img>` starts at the newest year and cascades to older years via `onerror`.
- Links worth keeping: verification gallery, its docs page (`.../C3S+seasonal+forecasts+verification+plots`),
  the available-data summary, OpenCharts seasonal, Copernicus CDS. All are in the footer.

## How the map interaction works
- Pan/zoom is **shared per map type**: `state.sk` and `state.fc` are `{tx,ty,z}` (pan as a
  fraction of the frame, zoom). Applied as a CSS transform `translate(%) scale()` with
  **origin top-left** (kept top-left so zoom-to-cursor math is exact). `tfmStr()` builds it.
- **Drag to pan, scroll to zoom toward the cursor.** Skill `<img>`s are dragged directly
  (`draggable="false"` + `user-drag:none` stop the browser's ghost-image drag). Forecast
  iframes eat pointer events, so each has a transparent **`.dragcap`** overlay that drives
  the drag/zoom. `applyTransforms()` updates every map of a type live without re-rendering.
- **Forecasts render in a fixed `FXD`px wrapper (`.fxd`) scaled to fit** the tile. This is
  essential: the OpenCharts embed lays out relative to iframe size, so without the fixed
  wrapper the small grouped tiles desync from the big one. `applyFit()` sets the scale;
  re-run on resize. Every render path must call `postRender()` (binds drag + applies fit) —
  forgetting it in `renderGroups` once left the small forecasts hugely zoomed/desynced.
- **Loading priority**: skill `<img>`s are `fetchpriority="high"`, forecast iframes are
  `fetchpriority="low"` + `loading="lazy"`, and the multi skill map is rendered first in
  `rebuild()` so it fetches first.
- `DEFAULTS` holds the starting `{tx,ty,z}`; drag to a view, read `state.sk`/`state.fc` in the
  console, paste into `DEFAULTS`, commit, to bake in a default framing.
- `AREAS` maps region → forecast embed area code; the region dropdown only affects forecasts
  (skill is always global).

## Working on it
- Verify the inline JS parses: extract the `<script>` and `node --check` it (no build to catch errors).
- Before changing a skill token, `curl` the gallery URL to confirm it returns 200.
- Terse house style: single-line functions, template literals for rendering, `$ = getElementById`.
  Keep it dependency-free and static.

## Note re: OCHA DS conventions
The global OCHA/`~/.claude` conventions (ocha-stratus, blob storage, marimo, Python/uv) **do
not apply here** — this is a pure client-side viewer with no Python and no data infrastructure.
