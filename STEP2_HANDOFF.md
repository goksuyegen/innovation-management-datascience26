# Step 2 · Competitive landscape · Handoff document (Surface drones)

> **Read this first if you are a new agent/chat.** This file contains everything needed to continue Step 2 of the
> Innovation Management project work: the requirements (from the kickoff slides), the theory to cite (from the
> lecture slides), what is already implemented in `work/11_exercise.ipynb` and with which results, the decisions
> taken and why, and a detailed, ordered to-do list with specifications.
>
> It replaces `STEP2_GUIDE.md`, which was written for a different sector (quantum computing).
>
> Last updated: 2026-11-10.

---

## 0. How to work with the user (very important)

- **The user wants to learn, not to receive a finished project.** Do NOT edit the notebook on your own initiative.
  Suggest code **in chat**, explain each part (what it does, why), and let the user type it into the notebook and
  run it. Edit files only when the user explicitly asks ("fix it", "do it").
- **Go in small steps**: one cell or idea at a time; ask the user to run it and share the output.
- **The notebook runs only on EPO TIP** (PATSTAT is not reachable locally). You cannot run it. After the user runs and
  saves (`Ctrl+S`), you can **read the outputs from the saved `.ipynb` file**.
- User background: knows computer science and notebooks; new to PATSTAT, patents and Jupyter kernels. Explain patent
  concepts; you don't need to explain basic Python.
- Notebook hygiene rules already agreed:
  - after changing an early cell: **Restart Kernel → Run All**, then check;
  - the **summary cell stays the last cell** (it uses variables created above it);
  - cells that **build** data and cells that only **check** data are kept separate;
  - hand-made corrections live in dictionaries (`NAME_MERGES`, `TYPE_FIXES`, `COUNTRY_FIXES`) with a comment
    "checked by hand".
- Before suggesting a step, predict the expected result (e.g. "CR4 should be ≈ 8.2%") so the user can check it.

---

## 1. The project in one page

**Course:** Innovation Management, Politecnico di Torino, A.Y. 2026/27 (Prof. Grazia Sveva Ascione; tutor Dr. Giacomo
Masali, giacomo.masali@polito.it, max 2 × 20-min Teams meetings per group, book 24 h ahead, email questions first).

**Scenario:** the team are consultants at an investment bank. Sector: **Surface drones (unmanned surface vessels,
USVs)**. The bank's client for this sector is **STX France** (an established shipbuilder looking for growth). The
client's three questions:
1. How is the sector doing overall?
2. Which segments are growing, and which are fading?
3. **Who are the emerging players to buy or partner with?**

**Deliverables, all due Sunday 20 December 2026 (hard deadline):**
- **Deck PDF** `TeamXX_Sector_deck.pdf`: **20 slides** + technical appendix (11 pt), **≤ 10 figures and tables in
  total**. Title slide: team number, sector, members with student IDs, repo URL and commit hash. Consistent citation
  style; contribution statement; statement on how generative AI was used.
- **GitHub repo** with the full pipeline (tag `v1.0-submission`). Suggested structure:
  ```
  team-XX-sector/
    README.md            question, how to run, results
    requirements.txt     pinned versions
    config/sector.yaml   (config, not hard-coding!)
    src/01_extract.py    SQL queries run on TIP
    src/02_clean.py      families, applicants, dates
    src/03_landscape.py  Steps 1–2   <-- Step 2 code ends up here
    src/04_present_score.py, 05_future_score.py, 06_quadrant.py
    notebooks/           exploration only
    tests/               unit tests for indicators
    outputs/figures/ outputs/tables/
  ```
  Do not commit bulk PATSTAT extracts; commit the queries.
- **Pitch video** `TeamXX_Sector_pitch.mp4`, ≤ 10:00, every member speaks, no code on slides.

**Grading (15 points):** 20% data & code quality · 25% landscape/trajectory/market-opportunity analysis · 20%
valuation methodology · **20% integration with lecture topics** · 15% presentation quality.

**Pipeline of the project:** Step 0 dataset → Step 1 describe the field → **Step 2 map competition** → Step 3 present
score (influence, volume, success, globalization) → Step 4 future score (own algorithm) → Step 5 Magic Quadrant →
Step 6 recommendation (acquire or partner, core competences, risks).

---

## 2. Step 2 requirements (kickoff slide 12, verbatim content)

*"Who is competing, how concentrated the field is, where the action is, and which players deserve to be scored."*

