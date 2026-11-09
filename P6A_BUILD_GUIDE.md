## 0. Before the start (10 min)

0.1 **Measures** in place: `P6A_MEASURES_TE2.csx` BUILD **09d** run and saved ("unchanged 140" on a rerun).
0.2 **Sort-by columns** (Table view; skip any already done): `P6W Compare[Window]` ▸ Order · `P6W Maturity Bucket[Bucket]`
    ▸ Order · `P6W Rating Map[Bucket]` ▸ Bucket Order · `P6W R Compare[Window]` ▸ Order · `P6W R Range[Range]` ▸ Order ·
    `P6W R Row[Row]` ▸ Order. Hide the Order / Days / Lo / Hi columns and `P6W Rating Map[Rating_ssj]`, `[Low Grade]`.
0.3 **Formats** on columns used as labels: `P6W AsOf[Date]` ▸ Format `d mmm yyyy`.
0.4 **New page.** Right-click the page tabs ▸ New page ▸ rename `P6 Hedge Fund Watch`. Canvas 16:9 (1280 × 720); colours
    from the theme.
0.5 **Page filter** (Filters pane ▸ Filters on this page): `DIM_COUNTERPARTY[HF Scope]` ▸ Basic ▸ tick **Hedge fund**.
    Lock it (padlock) and hide it (eye) — the A1 Scope slicer becomes optional (one value today, Q4). Keep A1 only if you
    want the scope visible; the measures enforce the scope anyway.
0.6 Selection pane on (View ▸ Selection).

---------------------------------------------------------------------------------------------------------------------
## 1. Rail and header shapes (5 min)

1.1 From **P1 Overview** copy `A0 Rail` and the nav buttons (`A1 Nav Overview` … `A5 Nav P5`) ▸ paste on P6 (same
    positions). Add a nav button for P6 under the last one (copy `A5 Nav P5` ▸ paste ▸ Y + 40 ▸ rename `A6 Nav P6`,
    text "P6" or the hedge icon) ▸ Action ▸ Page navigation ▸ `P6 Hedge Fund Watch`. Fill `#46B6C9` on P6, `#5E6E84` on
    the others. Paste the new `A6 Nav P6` on P1 and P5 too (Action → P6).
1.2 `B0 Header Back`: Rectangle · **60 · 8 · 1212 · 60** · fill `#1D2735`, border `#2C3A4D` 1 px, rounded 10 (or copy
    from P1).

---------------------------------------------------------------------------------------------------------------------
## 2. Header (20 min)

### A1 `A1 Scope` — 70 · 16 · 200 · 44 (optional, see 0.5)
- Button slicer `DIM_COUNTERPARTY[HF Scope]`, single select, Force selection. Selected fill `#46B6C9`, text `#0E141D`;
  header `Scope`. Hedge fund selected before saving.

### A2 `A2 Strategy` — 280 · 10 · 170 · 56
- Slicer (dropdown) `DIM_COUNTERPARTY[HF Strategy]`, multi-select, search on, header `Strategy (NAV report)`.
  Values include "Not in NAV report" and "No strategy given" (so in-scope entities can still be picked).
