# PX "16A move explainer" — drill-through page build guide (BUILD 2026-11-12a)
Measures build **12f** (`P6A_MEASURES_TE2.csx`, 228 measures, folder `P6\9 Move explainer`, prefix `PX`).
Setup tables: `P6W_SETUP_PATCH_07.dax`. Check: `PX_CHECK.dax`.
Works for any counterparty in context (one CPY, one CPH, several). Live DAX on FACT_LIMIT_16A + FACT_ALLREPO; when the
ALLREPO light bake gains a daily bridge table, only the PX base measures change, the page stays.

## 0. Order of work (≈ 1 h)
1. `P6W_SETUP_PATCH_07.dax`: three tables (PX Window, PX From / PX To, PX Step). Sort Window and Step by Order.
2. Tabular Editor ▸ run `P6A_MEASURES_TE2.csx` (12d) ▸ Ctrl+S in Power BI.
3. `PX_CHECK.dax` with x in `_ids` ▸ the figures in its header must come back. Note the ms of X1.
4. Build the page (§1–§4), then wire the drill-through (§5).

## 1. Drill-through page
- A normal report page that **receives a filter from another page**. You right-click a data point on page A (e.g. a CPH
  row in the movers table) ▸ **Drill through** ▸ the page opens filtered to that CPH. A **Back** arrow returns to page A.
- The page declares which field it accepts in its **drill-through well** (Build pane, bottom). Any visual that shows that
  field can drill to it. The option only appears in the right-click menu when the visual you click contains that field.
- **Keep all filters** (switch under the well): On = the page also inherits page A's other filters and slicers (e.g. the
  As of date). We want On.
- While designing, the page shows everything unfiltered. To design with real numbers, open the drill-through filter
  card in the Filters pane and tick one CPH temporarily; drilling later replaces it.
- Usually hidden from the page tabs (right-click the tab ▸ Hide page); drilling still works.

## 2. Create the page
1. New page ▸ rename **PX 16A Move**. Same canvas size and background as P6a (copy P6a's page format if needed:
   Format ▸ Canvas settings / Canvas background).
2. Click an empty spot of the canvas ▸ Visualizations ▸ **Build** ▸ scroll to **Drill through**:
   - drag `DIM_COUNTERPARTY[CPH_Label]` into "Add drill-through fields here";
   - then drag `DIM_COUNTERPARTY[CPY Label]` under it (see §5 test);
   - **Keep all filters: On**; Cross-report: Off.
   Power BI adds a **Back** button (top-left arrow). Move it to 8 · 10 · 24 · 24.
3. Add a page slicer **As of**: copy the P6a As-of slicer (`P6W AsOf`) here; when asked "sync this slicer?" ▸ **Sync**.
   (Drilling from P6a carries the date anyway; the slicer lets you change it on this page.)

## 3. Header and window (Y 8–70)
| Visual | X · Y · W · H | Content | Settings |
|---|---|---|---|
| Title | Card (new) 40 · 6 · 720 · 30 | `PX Title` | callout 16 pt, label off, background off, left aligned |
| Subtitle | Card (new) 40 · 34 · 720 · 22 | `PX Subtitle` | callout 9 pt muted `#8C9BB0`, label off |
| Window | Button slicer 900 · 10 · 360 · 28 | `PX Window[Window]` | single select, 1 row × 5 columns, default **1W** selected |
| From / To | Slicer (Dropdown) 900 · 42 · 176 · 26 and 1084 · 42 · 176 · 26 | `PX From[Date]`, `PX To[Date]` | single select; header text "From (Custom)" / "To (Custom)"; only used when Window = Custom |
| As of | the synced slicer 770 · 10 · 120 · 28 | `P6W AsOf` | as on P6a |
| Sponsored | Button slicer 640 · 10 · 120 · 28 | `PX Sponsored[Sponsored]` | single select, 1 × 2, default **Exclude**; the subtitle says which is on (12 Nov b) |
Window logic: end = As of (or To on Custom); start = end − 1/7/14/30 days (or From). Each fact snaps to its last file on
or before those dates (16A and ALLREPO can differ by a day; the subtitle shows both).

## 4. Body
### 4a. Waterfall `PX1` — stacked column chart · 20 · 80 · 740 · 330
- X-axis: `PX Step[Step]` (sorted by Order). Y-axis, in this order: `PX WF Base`, `PX WF Total`, `PX WF Up`, `PX WF Down`.
- Format ▸ Columns ▸ Colors: **Base = no fill** (Transparency 100 %), Total `#46B6C9`, Up `#E8597A` (pushes 16A up),
  Down `#56C08D`. Spacing ▸ inner padding 30 %.
- Data labels On; Apply settings to ▸ series **Base ▸ Off**; Up / Down / Total ▸ display units Millions, 1 decimal.
- Legend Off. Y-axis: display units Millions, title Off, gridlines dotted `#243042`. X-axis: title Off, word wrap On.
- Title: fx ▸ Field value ▸ `PX WF Title`; Subtitle On ▸ fx ▸ `PX WF Subtitle`.
- Analytics pane ▸ Y-axis constant line ▸ Value fx ▸ `PX Limit End`, dashed amber `#E0A44B`, label "limit".
- How to read: Matured / New = net risk that left / arrived with trades; Revaluation = gross-risk change on trades held
  on both dates (prices, collateral value, haircut); Netting = net-risk change on held trades not explained by their
  gross risk (+ = offsetting trades gone); Non-repo = 16A minus repo net risk (derivatives, other).