| Question | How (from the slide) |
|---|---|
| Q1 How concentrated is the field, and is it consolidating? | Herfindahl–Hirschman Index (HHI), or others from the literature |
| Q2 Who are the incumbents, and who are the new entrants? | New applicants per year (**they never patented before**) and their share of families + **rate of disappearance** |
| Q3 Which subfields are growing fastest? | Growth of CPC groups, **or topics from abstracts (embeddings + clustering, topic models)** |
| Q4 Which political, economic, social and technological forces shape it? | **PEST analysis** |

**In the deck (suggestions):**
- Table: **top applicants, with type (firm, start-up, university) and country**
- Figure: **concentration and entry over time**
- Figure: **subfield growth map**
- Table: **PEST analysis (MANDATORY)**

Step 2 also has a **purpose for later steps**: "screen the players worth scoring" in Step 3. The top-applicants table is
the shortlist for Steps 3–6.

Rules from Step 0 that still apply: unit = **DOCDB family**; time = **earliest priority year**; applicants: harmonise
names (PSN/HAN + **own rules for subsidiaries**); **truncation**: the last ~3 years are incomplete (18-month publication
lag): flag them, do not read them as a decline.

---

## 3. Theory to cite (20% of the grade is "integration with lecture topics")

Lecture slides are in `c:\Users\fqsod\Downloads\Material (1)\IM_Theory_0..5_*.pdf`; reference documents in
`useful_material/`.

### Theory 3 · Patent intelligence and patent landscapes (most relevant)
- **Define the user before the search**: a landscape is designed around its user. Our user = STX France (acquire or
  partner). Every Step 2 slide should answer something for that user.
- Landscape template (WIPO report): **data → perimeter → indicators → actors**. Step 2 = indicators + actors.
- "Who" = applicants/owners; technique = **the 'name game'**: entity disambiguation and **consolidation of the ultimate
  owner**. WIPO consolidates to the ultimate owner (M&A, reassignments) → justifies merging subsidiaries (CSIC).
- What a landscape measures on **competitors**: portfolios, international extension (family size), size and
  obsolescence, **collaborations (co-assignments)**, specialization, transactions (reassignments).
- **International families** (protection sought beyond the home office): "a proxy for quality and value" and they
  "reduce national biases: about 48% of all active families are filed in one authority only, roughly half of all
  families are China-only" (WIPO 2024, Appendix A.3, Fig. 26).
- **Innovation Maturity Matrix** (WIPO 2024, App. A.4; method by IPOS International):
  - y = innovation intensity (number of families, log scale);
  - x = relative recency: `R = Σ_i (w_i · i) / (n · Σ_i w_i)`, with i = 1 for the first year, n = number of years,
    w_i = filings in year i; **relative recency = R of the subfield / R of the whole sector**;
  - quadrants: **current hot topics** (many, recent), **emerging interest** (few, recent), **mature sectors** (many,
    old), **modest development** (few, old).
- Search strategy = a classification problem (perimeter); "every indicator is a modelling choice"; patents measure
  inventive activity, not innovation; propensity to patent differs by sector; value is skewed.

### Theory 2 · IPR strategic choices
- **Practicing entity (PE)**: makes/sells products based on its patents (patents = exclusion).
  **Non-practicing entity (NPE)**: owns patents but does not produce (patents = revenue from licensing/sale).
- **Universities and public research organisations are NPEs** (earn via licences and spin-offs; mission = knowledge
  transfer). **Individual inventors are NPEs too.**
- Use: in our sector the top applicants are mostly Chinese universities → inventions come mostly from NPEs →
  for STX France, universities are **licensing/partnering** sources, practicing firms and start-ups are possible
  **acquisition** targets.
- Patent pools can keep new entrants out (anti-competitive) — only if relevant.

### Theory 1 · Patents, history and filing
- EPO benchmark of who files: **72% large enterprises, 18% SMEs and individual inventors, 10% universities and
  public research**. Compare our sector's family shares by applicant type with this benchmark (a much higher
  university share = young, academic, pre-commercial field).
- Applicant = who files/owns; inventor = who invented (we use applicants, `applt_seq_nr > 0`).

### Theory 0 · Types of IPR, appropriability
- Appropriability problem; **public intervention**: public R&D funding of universities (Samuelson), subsidies/tax
  credits (Pigou), **public procurement (e.g. defence, health)**, **prizes (e.g. DARPA Grand Challenge)**; private
  mechanisms: IPRs, secrecy, lead time, complementary assets. → anchors the **Political** and **Economic** columns of
  PEST (naval/defence procurement of USVs, state-funded university research in China).
