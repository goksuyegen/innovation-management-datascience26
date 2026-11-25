# Report notes · Step 2 (Surface drones, client STX France)

Material to copy into the deck and the technical appendix. Each entry gives the **numbers** (PROD only), a
**ready-to-use sentence**, and the **theory or source** to cite.



---

## A. Technical appendix

### A1. Data ✅
- Source: PATSTAT Global, queried through EPO TIP (`epo.tipdata.patstat`, PROD database). *(Add the PATSTAT edition,
  e.g. "2026 Spring", before submitting.)*
- Unit of analysis: the **DOCDB family** (one invention, filed in one or more countries).
- Time: the **earliest priority year** of the family; window 2000–2025.
- **Truncation:** applications are published about 18 months after filing, so the years after **2022** are
  incomplete. They are shaded in figures and left out of trend measures.
- Filters: patents only (`ipr_type = 'PI'`); `appln_id < 900000000` (drops artificial records); applicants only
  (`applt_seq_nr > 0`, not inventors).

### A2. Sector perimeter ✅
- **Rule:** a family is in the sector if its title or abstract contains a sector keyword, **or** if it has one of
  the CPC codes B63B2035/006–008 **and** its title or abstract contains a drone word (unmanned, uncrewed, crewless,
  pilotless, driverless, autonom*, drone, remote/radio control, USV, unattended, robot, payload, glider).
- **Why the extra condition on CPC codes:** families matched only by the CPC codes (no keyword) were often unrelated
  (wave power, buoys, hydrogen). Only 860 of these 1,365 families mention unmanned operation, and only those are kept.

| Step | Families |
|---|---|
| Matched by CPC codes | 2,436 |
| Matched by keywords | 9,025 |
| Union | 10,390 |
| CPC-only families | 1,365, of which 860 kept (they mention unmanned operation) |
| **Final sector** | **9,885** |

- Scope decisions (frozen): underwater vehicles that overlap with the sector (5.3% of families) are **kept**; toy
  radio-controlled and bait boats are **out of scope**; flying drones are **not** excluded by a rule (they are rare
  errors, see A3).

> *Sentence:* "The sector is defined by keywords in titles and abstracts, plus CPC codes B63B2035/006–008 when the
> text also refers to unmanned operation. This gives 9,885 DOCDB families."

Theory: Theory 3, where the search strategy is a classification problem (the perimeter) and every indicator is a
modelling choice.

### A3. Validation of the perimeter (precision) ✅
- Method: random sample of **100 families** (`random_state = 42`), labelled from title and abstract. File:
  `work/validation/sector_validation_sample_labeled.csv`.
- Labelling rule: a generic ship component counts as relevant only if the abstract mentions unmanned, autonomous or
  remote operation.
- **Result: precision = 90/100 (95% Wilson CI 82.6–94.5%).**

| Error type | Count |
|---|---|
| Flying drones (UAVs) | 3 |
| Generic ship devices with no unmanned operation | 3 |
| Underwater vehicles (seismic node; ballast "multi-role" vehicle) | 2 |
| Moored floating platform | 1 |
| Coastal HF radar | 1 |

- No single error type dominates, so the rule was not changed.
- ⏳ **Recall check:** known USV makers (Saildrone, Sea Machines, L3Harris/ASV, Kongsberg, Maritime Robotics, Liquid
  Robotics, Zhuhai Yunzhou) are searched for among the applicants.

> *Sentence:* "On a random sample of 100 families, 90 are surface drones or their systems (precision 90%, 95% CI
> 83–95%). The errors are spread across flying drones, underwater vehicles and generic ship equipment."

### A4. From sector families to analysed families (attrition) ✅

| Reason | Families | Share |
|---|---|---|
| Only utility models or designs, no patent (UM 2,286 applications, designs 5) | 2,288 | 23% |
| Priority year outside 2000–2025 | 308 | 3% |
| No applicant recorded | 7 | 0.1% |
| **Kept for the analysis** | **7,282** | **74%** |
| Total | 9,885 | 100% |

> *Sentence:* "Of 9,885 sector families, 2,288 (23%) contain only utility models and are excluded by the
> patents-only filter, 308 have a priority year outside 2000–2025, and 7 have no applicant. 7,282 families remain."

- **Methodological choice: patents only.** Patents are examined, while utility models are mostly not. Patents also
  compare countries more fairly, because many countries, including the US, have no utility models. Utility models are
  filed mostly in China, so excluding them under-counts small Chinese players.
- ⏳ **Robustness check:** rerun the top applicants, CR4/HHI and China's share with utility models included, and state
  whether the conclusions change.

Theory: Theory 0 (types of IPR; utility models as a weaker form of protection).

### A5. Applicant name harmonisation ✅ (method) · ⏳ (sector check on PROD)
- Five methods compared on the course **gold standard** (3,192 names, 481 organisations; pairwise precision, recall,
  F1). The data was split by organisation: Terrorizer's parameters were tuned on one half, and every method was scored
  on the other half (1,736 names, 241 organisations). Details, code and CSV files: `work/name_harmonisation/`. ✅

