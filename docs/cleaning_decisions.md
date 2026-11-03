# Cleaning Decisions & Assumptions — Phase 2

> **Purpose:** a permanent record of every assumption and implementation decision made while cleaning the immoscout dataset, and *why* it was made. Written so that future-you (or a reviewer reading the repo) can trace any cleaning action back to its reasoning and its verified numbers.
>
> **Status:** living document — updated as each step of `notebooks/02_clean_data.ipynb` is completed.
> **Last updated:** 2026-11-03 (**Phase 2 COMPLETE** — Steps 1–7 executed, Run-All reproducibility verified, clean CSV saved and re-read from disk).

---

## 0. Ground rules for every decision in this file

1. **Every number is verified against `data/raw/immo_data.csv`** — nothing here is estimated from memory. When a number was checked with a direct pandas computation, the date of the check is noted.
2. **Cleaning ≠ analysis.** Step 3 removes only values that are *provably impossible* (a 0 m² flat, rent > total rent). Values that are merely *extreme* (a €2,500/mo flat — Munich exists) stay, because removing them would bias every city comparison made later.
3. **Missing ≠ impossible.** A blank cell is a missing-value problem (Step 4). A nonsensical value is an impossible-value problem (Step 3). The two are never mixed: `totalRent = NaN` survives Step 3 on purpose.
4. **No silent cleaning.** Every drop prints how many rows it removed, so the notebook output is an audit trail.

---

## 1. Dataset facts the decisions rest on

All verified 2026-09-16 → 2026-09-24 (Phase 1), re-verified 2026-11-03 where noted.

| Fact | Value | Consequence |
|---|---|---|
| Rows × columns | 268,850 × 49 | baseline for every %-loss figure |
| `scoutId` | unique on all 268,850 rows, 0 nulls | Step 2 dedupe is a documented no-op |
| Duplicate full rows | 0 | nothing to dedupe beyond `scoutId` |
| `regio1` == `geo_bln` | identical in every row (16 states) | drop `geo_bln` (Step 5) |
| `regio2` == `geo_krs` | identical (419 districts) | drop one twin (Step 5) |
| `regio2` semantics | **district**, NOT city (corrected in Phase 1) | `city` is built from `regio3` (Step 5) |
| `regio3` granularity | 8,684 unique values, thin groups | warn before group-by analysis |
| `date` | exactly 4 snapshots: Sep18, May19, Oct19, Feb20 | trend questions (plan Q6/Q8/Q9) are weak — reframe in Phase 3 |
| Encoding | clean UTF-8, no BOM, umlauts real (`Schüren`) | only `_` → space replacement needed (Step 5) |
| `baseRent` missing | 0 | usable as primary price column |

---

## 2. Decisions made (with reasoning)

### D1 — Keep the duplicate check even though it finds nothing (Step 2)

`scoutId` is unique, so `drop_duplicates(subset=['scoutId'])` removes 0 rows. **Decision: keep the code anyway.**

*Why:* the check is conditional — its answer *could* change if the dataset were re-downloaded in a newer version. A cleaning step is only pointless if its result cannot change the data. Removing the check would save nothing and lose the audit trail.

### D2 — Look-alike listings are NOT duplicates (checked, no action)

15,519 rows fall into 6,892 clusters sharing `(baseRent, livingSpace, noRooms, yearConstructed, geo_plz, regio3, date)` — e.g. 31 identical 3-room 63.57 m² flats in Delitzsch 04509 @ €350, each with its own `scoutId` and differing photo counts.

*Decision:* treat as **distinct units** (batch-uploaded landlord blocks), not duplicate records. *Why:* distinct `scoutId`s and differing `picturecount` suggest real listings; and impact is provably negligible — 0 of the 1,247 places with ≥ 50 listings have any single signature above 20 % of that place. *Caveat:* no column *proves* a re-list didn't happen, so this is "most likely", not "certain" — documented as a one-line limitation, not a cleaning action.

### D3 — Text encoding needs no repair (Step 5 scope)

The `�` seen in some console output is terminal rendering (mojibake), not bad data — `str.contains("\ufffd")` returns 0 matches.

*Decision:* no umlaut fixing; only `.str.replace('_', ' ')` + `.str.strip()` on location names.

### D4 — Fixed bounds, NOT 99th-percentile clipping (Step 3) ← *decided 2026-11-03*

Two candidate strategies for outlier removal:

| Approach | Would cut at | Effect |
|---|---|---|
| **Fixed bounds** (chosen) | rent 10–10,000 €, space 10–500 m², rooms 1–20 | removes only provably broken rows: **216** |
| 99th-percentile clipping | rent €2,500, space 180 m², rooms 5 | also removes the *real* top 1 % — expensive Munich/Schwabing flats |

*Why fixed bounds won:* the 99th percentile of `baseRent` (€2,500) is a completely plausible rent for Munich. Clipping there would delete legitimate luxury listings and systematically bias city comparisons downward. Percentile clipping remains available in Phase 3 as a *presentation* choice (medians, log scales) — but not as row deletion.

### D5 — The four logical-contradiction drops and their exact counts (Step 3a)

| Mask | Rule | Rows removed | Rationale |
|---|---|---|---|
| c1 | `baseRent > totalRent` AND `totalRent ≠ 0` | 215 | total = base + extras, so total < base is impossible. `totalRent = NaN` survives — NaN comparisons evaluate False, and missing ≠ contradictory |
| c2 | `baseRent == 0` AND `totalRent == 0` | 7 | a listing with no rent information at all |
| c3 | `noRooms == 0` | 0 | verified empty; check kept to guard future data reloads |
| c4 | `livingSpace == 0` | 72 | a 0 m² flat does not exist |

Subtotal: **294 rows**.

> ⚠️ Operator-precedence note: the first-draft mask1 (`& df['totalRent'] != 0` without parentheses) produced the identical 215-row result *by coincidence* of how `&` and `!=` bind against 0. The final code parenthesizes every comparison so correctness doesn't depend on luck.

### D6 — Rent mismatches are KEPT (Step 3b) ← *decided 2026-11-03*