- Concern: patents can create excessive concentration of monopoly power (link to Q1).

### Theory 4 · Knowledge spillovers
- Innovation concentrates geographically (clusters; Marshall–Arrow–Romer, Porter, Jacobs; tacit knowledge, density).
  → optional remark: our top applicants cluster in Shanghai (3 of top 10), Zhejiang (2), Harbin.

### Theory 5 · Patent valuation
- Universities and start-ups cannot be valued by cash flows → scores from patent indicators.
- IP scoreboard (PoliTo + Leonardo): strategic relevance includes **growth of the field (H)**, **competition (M)**,
  **concentration (L)** → Step 2 outputs feed Step 3.

### Kickoff reference list (to cite where relevant)
- **Utterback & Abernathy (1975)**, dynamic model of process and product innovation → industry life cycle / dominant
  design: consolidation (rising HHI, falling entry) is a sign that a dominant design is emerging. Link Q1/Q2 to it.
- **Teece (1986)** profiting from innovation, complementary assets → why a shipbuilder would partner/acquire (Step 6).
- Concentration measures: **Liston-Heyes & Pilkington (2004)**, *Inventive concentration in the production of green
  technology: fuel cell patents*, Science and Public Policy 31(1) — six measures (CR4, CR8, HHI, 1/HHI, CV, Gini,
  Lotka); replicated in `tutorial_1/11_competitive_landscape.ipynb`.
- Ernst (1998) patent portfolios; Brockhoff (1992) (Steps 3–5).

### Reference documents in `useful_material/`
- `wipo-landscape-patentSDG.pdf` — the landscape template above; top-25 owners per region with CAGR (Table 1, Fig.
  14 style: share vs CAGR bubble chart is a nice format for the top-applicants figure); academia section.
- `clarivate_analytics._global_innovators_report_2017.pdf` — Step 3 (volume ≥100 granted families as stage gate,
  success = grant rate, globalization = quadrilateral families CN/EP/JP/US, influence = citations excl. self).
- `PATSTAT_global_manual_2026.pdf` — data catalog. Facts used:
  - `PSN_SECTOR` keywords: INDIVIDUAL, COMPANY, UNKNOWN, GOV, NON-PROFIT, UNIVERSITY, HOSPITAL (can be several).
    **Filled 3–4 months after each PATSTAT release** → new names are UNKNOWN/empty (justifies our name-based rule).
  - `PERSON_CTRY_CODE`: default value = **spaces** when unknown (justifies the office fallback).
  - `PSN_LEVEL`: 0 none, 1 automated, 2 automated + manual harmonisation.
  - `HAN_ID` / `HAN_NAME`: OECD harmonisation, also with a release lag.
  - `DOCDB_FAMILY_SIZE`, `NB_CITING_DOCDB_FAM`, `NB_APPLICANTS` exist in `TLS201_APPLN`.

---

## 4. What is implemented in `work/11_exercise.ipynb` (state on 2026-11-10, ENV = TEST)