### 4b. Answer cards `PX2` — Card (new) · 780 · 80 · 480 · 330
- Fields (order): `PX A Netting`, `PX A Haircut`, `PX A Underlyings`, `PX A NonRepo`, `PX A Volume`.
- Rename each in the Fields well: "Netting", "Haircut", "New underlyings", "Derivatives (non-repo)", "Volume".
- Layout: **1 card per row** (Cards ▸ Layout ▸ max cards per row 1), vertical; label **above** value, 10 pt muted;
  callout 14 pt.
- Callout value ▸ Apply settings to ▸ each series ▸ Font colour fx ▸ Field value ▸ the matching Colour measure
  (`PX A Netting Colour`, `PX A Haircut Colour`, `PX A Underlyings Colour`, `PX A NonRepo Colour`, `PX A Volume Colour`).
  Red = this pushes 16A up; green = not a driver; grey = no repo.
- Reference labels ▸ Apply settings to each series ▸ Add ▸ the matching Detail measure (`PX A … Detail`), 9 pt muted,
  position below the value. (Derivatives detail = `PX A NonRepo Detail`.)
- If Card (new) spaces them badly, fall back to five stacked cards (same recipe as P6a K-cards), 480 × 62 each.

### 4c. Daily trend `PX3` — line and clustered column chart · 20 · 420 · 740 · 280
- X-axis: `DIM_DATE[Date]`, Format ▸ X-axis ▸ Type **Categorical**, date format d mmm.
- Column y-axis: `PX T MtM` ("Repo MtM", colour `#2A3B52`). Line y-axis: `PX T Util` ("16A util", `#46B6C9`, 2 px),
  `PX T Limit` ("limit", `#E0A44B`, dashed), `PX T Net` ("repo net risk", `#C5CFDC`, dashed).
- Both axes display units Millions. Secondary axis On (lines), Title "€m". Legend top.
- Only file days of the window show (other dates are blank and drop out). Read: lines up while the MtM bars shrink toward
  0 = MtM moving to the client; a spike that reverses in 1–2 files = collateral timing.

### 4d. Collateral check `PX4` — Card (new) · 780 · 420 · 480 · 220, plus note `PX5` · 780 · 644 · 480 · 56
- (12 Nov f) MtM and notional count **started trades only** (forward-starting excluded), as market risk does: on the
  11 Nov test this gives repo 4.9bn / reverse repo 10.6bn = the risk note exactly. Net / gross risk keep all trades.
  Add to PX4: `PX Repo Notional End` "Repo notional", `PX RevRepo Notional End` "Rev. repo notional",
  `PX Fwd Notional End` "Forward-starting (not counted)".
- PX4 fields: `PX MtM Start` "Repo MtM start", `PX MtM End` "Repo MtM end", `PX MtM Matured` "… matured trades",
  `PX MtM Held` "… trades held", `PX MtM New` "… new trades", `PX Spot Start` "16A spot start", `PX Spot End` "16A spot end",
  `PX Collat End` "Collateral posted (est.)". Layout 2 per row, callout 13 pt, display units Millions, 1 decimal.
- PX5: Card (new) with `PX Collat Note`, 9 pt amber `#E0A44B`, label off.
- Convention: repo MtM negative = in our favour (as market risk quotes it). Spot = 16A MtM column (exposure after
  collateral). Collateral (est.) = spot − repo MtM, shown only when spot > €0.5m.

## 5. Wire and test the drill-through
1. Go to P6a ▸ movers table (it shows `CPH_Label`) ▸ right-click a CPH row ▸ **Drill through ▸ PX 16A Move**.
   The page opens for that CPH; the Back arrow (Ctrl+click in Desktop) returns.
2. **CPY test:** right-click a visual that shows `CPY Label` but not `CPH_Label` (e.g. the P1 entities table if it uses
   CPY Label, or a quick test table). If "Drill through" does **not** appear, Power BI wants both fields in that visual:
   then remove `CPY Label` from the well (CPH drill works everywhere), and for CPY drill duplicate the page
   (right-click tab ▸ Duplicate) with only `CPY Label` in its well. Flag which case you get.
3. Optional button on P6a: Insert ▸ Buttons ▸ Blank ▸ Action ▸ Type **Drill through** ▸ Destination **PX 16A Move**;
   text fx "Explain 16A move". It activates when a row is selected in a visual with the drill field.
4. Hide the page tab (right-click ▸ Hide page).
5. Performance Analyzer on the page for one fund and one large CPH; flag the times (the trade matching is the heavy part
   until the bake carries it).

## 6. Known limits
- Collateral is inferred (no collateral feed). Request: daily collateral posted / received / calls per GMRA / CSA.
- Repo scope = ALLREPO 07L, Sponsored excluded; per entity, not per agreement (market-risk notes are per GMRA).
- With Keep all filters On, a P1 date-range filter can cut the daily trend; if PX3 is empty, check the carried filters
  in the Filters pane.