- Tooltip text (Format ▸ Header ▸ tooltip, or the slicer's description): "Strategy from the latest monthly NAV report".

### A3 `A3 As Of` — 460 · 10 · 160 · 56
- Slicer (dropdown) `P6W AsOf[Date]`, **Single select on**, sorted **descending** (⋯ ▸ Sort ▸ Date ▸ descending).
  Header `As of`. **Save with nothing selected** (= latest file). Never sync it with another page.

### A4 `A4 Source` — 630 · 16 · 160 · 44
- Copy P1's G2 source button (field `'P1 Source'[Source]`) ▸ paste ▸ retype position. Header `Source`. **CORTEX**
  selected before saving (Q1). Do not sync with P1 (each page keeps its own choice).

### A5 `A5 Compare` — 800 · 16 · 140 · 44
- Button slicer `P6W Compare[Window]`, single select, Force selection, 3 × 1, header `Compare`, **1W** selected.

### A6 `A6 Dates` — 950 · 10 · 314 · 56
- Card (new). Data `P6 AsOf Label`, `P6 NAV Label`. Callout 11 pt; the NAV value in amber `#E0A44B` (Callout ▸ per
  series colour). Labels off.
- Check: "Risk 4 Nov 2026 · latest" / "NAV 31 Aug 2026 · latest report on 4 Nov".

### B0n `B0n Excluded Note` — 70 · 60 · 1190 · 14 (inside the header band, bottom line)
- Card (new) or a text box with a dynamic value: `P6 Excluded Note`, 8 pt, `#8C9BB0`, no background.
- Check: "24 funds in 8 asset-manager envelopes excluded · €1,177m 16A (envelope held outside the HF scope)".
- If it crowds the header: delete it; the same text is in K1's tooltip.

**Checkpoint 1:** header row, CORTEX and 1W selected, A3 empty, dates card reads 4 Nov / 31 Aug.

---------------------------------------------------------------------------------------------------------------------
## 3. Top row: K1, K3, K4, K5, X1, X2 (45 min) — top row v2 (7 Nov)

Before: run `P6W_SETUP_PATCH_03.dax` (4 small tables) and measures build **09d** (or later). Card (new), Y **76**, H **88**, callout
24 pt (X1 22 pt), labels 9 pt muted, reference labels 9 pt. Old K2 (headroom) and K6 (repo limits) are now second lines
of K1 and K4.

| Card | Name | X · W | Callout | Label | Reference labels (in order) | Check (facts, 4 Nov) |
|---|---|---|---|---|---|---|
| K1 | `K1 16A Util` | 60 · 170 | `P6 16A Util` | 16A utilisation | `P6 K1 Detail` (colour fx `P6 Delta Colour 16A`), `P6 K1 Detail 2` | €443m · "▲ €11m vs 1W · 6%…" · "headroom €6.62bn" |
| K3 | `K3 CPHs Near` | 236 · 140 | `P6 K3 Text` | CPHs ≥ 80% / over | `P6 K3 Detail` | "0 / 0" |
| K4 | `K4 Repo Risk` | 382 · 176 | `P6 Repo Net Risk` | Repo net risk | `P6 K4 Detail`, `P6 K4 Detail 2` | €115m · "17A €39m · 17B €75m" · "▲ … · limits used 25%" |
| K5 | `K5 NAV Down` | 564 · 140 | `P6 K5 Funds` | label fx `P6 K5 Label` (or "NAV ≤ −5%") | `P6 K5 Detail` | 2 · "carry €1m of 16A util" |
| X1 | `X1 Volume` | 710 · 268 | `P6 X Notional` | **label off** (no title, 7 Nov) | `P6 X1 Line 1` · `P6 X1 Notional Δ Text` (colour fx `P6 X Δ Colour`) · `P6 X1 Deals Δ Text` (colour fx `P6 X Deals Δ Colour`) | see XC2 |
| X2 | `X2 Activity` | 984 · 288 | matrix, below | | | see XC3 |

- Reference-label layout: K1, K4 vertical (2 lines). X1: line 1 full width, then the two Δ labels side by side (titles
  "notional" / "deals", 9 pt). If Card (new) will not place them that way, put both Δ into one text measure and drop the
  colours (flag it; I add the measure).
- K1 tooltip well: `P6 K1 Tooltip`. K5 threshold slicer as before (hidden).

### Display units: **None** everywhere on P6 (fixes "€443.4Mm", "€114.7,,Mm", "€38.0,,,bnbn")
The P6 measures already scale and carry their unit (format `"€"#,0.0,,"m"` → €443.4m). A visual set to Auto / Millions
scales a second time and adds its own "M". In every card callout, card reference value and table / matrix column:
Format ▸ … ▸ **Display units ▸ None** (Card (new): Callout value ▸ Values ▸ Display units; Table: Specific column ▸
Display units, or Values ▸ Display units for all). Decimals: Auto. Also turn **Totals off** on M (the total row shows a
meaningless rating "B+ ↓" and 06 "R").

### Stacked cards (pixel control; use when Card (new) spacing will not behave) — 9 Nov
Card (new) spreads its reference labels to the bottom of the card and, in tabular layout, puts a second field beside the
first. Instead, build each top-row card from three plain pieces, all at the card's X, aligned left:

| Piece | Visual | Y · H | Content | Settings |
|---|---|---|---|---|
| a | Shape ▸ Rounded rectangle | 76 · 88 | — | fill `#1D2735`, border `#2C3A4D` 1 px, radius 10. Name `Kx Back`. |
| b | Card (new) | 78 · 46 | **one** field: the callout measure | Label (category) on = the card title, 9 pt muted, **above**; callout 24 pt; display units None; background **off**; padding 8 left, 2 top. |
| c | Card (new) | 124 · 38 | the reference **text measures**, as separate fields | **Layout ▸ vertical, 1 card per row**, label (category) **off**, callout 9 pt, padding 0 left 10, spacing 0; per-series colour fx where listed; background off. |

Pieces b and c sit on top of a (Selection pane: c, b above a). Group them (Ctrl+click ▸ right-click ▸ Group ▸ name `K1`).
Fields for piece c:
- K1: `P6 K1 Detail` (colour fx `P6 Delta Colour 16A`), `P6 K1 Detail 2`.
- K3: `P6 K3 Detail`. K5: `P6 K5 Detail`.
- K4: `P6 K4 Detail`, `P6 K4 Detail 2` (one callout only in b: `P6 Repo Net Risk`; the 17A / 17B split is text, not a
  second callout — that is what pushed it to the right in tabular layout).
- X1 (title off in b, callout 22 pt, b at Y **98** so the two slicers fit above it): piece c = `P6 X1 Line 1`, then
  `P6 X1 Notional Δ Text` (colour fx `P6 X Δ Colour`) and `P6 X1 Deals Δ Text` (colour fx `P6 X Deals Δ Colour`).
  These now carry their own words ("notional +13%", "deals +25%", build 09d), so no label titles are needed. For
  "notional" and "deals" on one line, make piece c **two** cards: c1 (Y 124, H 18) `P6 X1 Line 1`; c2 (Y 142, H 18) the
  two Δ fields with **2 cards per row**.
- X1 sparkline: keep it in piece b's image slot (it works) — Image ▸ position Right, size 104 × 26.

Callout colour: piece b ▸ Callout value ▸ Font colour fixed teal (K1, K4), amber (K5) — or fx as you had it.

### K4 tooltip page `P6 TT Repo Limits` (15 min)
1. New page ▸ rename `P6 TT Repo Limits` ▸ Page information ▸ **Allow use as tooltip** ▸ Canvas type **Tooltip**
   (320 × 240). Hide the page.
2. `TT1 Repo Trend` — Line chart · 8 · 8 · 304 · 170: X `DIM_DATE[Date]` (continuous), Y `P6 K4T 17A Used %` ("17A",
   teal), `P6 K4T 17B Used %` ("17B", violet). Y axis 0 %–auto, format `0%`. Visual filter `DIM_DATE[Date]` relative
   date: last 6 months (the measures blank everything outside the 90 days to as-of). Title "Repo limits used · 90 days".
3. `TT2 Repo Legend` — Card (new) · 8 · 184 · 304 · 48: `P6 K4T Legend`, 9 pt, label off.
4. Page filter `DIM_COUNTERPARTY[HF Scope]` = Hedge fund (as P6).
5. Back on P6 ▸ K4 ▸ General ▸ Tooltips ▸ Type **Report page** ▸ `P6 TT Repo Limits`.

### X1 controls (laid over the card's top row)
- `X1a Product` — Button slicer · **732 · 81 · 136 · 18**: field `P6W Activity Product[Code]` (sorted by Order), single
  select, Force selection, 6 × 1, 8–9 pt, padding 0, styled as A5. **All** selected before saving. Tooltip text:
  "All = Rates + FX + Credit · Rt Rates · Rp Repo (17A) · RR Rev repo (17B) · FX · Cr Credit".
- `X1b Window` — Button slicer · **874 · 81 · 98 · 18**: field `P6W Activity Window[Label]`, single, Force selection,
  4 × 1, header off; type "wk" as a text box at 860 · 81 if you want the unit shown. **1** selected before saving.
- Selection pane: X1a, X1b above X1 and X1s.
- **Sparkline.** First try Card (new) ▸ Image ▸ on ▸ Image URL ▸ fx ▸ Field value ▸ `P6 X1 Sparkline` ▸ position Right,
  size 104 × 26. If it does not render, or pushes the reference labels: image off, and add `X1s Sparkline` — Table ·
  **866 · 104 · 104 · 30**: column `P6 X1 Sparkline` (renamed to a single space), Image size 92 × 26, header font 1 pt in
  `#1D2735`, grid / borders / background off, totals off. Interactions from X1s: None.
- X1 tooltip: report page `P6 TT Tenor` (below).

### X2 `X2 Activity` — Matrix · 984 · 76 · 288 · 88
1. Rows `P6W X2 Row[Row]`, Columns `P6W X2 Product[Product]`, Values `P6 X2 Cell`. Row / column subtotals **off**.
2. Cell elements ▸ Font colour ▸ fx ▸ Field value ▸ `P6 X2 Cell Colour`. Font 9 pt, row padding 0, column headers 9 pt
   muted, row headers 9 pt muted. Widths: row header 58, each column 50.
3. Title on, "Activity by product", 9 pt muted; Subtitle fx `P6 X2 Subtitle` ("1W vs 12-wk avg · to 3 Nov"). If the
   three rows do not fit in 88 px: subtitle off first, then title off (the card frame shape can carry a text box).
4. Background `#1D2735`, border `#2C3A4D`, rounded 10 (so it reads as a card).
5. Tooltip: report page `P6 TT Tenor`.

### Tooltip page `P6 TT Tenor` (10 min)
- New page, tooltip canvas (320 × 240), hidden. `TT3 Tenor Trend` — Line chart · 8 · 8 · 304 · 200: X `DIM_DATE[Date]`
  (continuous), Y `P6 XT Tenor` ("new-deal tenor, years"), teal. Visual filter on `DIM_DATE[Date]`: last 9 months.
  Title fx `P6 X1 Footnote`. Page filter HF Scope = Hedge fund.
- The hovered X2 column passes its product to the page (tooltip pages receive the hovered cell's filters); hovering X1
  uses the X1a slicer.

### Interactions for the top row
X1a, X1b → every visual except X1 / X2 / X1s: **None**. X1a → X2: None (X2 has its own products). M / N / C1 clicks → X1,
X2: **Filter** (activity for the clicked CPH). Everything else as §10.

**Checkpoint 2:** the top row on CORTEX and on Facts; click X1a through All → Cr and X1b 1 → 8; hover K4 and an X2 cell.

---------------------------------------------------------------------------------------------------------------------
## 4. M Who moved (25 min)

### M `M Movers` — 60 · 172 · 764 · 272
1. Insert ▸ **Table**. Columns, in order, renamed in the well:
   `DIM_COUNTERPARTY[CPH_Label]` → "CPH" · `P6 M Rating` → "Rating" · `P6 16A Util` → "16A util" · `P6 16A Util %` →
   "Util %" · `P6 M Delta` → "Δ window" · `P6 M 06 Status` → "06" · `P6 17A Util` → "17A" · `P6 17B Util` → "17B" ·
   `P6 NAV 1M` → "NAV 1M" · `P6 NAV YTD` → "NAV YTD" · `P6 M Covenant` → "Cov.".
2. Filters ▸ this visual: `CPH_Label` ▸ Basic ▸ untick **(Blank)**; then Filter type **Top N** ▸ Top **8** ▸ By value
   `P6 M Delta Abs` ▸ Apply. Sort "Δ window" descending.
3. Display units **None** on every numeric column (see §3). Cell elements: "Util %" font colour fx `Fmt RAG Colour 16A` (P1 measure; if it does not exist, use `P6 M Stripe
   Colour`) · "Δ window" font colour fx `P6 Delta Colour 16A` · "06" font colour fx `P6 M 06 Colour` · "Cov." font
   colour fx `P6 M Covenant Colour` · "CPH" **background** fx `P6 M Stripe Colour`.
4. Formats: "16A util", "Δ window", "17A", "17B" display units **None** (the measures show €…m) · "Util %" `0%` · NAV columns
   `+0.0%;-0.0%`. 9 pt, row padding 2, totals **off**, word wrap off. Widths: CPH 170, others 52–62.
5. Title `Who moved`. Subtitle fx ▸ `P6 16A Source` (8 pt muted) — tells which source the 16A columns show.
- Check (facts, 1W): Capula, Welwing, Bridgewater, Millennium near the top; Millennium "Review" (amber), NISA "Review".
  NAV columns blank for funds not in the US NAV report (Capula, Bridgewater, …): expected.

---------------------------------------------------------------------------------------------------------------------
## 5. N NAV vs our exposure (20 min)

### N `N NAV Scatter` — 832 · 172 · 440 · 272
1. Insert ▸ **Scatter chart**. Values `DIM_COUNTERPARTY[CPH_Label]` · X `P6 N NAV YTD` · Y `P6 N Util Over NAV` ·
   Size `P6 N Util`. Play axis empty.
2. Markers ▸ Colour ▸ fx ▸ Field value ▸ `P6 N Colour`. Tooltips well: `P6 N Tooltip`.
3. X axis −40 % … +60 % (fixed, format `+0%`); Y axis 0 … auto, format `0.0%`. Analytics (magnifier) ▸ **X-axis
   constant line** 0, dashed slate · **Y-axis constant line** ▸ fx ▸ `P6 N Util Over NAV P75`, amber, label
   "75th pct".
4. Filters ▸ this visual: `CPH_Label` not (Blank); `P6 NAV Cur USD` is not blank.
5. Title `NAV vs our exposure`. Subtitle fx `P6 N Subtitle` (names the metric).
6. **N1 `N1 Metric`** — 1020 · 178 · 240 · 22: Button slicer `P6W N Metric[Metric]` (sorted by Order), single select,
   Force selection, 5 × 1 (16A · 06 · 17A · 17B · Net repo), 8 pt, styled as A5. **16A** selected before saving. Selection pane: N1 above N. Interactions:
   None on every other visual (it only drives the N measures). Y axis: back to **auto** (17A / 17B ratios are far larger
   than 16A's).
- Check: 18 dots; NISA highest (1.5 % of NAV), most below 0.1 % — the Y range is small: try Y max 2 % fixed if the
  dots crowd at the bottom; BlackRock GEST large and far right (YTD +55 %).

**Checkpoint 3:** top half of the page (cards, M, N). Click a CPH in M: N highlights it.

---------------------------------------------------------------------------------------------------------------------
## 6. T HF PFE vs limit (15 min)

### T `T PFE Trend` — 60 · 452 · 292 · 260
1. Insert ▸ **Line chart**. X `DIM_DATE[Date]` (Type **Continuous**). Y: `P6 T Util` ("16A util"), `P6 T Limit`
   ("Limit"), `P6 T NAV Marker` ("NAV month"), `P6 T Last Marker` ("As of").
2. Lines: Util teal 2 px, **Shade area** on (transparency 80 %) · Limit slate dashed 1 px · NAV month: line width 0,
   markers on, amber, size 6 · As of: width 0, marker teal, size 8.
3. Y axis display units Millions/Billions auto, start 0. X axis no title. Legend off (the subtitle explains).
4. Filters ▸ this visual: `DIM_DATE[Date]` ▸ Relative date ▸ is in the last **36 months** (keeps the axis query small;
   the measures blank everything outside the 12 months to the as-of date).
5. Title `HF PFE vs limit`. Subtitle fx `P6 T Subtitle`.
- Check: no step between 23 and 26 Oct 2026 (fixed in 06e); last point 4 Nov €443m, limit ≈ €7.06bn.

---------------------------------------------------------------------------------------------------------------------
## 7. C Headroom by CPH / Maturity of live trades (25 min)

### C1 `C1 Headroom By CPH` — 360 · 452 · 272 · 260
1. Insert ▸ **Stacked bar chart**. Y `DIM_COUNTERPARTY[CPH_Label]`. X: `P6 C1 Util` ("Used"), `P6 C1 Over Limit`
   ("Over"), `P6 C1 Headroom` ("Headroom"). Colours teal / coral / slate.
2. Filters ▸ this visual: CPH_Label not (Blank); Top N **12** by `P6 C1 Util`. Sort by `P6 C1 Util` descending.
3. Data labels: on for "Used" only ▸ Value ▸ custom field `P6 C1 Util % Label`. *Fallback:* labels off, % in tooltip.
4. Title `Headroom by CPH`, subtitle "16A · as of" + the as-of date (static subtitle "16A utilisation and headroom").

### C2 `C2 Maturity` — 360 · 452 · 272 · 260 (same place, hidden by default)
1. Insert ▸ **Stacked column chart**. X `P6W Maturity Bucket[Bucket]` (sorted by Order). Legend
   `DIM_PRODUCTLINE[Family]`. Y `P6 C2 PFE Proxy` ("SA-CCR proxy"). Colours per family as P5-W (FX teal · Rates violet
   · GRI&T green · Credit & securitisation coral · Equity amber · Other slate).
2. Tooltips well: `P6 C2 Notional`, `P6 C2 Deals`. Y axis display units Billions.
3. Title `Maturity of live trades (estimate)`. Subtitle fx `P6 C2 Subtitle`.
- Check: 10Y+ and 5-10Y rates dominate (≈ €10bn and €11.7bn proxy); total ≈ €47bn (proxy, not 16A).

### Cb `Cb C Switch` — 470 · 458 · 154 · 22
1. Bookmarks (View ▸ Bookmarks): show C1 / hide C2 ▸ Add ▸ `C Headroom`; hide C1 / show C2 ▸ Add ▸ `C Maturity`. For
   both: ⋯ ▸ **Data unticked**, Display ticked, Current page ticked, **Selected visuals** (select C1 + C2 first) ▸ Update.
2. Insert ▸ Buttons ▸ Navigator ▸ **Bookmark navigator** ▸ show only these two (Format ▸ Bookmarks ▸ group or tick),
   2 × 1, 8 pt, selected fill teal. Rename tiles "Headroom" / "Maturity" (bookmark names).
3. Leave **C Headroom** selected before saving. Selection pane: Cb above C1 and C2.

---------------------------------------------------------------------------------------------------------------------
## 8. R Repo collateral (35 min)

### R1 `R1 Collateral Mix` — 640 · 452 · 352 · 190
1. Insert ▸ **100 % stacked bar chart**. Y `P6W R Row[Row]` (sorted by Order). Legend `P6W Rating Map[Bucket]` (sorted
   by Bucket Order). X `P6 R1 Collateral`.
2. Colours: A teal · B violet · C slate · D `#B7A27A` · D- and below amber · No bond detail `#5C6B80`.
3. Data labels on (share), 8 pt, `#0E141D`, hide below 5 % if offered. Legend top, 8 pt.
4. Title `Collateral received (17B)`. Subtitle fx `P6 R Subtitle`.
- Check: As of A 64 % · B 19 % · C 17 %; Compare (3M) A 63 % · B 18 % · C 19 %.

### R1a `R1a Compare` — 650 · 486 · 200 · 22
- Button slicer `P6W R Compare[Window]`, single select, Force selection, 5 × 1, 8 pt, **3M** selected. Above R1.

### R1c `R1c Cards` — 640 · 642 · 352 · 70
- Card (new), 3 values: `P6 R Wtd Haircut` ("Wtd haircut", reference `P6 R Haircut Delta`) · `P6 R Top Issuer Share`
  ("Top issuer", reference `P6 R Top Issuer Delta`) · `P6 Repo Net Risk 17B` ("17B net risk", reference
  `P6 R 17B Risk Delta`). Callout 14 pt, label 8 pt.
- Check: 0.34 % (+0.07pp) · 18 % (−1pp) · €75m (+€20m).

### R2 `R2 Collateral Over Time` — 640 · 452 · 352 · 190 (hidden by default)
1. Insert ▸ **100 % stacked area chart**. X `DIM_DATE[YearMonth]` (Categorical). Legend `P6W Rating Map[Bucket]`.
   Y `P6 R2 Share`. Colours as R1. Tooltips well `P6 R2 Haircut`.
2. Filters ▸ this visual: `DIM_DATE[Date]` ▸ on or after **1 Jan 2023**.
3. Title `Collateral over time`. Subtitle fx `P6 R2 Subtitle` ("Rated C or lower … over 2Y · rose in n of 24 months").

### R2a `R2a Range` — 650 · 486 · 230 · 22 (hidden by default)
- Button slicer `P6W R Range[Range]`, single, Force selection, 5 × 1, 8 pt, **2Y** selected.

### R3 `R3 Collateral vs NAV` — 640 · 452 · 352 · 190 (hidden by default)
1. Insert ▸ **Line and clustered column chart**. X `DIM_DATE[YearMonth]`. Column `P6 R3 NAV 1M` ("NAV 1M"). Line
   `P6 R3 Low Grade Share` ("Rated C or lower", secondary axis).
2. Columns ▸ Colour ▸ fx ▸ `P6 R3 NAV Colour`. Line amber 2 px, markers on.
3. Filters ▸ this visual: `DIM_DATE[Date]` ▸ on or after 1 Jan 2025 (the measures blank months outside the 12 NAV months).
4. Title `Collateral vs NAV`. Subtitle fx `P6 R3 Subtitle`.
- Check: all hedge funds, corr ≈ −0.10 (no visible link at book level); click a CPH in M to see one fund's months.

### Rb `Rb R Switch` — 800 · 458 · 186 · 22
1. Bookmarks `R Mix` (R1, R1a, R1c shown; R2, R2a, R3 hidden) · `R Over time` (R2, R2a, R1c shown) · `R vs NAV` (R3,
   R1c shown). Each: Data **unticked**, Display ticked, Selected visuals = R1, R1a, R1c, R2, R2a, R3 ▸ Update.
2. Bookmark navigator with these three, 3 × 1, 8 pt. **R Mix** selected before saving. Above R1–R3.

**Checkpoint 4:** C (both views) and R (three views).

---------------------------------------------------------------------------------------------------------------------
## 9. V Covenant & review (15 min)

### V `V Covenant` — 1000 · 452 · 272 · 260
1. Insert ▸ **Table**. Columns: `FACT_HF_NAV[Fund_Name]` ("Fund") · `P6 V Issue` ("Issue") · `P6 NAV 1M` ("NAV 1M") ·
   `P6 V Since` ("Since", format `mmm yy`).
2. Filters ▸ this visual: `P6 V Has Issue` is **1**. Sort by `P6 V Severity`: add it as a column, sort descending,
   then set its width to 0 (or hide via Format ▸ Specific column ▸ width 0).
3. "Issue" font colour fx `P6 V Colour` (coral breach · amber NAV / DD / 3-negative · slate validity soft).
4. 8–9 pt, word wrap on for Fund, totals off. Title `Covenant & review`. Subtitle fx `P6 NAV Label`.
- Check: Market Advantage "NAV ≤ -10 % 1M" first (−34.5 %), Capstone Alternative Risk "NAV ≤ -5% 1M", then the
  "DD > 12 months" block (amber), "Validity passed (soft)" last (slate).

---------------------------------------------------------------------------------------------------------------------
## 10. Interactions (10 min)

Format ▸ **Edit interactions**. F = Filter, H = Highlight, None = ⊘.

| Source → | K1–K6 | M | N | T | C1/C2 | R1–R3, R1c | V |
|---|---|---|---|---|---|---|---|
| A2 Strategy | F | F | F | F | F | F | F |
| A3 As of, A4 Source, A5 Compare, R1a, R2a, threshold | measures only (disconnected) — leave as set |
| M row click | None | – | H | F | F | F | F |
| N dot click | None | F | – | F | F | F | F |
| C1 bar click | None | F | H | F | – | F | F |
| V row click | None | None | None | None | None | F | – |
| T, C2, R1, R2, R3 clicks | None everywhere |

A6, B0n = None from every source. Edit interactions off.

---------------------------------------------------------------------------------------------------------------------
## 11. Final checks (15 min)

11.1 **Layer order** (top first): `Cb`, `Rb`, `R1a`, `R2a` · everything else · `B0 Header Back` · `A0 Rail`.
11.2 **Numbers on Facts, 4 Nov:** K1 €443.4m · K2 €6.62bn · K4 €114.7m · K5 2 · K6 25 % · M top 8 by |Δ| · R1c 0.34 % ·
     V Market Advantage first. **CORTEX:** K1 ≈ €440m, A6 unchanged.
11.3 **As of 23 Oct 2026** (A3): exclusion note "25 funds … €1,275m"; T ends on 23 Oct, no step; NAV label still Aug.
     **As of 1 Mar 2026**: NAV label "31 Jan 2026"; CORTEX falls back to facts (M subtitle "facts (no CORTEX figure)").
     Clear A3 again before saving.
11.4 **Speed:** View ▸ Performance analyzer ▸ Start recording ▸ Refresh visuals. Target ≤ 2,000 ms per visual. Likely
     heaviest: M (rating + 06 status per CPH), N (P75 line), C2 (live Sales deals), K3. Flag the list whatever it shows.
11.5 **Text:** nothing below 8 pt (subtitles) / 9 pt (everything else).

**Checkpoint 5:** the full page + Performance analyzer list.

---------------------------------------------------------------------------------------------------------------------
## If something does not work
| Symptom | Likely cause | Fix |
|---|---|---|
| Every card blank | A3 saved with a date that has no 16A file, or the page filter 0.5 missing | clear A3; check 0.5 |
| K1 differs CORTEX vs facts by a lot | CORTEX has no row for some funds | expected for dates before 29 May 2026; else flag the CPHs |
| M shows (Blank) row | visual filter on CPH_Label missing | §4 step 2 |
| N empty | `P6 NAV Cur USD` filter set to "is 0" | set "is not blank" |
| T shows a step on a quiet day | a fund entered / left an asset-manager envelope (exclusion is per day) | check `P6 Excluded Note` on both dates |
| C2 and C1 both visible | bookmark Display state not updated | redo §7 Cb with the right visibility, ⋯ ▸ Update |
| R2 blank | P6W R Range not selected / date filter | select 2Y; §8 R2 step 2 |
| Error icon on a visual | a measure broke | `EVALUATE FILTER(SELECTCOLUMNS(INFO.MEASURES(),"Measure",[Name],"Error",[ErrorMessage]),[State]<>1)` and flag it |
| Visual > 2 s | — | flag the Performance analyzer list |