| # | Cells (ids) | What it does | Result on TEST |
|---|---|---|---|
| 1 | `1a351819`, `f59dab12` | imports (incl. `%pip install cleanco`), config: `ENV`, `NAME_METHOD="dictionary"`, sector CPC prefixes `B63B2035/006`, `/007`, `/008`, 13 keywords, `YEAR_MIN/MAX=2000/2025`, `LAST_COMPLETE_YEAR=2022`, `IPR_TYPE="PI"`, `SPLIT_YEAR=2015`, `WINDOW=3`, `TOP_N=15` | — |
| 2 | `1b64a7d3` | families by CPC codes and by keywords (title/abstract, lower-case LIKE) | codes 127, keywords 125, union 199 |
| 3 | `14307a54` | quality check: 10 random titles of codes-only and keywords-only families | codes-only contain noise (wave power, buoys, hydrogen…) |
| 4 | `3d22b254`, `4f13df7b` | **rule: keep a code-only family only if its title/abstract matches `DRONE_WORDS`** (`unmanned|uncrewed|autonom|drone|remote.?control|\busv\b|unattended|robot|payload|glider`) | code-only kept 50 of 74; **final sector = keywords ∪ (codes ∧ drone words) = 175 families** |
| 5 | `bf2d01a1` | `families` subquery (PI, `appln_id < 900000000`, year = min `earliest_filing_year` within 2000–2025); `raw_sector` = applicants (`applt_seq_nr > 0`) with `psn_id, psn_name, han_name, psn_sector, ctry`; `family_cpc` = all CPC codes of the families | **153 families with applicants**, 198 rows |
| 6 | `671e1c63` | raw name counts | psn_name 163, han_name 165, psn_id 167 |
| 7 | `fb66c396` | Method A (dictionary of legal forms) and Method B (`cleanco`) | 163 → 160 names with both |
| 8 | `43a3009a`, `48a2deb2` | **gold standard** (`PATSTAT_500_label_datav4.csv`, 3,192 names in 481 orgs), pairwise precision/recall/F1; Method C = first word | A: P 0.995 R 0.002 F1 0.004 · B: F1 0.005 · **C: P 0.961 R 0.923 F1 0.942** |
| 9 | `7f040447` | Method C checked on our sector | **C wrongly merges 67 names** (all "ZHEJIANG…", "CHANGSHA…", "CHINA…": Chinese names start with a city) → **decision: use Method A** |
| 10 | `002dc12c`, `686946f1` | `NAME_MERGES` (SHUNHAI SHIP MAKING → SHUNHAI SHIPYARDS; CSIC lines still commented); `links` = raw_sector + `applicant` (A + merges) + `type` from `psn_sector` | 159 applicants |
| 11 | `790882bd` | type fallback from name words (`FIRM_WORDS` → firm; UNIVERSITY/COLLEGE → university; INSTITUTE/ACADEMY → gov/non-profit) + `TYPE_FIXES` (Xunord, ETME Peppas → firm) | only **E-4S** still unknown |
| 12 | `04895e18` | `ctry` "" → NaN; count applicants with no country | **96 of 159 have no country** |
| 13 | `435f0576` | `family_offices` = (family, `appln_auth`) | CN 105, US 28, KR 14, WO 12, EP 5… |
| 14 | `f9f776e6` | `country` = most frequent written country, else most frequent national office (EP/WO excluded), else hand fix (`COUNTRY_FIXES`: PEPPAS ANTONIOS → GR); `country_source` ∈ written/office/hand | 63 written, 95 office, 1 hand, 0 missing; **CN 97, US 33, KR 16**, GB 4… |
| 15 | `63eb8b41`, `f3f315c3`, `1f5b9d96` | checks: crosstab country × source; non-CN office cases; keyword search of names | only J3S → US left from office outside CN |
| 16 | `d3717bb7` | **Q1 input**: `links.drop_duplicates(["unit_id","applicant"])`; `complete` = years ≤ 2022; `families_per_applicant` | **156 applicants, 184 applicant-family pairs; size distribution 1:138, 2:11, 3:5, 4:1, 5:1** |
| 17 | `48b8e387` | summary cell (must stay last) | see numbers above |

**Top applicants on TEST (families):** Shanghai Jiao Tong Univ 5, Harbin Engineering Univ 4, Shanghai Ocean Univ 3,
Korea Institute of Ocean Science & Technology 3, Nanjing Univ of Information Science & Technology 3, Shanghai Univ 3,
Zhejiang Ocean Univ 3, Zhejiang Univ 3, then 2-family players incl. Dalian Maritime Univ, Holemans Walter (individual),
Geosystem Research, Liquid Robotics, Solar Sailor, Guangzhou Shunhai Shipyards.

**Applicant types (per applicant):** firm 75, university 42, individual 28, government/non-profit 13, unknown 1.

> ⚠️ All numbers above are on **TEST** (a ~10k-document sample). They only test the code; **slides must use PROD**.

### Decisions taken (and their justification, for the appendix)
1. **Sector = keywords ∪ (CPC B63B2035/006–008 ∧ drone words).** Code-only families without drone words were noise.
2. **Name cleaning = Method A** (+ hand merges). Method C scores F1 0.94 on the gold standard (big Western firms,
   first word = brand) but merges 67 unrelated Chinese organisations in our sector. Lesson for the appendix: a
   benchmark only validates data that looks like the benchmark.
3. **`han_name` not used**: it has more distinct values than `psn_name` here (165 vs 163) and HAN is filled with a
   release lag (manual).
4. **Type**: `psn_sector` first; if empty/UNKNOWN, words in the name; then hand fixes. Justification: PATSTAT manual
   (PSN_SECTOR filled 3–4 months after release).