`totalRent` should equal `baseRent + heatingCosts + serviceCharge`, but after 3a there remain **35,336** mismatching rows: **23,057** with a filled `totalRent` (of which **9,641** don't even match `baseRent + serviceCharge`) and **12,279** with missing `totalRent`.

*Decision:* keep all of them. *Why:* a total ≠ sum of parts is usually *legal* — the listing includes recurring costs the two component columns don't capture (garage, internet, furniture, gardening). Dropping ~35k rows (13 % of the dataset) for arithmetic purity would discard real listings and skew geographic coverage. The mismatch becomes an analysis-time consideration (prefer `baseRent` for cross-listing comparisons; use `totalRent` only where present), not a cleaning action.

### D7 — `totalRent` cap: bounded but missing values preserved (Step 3c)

`totalRent` is capped at €20,000/month — but **only** for rows where it is filled and non-zero: NaN and 0 pass through untouched.

*Why:* a €15.7 M monthly rent is a data error (placeholder/comedy entry) — 8 such rows removed. But NaN/0 are *missing-value* problems that belong to Step 4's strategy decision, so Step 3 must not pre-empt it.

### D8 — Step 3 outcome (verified end-to-end 2026-11-03)

| Stage | Rows removed | Running total |
|---|---|---|
| start | — | 268,850 |
| 3a contradictions | 294 | 268,556 |
| 3c bounds (rent/space/rooms) | 216 | 268,340 |
| 3c totalRent cap | 8 | **268,332** |

**Total removed: 518 rows = 0.19 %** → **99.81 % of the data survives.** The dataset was healthier than Phase 1's outlier drama suggested: only a few hundred truly broken rows.

### D9 — One dataframe going forward

After Step 3, `df` is re-pointed at the cleaned frame (`df = df_clean`). *Why:* the remaining steps (4–7) read a variable named `df`; carrying two frames invites editing the wrong one.

---

## 2b. Decisions made in Step 4 (2026-11-03)

### D10 — `totalRent`: keep as-is, `baseRent` becomes the primary price column (closes O1)

40,449 of 268,332 rows (15.07 %) have no `totalRent`, plus 226 have `totalRent = 0`. Options considered:

| Option | Rejected/chosen | Reason |
|---|---|---|
| **baseRent primary, totalRent untouched** (chosen) | ✅ | `baseRent` is 100 % complete; nothing fabricated; the 85 % subset where totalRent exists stays comparable gross-vs-net |
| Impute totalRent ≈ baseRent + serviceCharge (+ heatingCosts) | ❌ | heatingCosts is 68 % empty and gets dropped → imputed totals systematically too low for ~28k rows; invents data |
| Drop the 40,449 rows | ❌ | loses 15 % of listings, hurts small-city coverage, discards perfectly good baseRent data |

Consequence for Phase 3: **all price analyses use `baseRent`**; `totalRent` analyses carry a "85 % coverage" caveat.

### D11 — Fill strategy for the remaining 20 gapped columns (closes O2/O3)

- **Numerics → median** (not mean — skewed distributions): `yearConstructed` (56,838 → 1972), `serviceCharge` (6,782 → 135), `pricetrend` (1,830 → 3.39), plus the second-pass five: `floor` (51,133 → 2.0), `numberOfFloors` (97,507 → 3.0), `thermalChar` (106,203 → 107), `telekomUploadSpeed` (33,281 → 40), `yearConstructedRange` (56,838 → 3.0).
- **`serviceCharge = 0` (3,389 rows) treated as missing** and refilled with the median — a 0 € service charge is "not recorded", not "genuinely free".
- **Text → literal `'unknown'`** (10 columns): `heatingType` 44,724, `telekomTvOffer` 32,542, `firingTypes` 56,777, `houseNumber` 70,799, `condition` 68,328, `interiorQual` 112,432, `petsAllowed` 114,351, `streetPlain` 70,794, `typeOfFlat` 36,522, `description` 19,705, `facilities` 52,777. Chosen over most-frequent-value because it keeps missingness **visible** as its own category in charts and Tableau filters instead of blending it into the dominant answer.
- **`totalRent` is the only column that keeps NaN** (by D10). Final audit: `totalRent 40,445` is the sole entry.

### D12 — pandas 3.0 dtype lesson (implementation note)

The first text-fill pass matched **zero columns** because it tested `dtype == 'object'`. Under pandas 3.0.2 (this venv), string columns report dtype `str`, not `object`. Fix: detect text via `pandas.api.types.is_string_dtype()` (with an `object` fallback for 2.x compatibility). Lesson: **never assume dtype names — check them against the running version.**

---

### D13 — Dates: parse with the exact format, keep the 4-snapshot caveat (Step 5)

`date` parsed with `pd.to_datetime(format='%b%y')` → exactly **4** datetimes: 2018-09-01 (46,761), 2019-05-01 (75,889), 2019-10-01 (66,548), 2020-02-01 (79,134). Format is specified explicitly (not inferred) so the parse fails loudly if a future download changes shape. The 4-snapshot limitation for trend questions (plan Q6/Q8/Q9) stands — see §4.

### D14 — Location hierarchy: `state` ← `regio1`, `district` ← `regio2`, `city` ← `regio3`; twins dropped (Step 5, closes O4)

- Readable columns built with `_` → space + strip (no umlaut work needed, per D3): `state` = 16 uniques, `district` = 419, `city` = 8,681.
- Dropped: `geo_bln` (≡ `regio1`), `geo_krs` (≡ `regio2`), plus the raw `regio1/2/3` now superseded by the readable copies → **40 columns remain**.
- `district` is kept deliberately as the middle level: `city` (regio3) is too granular for reliable group-bys (D2-style thin groups), so Phase 3 gets state → district → city at three resolutions.

### D15 — `city` loses 3 values: 8,684 → 8,681 (verified non-issue)

Raw file has 8,684 distinct `regio3` values; the cleaned data has 8,681. Verified cause: **three tiny places had all their listings among the 518 rows removed in Step 3** (e.g. a hamlet whose only listing was a 0 m² row). The `_` → space renaming itself merges nothing (collision check on raw uniques returned empty). Honest, expected loss — no action.

---

### D16 — Feature engineering: `price_per_m2` unclipped; bins data-aware (Step 6, closes O6)

- `price_per_m2` = `baseRent / livingSpace`. Distribution: median **7.37 €**, mean 8.74, p95 17.48, max 416.67.
- **Unclipped by decision:** only 5 rows exceed 100 €/m² and 92 sit below 2 €/m². Clipping them would bend the headline metric; Phase 3 will use medians/quantiles that are robust to these few rows. The 92 ultra-cheap rows are a known artifact (tiny rent on large space), flagged not hidden.
- **Size bins:** `small < 40 · medium 40–80 · large 80–130 · xl 130+` m² → counts 26,070 / 158,260 / 70,180 / 13,822. Chosen over quartile bins (54/67/87) so the medium band covers the listing-market core and labels stay round and speakable in Tableau.
- **Room bins:** `1 · 2 · 3 · 4+` with edges 1.5/2.5/4 so 3.5-room listings count as `3 rooms` → counts 31,074 / 98,603 / 128,592 / 10,063.

### D17 — Step 7 safety net is a verified no-op; file saved and re-read (Step 7, closes O7 implicitly)

`dropna(subset=['baseRent', 'livingSpace', 'noRooms'])` removes **0 rows** (Steps 3–4 guarantee completeness) — kept as a cheap guard for future data versions. Final file: `data/processed/immo_data_clean.csv`, **268,332 × 43**, verified by reloading from disk: NaN total exactly **40,445** (`totalRent` only, per D10). `serviceCharge` kept with its median-filled values; the €25k-outlier question (O7) dissolves because `serviceCharge` is not used in any primary metric — noted for Phase 3 if it ever feeds a chart.

### D18 — Phase 2 headline (for README/methodology)

268,850 → **268,332 rows (99.81 % survive)**; 49 → **43 columns** (7 dropped for >60 % missing, 5 twin/superseded location columns, +3 engineered features). Cleaning was **conservative by design**: only provably impossible values removed; all extreme-but-plausible data retained and documented.

---

## 3. Open decisions (not yet made — listed so none is forgotten)

| # | Decision | Where it lands | Options on the table |
|---|---|---|---|
| O1 | ~~What to do with 40,449 missing `totalRent`~~ | ~~Step 4~~ | **Closed — D10**: `baseRent` primary, `totalRent` untouched |
| O2 | ~~Fill strategy for other missing numerics~~ | ~~Step 4~~ | **Closed — D11**: median fills (explicit list) |
| O3 | ~~Fill strategy for text columns~~ | ~~Step 4~~ | **Closed — D11**: literal `'unknown'` |
| O4 | ~~Drop twins~~ | ~~Step 5~~ | **Closed — D14**: `state`/`district`/`city` built, twins dropped |
| O5 | Keep granular `city` as-is, or also aggregate to district level | Phase 3 | `district` (419) already available as the robust middle level; decide per-chart |
| O6 | ~~Bins for `size_category` / `room_category`~~ | ~~Step 6~~ | **Closed — D16**: <40/40–80/80–130/130+ m²; 1/2/3/4+ rooms |
| O7 | ~~`serviceCharge` outlier bound~~ | ~~Step 7~~ | **Dissolved — D17**: not used in any primary metric; revisit only if it feeds a Phase 3 chart |

### Verified missing-value profile (post-Step-3, 2026-11-03)

27 of 49 columns have gaps. Drop-list candidates (> 60 %): `telekomHybridUploadSpeed` 83.26 %, `electricityBasePrice` 82.57 %, `electricityKwhPrice` 82.57 %, `energyEfficiencyClass` 71.05 %, `lastRefurbish` 69.98 %, `heatingCosts` 68.17 %, `noParkSpaces` 65.39 % — the same 7 columns Phase 1 identified, so the drop list is stable under cleaning. Note `heatingCosts` is > 60 % empty *and* part of the rent-arithmetic — see O2/O6 discussion when Step 4 runs.

---

## 4. Known limitations carried forward (for Phase 3 / README)

- **4 time snapshots only** (Sep18 / May19 / Oct19 / Feb20, unequal gaps): "trend" and "appreciation" claims are weak — plan questions 6/8/9 should be reframed as *snapshot comparisons*.
- **Look-alike listing blocks** (D2): at most a one-line caveat; impact measured negligible.
- **Rent mismatches** (D6): real-world extra costs not decomposable into the given columns.
- **99.81 % row survival** should be stated in the methodology doc so reviewers see the cleaning was conservative by design.

---

## 5. Where each decision lives in the notebook

| Decision | Notebook location |
|---|---|
| D1 dedupe | Step 2 markdown + code cell |
| D2 look-alikes | "Carried over" section A2 |
| D3 encoding | "Carried over" section A2 |
| D4 bounds strategy | Step 3 header + 3b/3c markdown |
| D5 contradiction drops | Step 3 code cell "3a" |
| D6 mismatch keep | Step 3 markdown "3b" |
| D7 totalRent cap | Step 3 code cell "3c" |
| D8 outcome table | Step 3 header (expected output) |
| D9 single frame | end of Step 3 code cell "3c" |