| Method | Groups (true 241) | Precision | Recall | F1 |
|---|---|---|---|---|
| A · dictionary of legal forms | 1,623 | 1.000 | 0.002 | 0.004 |
| A+ · A + abbreviations, Unicode, non-Latin fallback | 1,621 | 1.000 | 0.002 | 0.004 |
| B · `cleanco` | 1,612 | 1.000 | 0.002 | 0.005 |
| first word (called "method C" in the notebook) | 283 | 0.988 | 0.934 | 0.960 |
| **Terrorizer** (Ascione; tutorial's method C, re-implemented) | 252 | 0.968 | 0.955 | **0.961** |

- Terrorizer ties with first word. Its tuned setting (first-word weight 0.6, threshold 0.9, no bridgeness pruning)
  leans heavily on the first word, because in the gold standard (large Western and Japanese firms) the first word is
  the brand. Dictionary methods cannot merge subsidiaries, which is why their recall is near zero.
- Terrorizer had to be re-implemented: the package is not on PyPI and the repository code does not run as it is (see
  `work/name_harmonisation/README.md`). Its knowledge-base stage was not used.
- ⏳ **Sector check** (`check_sector_names.py`): how many unrelated Chinese organisations each method merges in our
  names. First word did this on TEST (67 names), because Chinese names start with a city or province ("ZHEJIANG…",
  "CHINA…").
- ⏳ **Choice** after the sector check. Current method: A, plus hand merges.
- Lesson for the appendix: *a benchmark only validates data that looks like the benchmark.*
- `han_name` (OECD HAN) is not used: it is filled with a release lag and gives no fewer distinct names here.
- **Ultimate owner:** research institutes and subsidiaries are merged into their group (for example, CSIC institutes
  into "China Shipbuilding Industry Corporation (CSIC)"), following WIPO's consolidation to the ultimate owner
  (Theory 3, the "name game"). Groups use **today's owner** (Step 3 scores who STX could partner with or buy now).
  Rules in `src/owners.py`; full list with reasons in A7.

### A6. Applicant type and country ✅ (rules) · ⏳ (numbers on PROD)
- **Type:** PATSTAT `psn_sector` first. If that is empty or UNKNOWN, words in the name (firm legal forms →
  firm; UNIVERSITY/COLLEGE → university; INSTITUTE/ACADEMY/LABORATORY → government or research). Then hand fixes.
  LABORATORY added on 24 Nov: two public labs (Southern Marine Science and Engineering Guangdong Laboratory, Peng
  Cheng Laboratory) had no type; firm words are checked first, so "X LABORATORY CO LTD" stays a firm.
  Justification: the PATSTAT manual says PSN_SECTOR is filled 3–4 months after each release, so new names are unknown.
- **Country:** the most frequent country written on the applicant's records. Failing that, the most frequent
  **national** office of the applicant's families (EP and WO excluded). Failing that, a hand fix. Justification: the
  manual gives spaces as the default when the country is unknown. Without the fallback most applicants have no country,
  China becomes invisible and the US looks like the leader.
- Report the share of countries by source (written, office, hand). ⏳ PROD numbers.
- Individuals are kept separate from their own firms (they are different legal owners).

### A7. Hand corrections and ultimate owners (PROD, 25 Nov)

**Ultimate-owner groups** (`src/owners.py`, a regular expression on the cleaned name; the names absorbed are written
to `outputs/tables/ultimate_owner_merges_PROD.csv`):

| Group | Members | Reason |
|---|---|---|
| CSSC | CSSC, former CSIC and their numbered research institutes | CSIC and CSSC merged in 2019 |
| CETC, CCCC | institutes and subsidiaries, incl. China E-Tech (Ningbo) Maritime Electronics Research Institute (= CETC Ningbo, 中电科) | state groups |
| PLA | military units, Naval University of Engineering | one owner |
| HD Hyundai | Hyundai Heavy, Samho, Mipo, Avikus… | group subsidiaries |
| Hanwha | Hanwha units, former DSME | Hanwha bought DSME in 2023 (Hanwha Ocean) |
| Boeing | Boeing, Liquid Robotics (Wave Glider) | acquired 2016 |
| Kongsberg Gruppen | Kongsberg Maritime, Seatex, Discovery… (not Kongsberg Automotive) | one group |
| thyssenkrupp | TKMS, Atlas Elektronik | Atlas belongs to TKMS |
| SLB | Schlumberger, WesternGeco | seismic unit of SLB |
| **Zhuhai Yunzhou (OceanAlpha)** | Zhuhai Yunzhou Intelligence / Intelligent Technology / Intelligent S T; **Pearl Hai Yunberg Intelligent Science Technology; Shenzhen Yunzhou Innovation Technology; Shenzhen Yunzhou Technology; Jiangsu Yunzhou Intelligent Technology; Yunzhou Yancheng Innovation Technology** (+ "Shenhzne" typo) | see below |
| Sifang | Beijing Sifang Automation; Sifang Jibao Wuhan Software; Sifang Zhifang / Sifang Intelligent Wuhan Control Technology | Wuhan subsidiaries; they co-file the same families (4 names: 71 family counts → 39 families). All sampled titles are unmanned ships. Not CRRC Qingdao Sifang (railways) |
| Exail | iXblue, ECA Group / ECA Robotics | combined as Exail in 2022 (Groupe Gorgé, now Exail Technologies) |
| Navigation Brilliance (Qingdao) | "Brillance" and "Brilliance" spellings | same company, typo in PATSTAT |

**Assumption to state (Zhuhai Yunzhou).** The extra "Yunzhou" applicants are merged into OceanAlpha because
(1) they carry the same brand name, "Pearl Hai" being a word-by-word translation of Zhuhai (珠海); (2) a sample
of their family titles on TIP shows only USVs of OceanAlpha's product line (formation control, launch and recovery,
masts, sampling boats); (3) OceanAlpha is the only large USV maker with that name. Their ownership was **not**
verified in a company registry (Qichacha / Tianyancha). Effect: Zhuhai Yunzhou goes from 87 to **115 families in 2012–2022**
(136 over all years); in the Step 3 firms ranking it moves from #12 to #7. Sentence for the appendix:

> "Applicants named 'Yunzhou' in Shenzhen, Jiangsu and Yancheng, and 'Pearl Hai Yunberg' (a literal translation of
> Zhuhai Yunzhou), are counted as part of Zhuhai Yunzhou Intelligence Technology (OceanAlpha): they share its name
> and all their patent families describe OceanAlpha-type unmanned surface vessels. We did not verify their
> ownership in a company registry; without this merge OceanAlpha would have 87 instead of 115 families in 2012–2022."

**Name merges** (`hand_fixes.name_merges` in `config/sector.yaml`): Guangzhou Shunhai Ship Making → Guangzhou Shunhai
Shipyards (same yard); CSIC No 707 and 715th institutes → CSIC (then CSSC); "SHENHZNE YUNZHOU INNOVATION TECHNOLOGY"
→ Shenzhen Yunzhou Innovation Technology (typo).

**Type fixes:** Xunord S R L → firm, ETME Peppas kai Synergates → firm (legal form not recognised).
**Country fixes:** Peppas Antonios → GR.

**Not changed, but to mention:** Dongguan Lianzhou Intellectual (8 families, none granted) and Zhongying Fund
Management (21 families) look like patent intermediaries, not USV makers; they stay in the data, flagged as
possible non-practicing entities. SLB's country shows as CA (from its records); the group is headquartered in the US.

---

## B. Main deck (Step 2 slides)

### B1. Q1 · Concentration and consolidation ⏳
- Measures: CR4, CR8, HHI, 1/HHI (Liston-Heyes & Pilkington 2004), for all applicants and without individuals.
- Over time: 3-year windows ending in 2022. Windows with fewer than `MIN_FAMILIES` families are flagged.
- Thresholds: HHI < 0.15 unconcentrated, 0.15–0.25 moderate, > 0.25 high.
- Robustness: international families only (filed in ≥ 2 authorities; WIPO 2024, Theory 3).
- Theory: Utterback & Abernathy (1975). Rising HHI and falling entry would mean a dominant design is emerging.
- *Note from the TEST run (not for the slides):* the field was de-concentrating through entry, not through big
  players shrinking. Check that this holds on PROD.

### B2. Q2 · Incumbents, entrants, start-ups ⏳
- To do: top-15 table (type, practicing/non-practicing, country, incumbent/entrant), entry and exit per year, the
  start-up definition, and the EPO benchmark of who files (72% large firms / 18% SMEs and individuals / 10%
  universities, Theory 1).
- Theory 2: universities and individuals are non-practicing entities, so they are partners or licensors for STX.
  Firms and start-ups are possible acquisition targets.

### B3. Q3 · Subfields ⏳
- To decide: CPC groups, topics from abstracts, or the Innovation Maturity Matrix (WIPO 2024 A.4).

### B4. Q4 · PEST (mandatory) ⏳
- Every claim needs a source and its implication for STX France. Starting points are in `STEP2_HANDOFF.md` §6.4.

---

## C. References used so far
- WIPO (2024), patent landscape report (SDGs): ultimate owner, international families, Innovation Maturity Matrix.
- European Patent Office, PATSTAT Global data catalog / manual (2026): PSN_SECTOR lag, country default value.
- Liston-Heyes, C. & Pilkington, A. (2004), *Inventive concentration in the production of green technology: fuel
  cell patents*, Science and Public Policy 31(1).
- Utterback, J. M. & Abernathy, W. J. (1975), *A dynamic model of process and product innovation*, Omega 3(6).
- Wilson, E. B. (1927), *Probable inference, the law of succession, and statistical inference*, JASA 22 (confidence
  interval for the precision).
- Course lectures: IM Theory 0 (types of IPR), 1 (patent filing, EPO benchmark), 2 (practicing vs non-practicing
  entities), 3 (patent intelligence and landscapes).