5. **Country**: written `person_ctry_code` first (most frequent), else most frequent **national** office of the
   applicant's families (EP/WO excluded), else hand fix. Without the fallback, 61% of applicants have no country and
   China is invisible (US would look like the leader). Justification: manual (default = spaces) + STEP2/kickoff
   warning.
6. **Not merged:** PEPPAS ANTONIOS (individual) with ETME PEPPAS KAI SYNERGATES (his firm): different legal owners;
   individuals are analysed separately.

### Update 2026-11-10 (later the same day): switched to PROD
- **Development continues on PROD** (`ENV = "PROD"`): each cell runs in ~2 seconds, and TEST is too small to read
  (3-year windows with 2–3 families). All TEST numbers above are superseded once the notebook is re-run on PROD.
- PROD sector: codes 2,436 · keywords 9,025 · union 10,390 · codes-only 1,365 → kept 860 with the extended drone words ·
  **final sector 9,885 families** · **7,282 families with applicants** (9,012 rows) after the PI / year filters
  (26% attrition — to explain, likely Chinese utility models dropped by `IPR_TYPE = "PI"`).
- `DRONE_WORDS` extended: `unmanned|uncrewed|crewless|pilotless|driver.?less|autonom|drone|remote.?control|radio.?control|\busv\b|unattended|robot|payload|glider`.
- Sector rule **frozen** (markdown cell "Sector definition: frozen" in the notebook): underwater overlap 5.3% kept;
  RC/bait boats out of scope; no flying-drone exclusion.
- The `.in_(list(...))` with ~10k ids works on PROD (no chunking needed).
- Validation: 100 random families (`random_state=42`, cell after the underwater check) → labels in
  `work/validation/sector_validation_sample_labeled.csv` (exception added in `.gitignore`). A first sample drawn
  before the drone-word update was discarded (not reproducible). Labelling rule *proposed* (user has not confirmed yet): a
  generic ship component counts as relevant only if the abstract mentions unmanned / autonomous / remote operation.
- Still to redo on PROD: unknown types, `NAME_MERGES`, `TYPE_FIXES`, `COUNTRY_FIXES`, non-CN office countries,
  Method C check, `MIN_FAMILIES` threshold, and the known-players recall check (search known USV makers — e.g.
  Saildrone, Sea Machines, L3Harris/ASV, Kongsberg, Maritime Robotics, Liquid Robotics, Zhuhai Yunzhou — in
  `links["applicant"]`; for any NOT FOUND, check Google Patents `assignee:(...)` to see whether the query missed them).

---

## 5. Improvements to the existing notebook (do these first, small)

1. **CSIC decision** (pending): uncomment the two CSIC lines in `NAME_MERGES` → group name
   `"CHINA SHIPBUILDING INDUSTRY CORPORATION (CSIC)"`. Write the rule in the markdown above:
   *"Research institutes and subsidiaries are merged into their group (ultimate owner, as WIPO 2024 / Theory 3)."*
   On PROD, search for more subsidiaries/variants of the top 30 (e.g. `str.contains` on "CSSC", "SHIPBUILDING",
   "NAVY", "STATE GRID"…) — note CSIC and CSSC merged in 2019 into China State Shipbuilding Corporation (verify).
2. **One type per applicant.** Different `psn_id`s of one applicant can carry different `psn_sector`s. After the type
   steps, set `type` = most frequent type of the applicant (same `most_frequent` pattern as the country), so tables
   don't depend on `.first()`.
3. **Attrition 175 → 153 families**: report why 22 families disappear (outside 2000–2025, not `PI` — e.g. **Chinese
   utility models**, or no applicant). Count each reason once; it goes in the appendix. Consider a sensitivity check
   including utility models (`ipr_type == "UM"`) because China files many of them.
4. The `appln_id < 900000000` filter is only inside the `families` subquery; the later joins to `TLS201_APPLN` in
   `q_sector`, `q_cpc_fam`, `q_offices` don't repeat it. Add it there too (harmless, more correct).
5. **Gold standard path**: read the local copy `../tutorial_1/PATSTAT_500_label_datav4.csv` (or keep the URL but
   document it) — reproducibility.
6. Tidy markdown titles of cells `a89384dc` ("Get the office of each family") and `9db954ee` ("one country per
   applicant 4b") → `### Office of each family`, `### One country per applicant`. Label the check cells
   (crosstab, non-CN office, keyword search) with a markdown "Checks".
7. Add `OUTPUT_DIR = Path("outputs/step2")` (re-import `Path`) and save every final table (`.csv`) and figure
   (`.png`, dpi 200) there — they go into the deck and the repo.
8. Validation of the sector query (kickoff Step 0): "hand-label about 100 random families". Check whether the team
   did it in Step 0; if not, do it on PROD (precision of the query) and report it in the appendix.

---

## 6. To-do list for Step 2 (in order), with specifications

### 6.1 Q1 · Concentration (next step; partly prepared)
**a) Whole-sector measures** (input: `families_per_applicant` from cell `d3717bb7`):
```python
def concentration_ratio(counts, k):
    largest_first = np.sort(counts)[::-1]
    return largest_first[:k].sum() / largest_first.sum() * 100

def herfindahl(counts):
    shares = np.asarray(counts) / np.sum(counts)
    return np.sum(shares ** 2)
```
- Report **CR4, CR8, HHI, 1/HHI** (and optionally CV, Gini, Lotka from the tutorial notebook — the "six measures" of
  Liston-Heyes & Pilkington 2004; code in `tutorial_1/11_competitive_landscape.ipynb`, cell "six_measures").
- **Expected on TEST: CR4 = (5+4+3+3)/184 ≈ 8.2%** (use as a correctness check). HHI will be very small (~0.008),
  1/HHI ≈ 120+ of 156 real applicants → very dispersed field.
- Interpretation thresholds (competition policy rule of thumb): HHI < 0.15 unconcentrated, 0.15–0.25 moderate,
  > 0.25 highly concentrated. Compare 1/HHI with the real number of applicants.
- Compute **twice**: all applicants, and **without individuals** (firms + universities + gov). Present the version
  without individuals as the main one, or both.

**b) Consolidating? Over time.** HHI, 1/HHI, CR4 on **3-year windows** (`WINDOW`) ending at `LAST_COMPLETE_YEAR`
(e.g. …, 2017–19, 2020–22). Show the number of families and applicants per window (CR4 = 100% mechanically when ≤4
applicants: flag small windows). Trend: Kendall's tau between window index and each measure (`scipy.stats.kendalltau`).
Consolidation = HHI and CR4 rising, 1/HHI falling. Link to **Utterback & Abernathy** (dominant design → shake-out).

**c) Robustness on international families (WIPO / Theory 3).** Define per family
`n_offices = family_offices.groupby("unit_id")["appln_auth"].nunique()`; **international family = filed in ≥ 2
authorities** (state in the appendix how WO/EP are counted; WIPO: "protection sought beyond the home office").
Recompute top applicants + CR4/HHI on international families only. Expect China's weight to drop sharply; this is the
fairer view of competitors relevant to a European client.

**d) Co-assignment (Theory 3 "collaborations").** Share of families with ≥ 2 distinct applicants; most frequent
type pairs (university–firm, firm–firm…). Cheap: from `links`.

**Deck output for Q1:** one figure "concentration and entry over time" (can be combined with Q2 entry, as the kickoff
suggests) + one sentence: concentrated or not, consolidating or not.

### 6.2 Q2 · Incumbents, entrants, start-ups
**a) Extra query: first patent ever + total portfolio of each applicant** (any field, not only the sector), by
`psn_id` in chunks of 5,000:
```python
psn_ids = [int(i) for i in raw_sector["psn_id"].unique()]
parts = []
for start in range(0, len(psn_ids), 5000):
    q = (db.query(TLS206_PERSON.psn_id,
                  func.min(TLS201_APPLN.earliest_filing_year).label("first_patent_year"),
                  func.count(func.distinct(TLS201_APPLN.docdb_family_id)).label("families_all_fields"))
         .join(TLS207_PERS_APPLN, TLS207_PERS_APPLN.person_id == TLS206_PERSON.person_id)
         .join(TLS201_APPLN, TLS201_APPLN.appln_id == TLS207_PERS_APPLN.appln_id)
         .filter(TLS206_PERSON.psn_id.in_(psn_ids[start:start + 5000]),
                 TLS207_PERS_APPLN.applt_seq_nr > 0,
                 TLS201_APPLN.earliest_filing_year.between(1900, YEAR_MAX))   # drops 9999 placeholders
         .group_by(TLS206_PERSON.psn_id))
    parts.append(patstat.df(q))
first_patents = pd.concat(parts)
```
Then map `psn_id → applicant` (via `links`/`raw_sector` + the same cleaning and merges) and aggregate per applicant:
`first_ever = min(first_patent_year)`, `portfolio = sum(families_all_fields)` (approximate; note double counting if
two psn_ids share families).

**b) Start-up definition** (the deck asks for type firm / start-up / university; PATSTAT has no start-up label). Proposal
to discuss with the user: **start-up = firm whose first patent ever is recent (e.g. ≥ 2012, i.e. ≤ ~10 years before
LAST_COMPLETE_YEAR) AND small total portfolio (e.g. < 50 families in all fields)**. Document the thresholds and test
their sensitivity. Optionally confirm top ones by hand (founding year from the web).

**c) Practicing vs non-practicing (Theory 2):** firms (incl. start-ups) = practicing; universities, gov/research,
individuals = NPE. Add as a column.

**d) Top applicants table** (`TOP_N = 15`), main deck table: applicant, type (firm / start-up / university /
gov-research / individual), PE/NPE, country, families in sector, families since `SPLIT_YEAR`, first year in sector,
last year in sector, first patent ever, **status: incumbent (first sector family < 2015) / entrant (≥ 2015)**.
Possibly a second version on international families (6.1c). Possibly also "top firms only" since STX France can only
acquire firms.

**e) Entry/exit per year** (as in `tutorial_1/11_competitive_landscape.ipynb`, section 5.2):
- active applicants; **new to the sector** (first sector family in year t); **new to patenting** (first patent ever in
  year t — this is the kickoff's "never patented before");
- **entrants' share of families** = share of year-t families with ≥ 1 applicant new to the sector;
- **rate of disappearance** = share of applicants active in t that never file again in the sector; set to NaN for
  t > LAST_COMPLETE_YEAR − 3 (unpublished recent filings);
- caveat: first years after `YEAR_MIN` look "all new" (left censoring) — read entry from a few years later;
- shade the incomplete years (> LAST_COMPLETE_YEAR) in every time figure.

**f) Benchmark (Theory 1):** share of sector families by applicant type vs EPO 72% large firms / 18% SMEs+individuals /
10% universities. One sentence for the slide.

### 6.3 Q3 · Subfields (choose with the user)
The sector is defined by only 3 small CPC subgroups (B63B2035/006–008), so "growth of CPC groups" must use the
**other CPC codes of the sector families** (`family_cpc`), or text topics.

- **Option A · CPC groups:** take main groups (e.g. `B63B35`, `B63H…`, `G05D1`, `B63G`, `G01S`, `G01C21`, `H02J`,
  `H02S`, `B63B79`, `E02B15`, `G01N33/18`, `G08G3`, `H04B7/185`…) of the sector families; keep groups with enough
  families; count families in **two 5-year periods: 2013–2017 vs 2018–2022** (`RECENT = LAST_COMPLETE_YEAR−4..
  LAST_COMPLETE_YEAR`, `PAST` = the 5 years before); growth % = recent/past − 1; scatter **size today vs growth**
  (top right big & growing, top left small & fast, bottom declining). **Always translate CPC codes into words using
  the official CPC scheme** (https://www.cooperativepatentclassification.org) — the codes listed here are candidates
  to verify, not verified definitions.
- **Option B · Topics from abstracts** (explicitly allowed by the kickoff; tutorial 2 covers patent text): embed
  title+abstract (e.g. `sentence-transformers`), cluster (KMeans/HDBSCAN) or BERTopic; name clusters from top words;
  same two-period growth. Visible themes in the titles already: solar/wind/wave-powered long-endurance USVs, water
  cleaning/garbage collection, path tracking/collision avoidance/control, military/inspection/combat, hydrographic
  survey/ocean monitoring, docking/launch-recovery, swarms/cooperation with UAVs/UUVs.
- **Option C · Innovation Maturity Matrix** (Theory 3 / WIPO A.4) on the subfields of A or B: x = relative recency
  `R_sub / R_sector`, y = number of families (log) → hot / emerging / mature / modest. Strong theory link; can replace
  the growth scatter or complement it.

**Deck output:** one "subfield growth map" figure + the hot subfields named in words.
Feeds Step 4 ("early filing in hot subfields").

### 6.4 Q4 · PEST (mandatory table, desk research, with sources)
Patent data say who/what/where, not why. Build one table, four rows, each factor with a **source** and its
**implication for STX France** (opportunity/threat). Stages (lecture): identify factors → effects → opportunities vs
threats → prioritise → action. Starting points to research and **verify with sources** (do not cite without checking):
- **Political:** naval/defence procurement of USVs (US Navy unmanned surface vessel programmes; DARPA ACTUV / Sea
  Hunter); use of naval drones in the Black Sea war (Ukraine, since 2022); European defence funding (EDF); China's
  maritime/marine-equipment industrial policy and state-funded university research (explains the CN university
  dominance); **IMO MASS Code** (Maritime Autonomous Surface Ships: regulatory framework under development; check
  current adoption timeline); export controls on dual-use autonomy. Theory link: public procurement & public R&D
  (Theory 0).
- **Economic:** rising defence budgets; offshore wind, oil & gas and hydrographic survey markets (cheaper than crewed
  vessels); venture capital in USV start-ups (e.g. Saildrone); acquisitions of start-ups by incumbents (e.g. **Liquid
  Robotics — in our data — acquired by Boeing in 2016**: a precedent for STX's acquire-or-partner question; verify).
- **Social:** seafarer shortage and crew safety; environmental monitoring and water-surface cleaning demand (many
  Chinese patents on garbage-collecting USVs); public acceptance of autonomous (armed) systems.
- **Technological:** autonomy/AI and COLREGs-compliant collision avoidance; long-endurance renewable propulsion
  (solar/wind/wave); satellite communications; sensors (sonar, radar, LiDAR); swarming and multi-domain cooperation.

### 6.5 Switch to PROD and final numbers
- Finish the whole chain on TEST first. Then set `ENV = "PROD"`, **Restart → Run All** of notebook 11 only (it rebuilds
  the sector itself; no need to rerun Step 1 notebooks for Step 2).
- Repeat the **human checks** on PROD: sector title samples and dropped titles; Method C check; unknown types;
  `TYPE_FIXES`, `NAME_MERGES`, `COUNTRY_FIXES` for the new top players; non-CN "office" countries.
- Keep the sector definition **identical to Step 1** (same codes, keywords and drone-word rule) or update Step 1 too.
- Large data: use `.head()`, avoid printing whole tables; query in chunks.

### 6.6 Code for the repository
Once Step 2 works in the notebook, move it to `src/03_landscape.py` (+ queries in `src/01_extract.py`, cleaning in
`src/02_clean.py`), parameters in `config/sector.yaml` (sector codes, keywords, drone words, years, split year, window,
top N, hand-fix dictionaries), outputs to `outputs/tables` and `outputs/figures`. Add small unit tests for the
indicator functions (e.g. `herfindahl([5]*10) == 0.1`, `concentration_ratio([91]+[1]*9, 4) == 94`). Pin versions in
`requirements.txt`. Notebooks stay for exploration.

---

## 7. What goes into the deck from Step 2 (budget: ~3–4 of the 10 figures/tables)

| Slide | Content |
|---|---|
| Concentration & entry | Figure: HHI / CR4 (and 1/HHI) over 3-year windows + new entrants per year / entrants' share; one sentence: concentrated? consolidating? (+ international-families robustness in one line) |
| Players | Table: top-15 applicants with type (firm / start-up / university), PE/NPE, country, families, first year, incumbent/entrant; one sentence on the type mix vs EPO 72/18/10 |
| Subfields | Figure: subfield growth map or Innovation Maturity Matrix; hot subfields in words |
| PEST | Table (mandatory) with sources and implications for STX France |
| Appendix | Sector rule; name cleaning (A vs B vs C, gold-standard F1, why A); type and country rules (with PATSTAT manual justifications); hand-fix dictionaries; filters (PI, appln_id < 9e8, 2000–2025, last complete year 2022); TEST vs PROD; start-up definition and thresholds; international-family definition; formulas (CR_k, HHI, 1/HHI, recency R) with references |

---

## 8. Pitfalls checklist
- [ ] Count **families**, not applications; co-owned families count once per owner.
- [ ] Count on **cleaned names**, never `person_name`.
- [ ] Stop time series at **LAST_COMPLETE_YEAR (2022)**; shade 2023–2025.
- [ ] Separate **individuals** from organisations in concentration and in the top table.
- [ ] Missing countries filled (China!) before any country statement; report `country_source` shares.
- [ ] China domestic-filing bias → robustness on **international families**.
- [ ] Small windows → CR4 mechanically high; show applicants per window.
- [ ] TEST numbers are never reported; PROD only.
- [ ] Every hand correction is in a dictionary, commented, and listed in the appendix.
- [ ] Every CPC code shown on a slide is translated into words from the official CPC scheme.
- [ ] Every PEST claim has a source.
