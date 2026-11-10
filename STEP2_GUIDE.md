# Step 2 · Competitive landscape: what it is and how to do it

A plain guide to Step 2 of the Innovation Management project work, for a data science student who has never used patent data. Our sector is **quantum computing**.

The code lives in [tutorial_1/11_competitive_landscape.ipynb](tutorial_1/11_competitive_landscape.ipynb). Background on the data columns: [tutorial_1/10_patent_attributes.ipynb](tutorial_1/10_patent_attributes.ipynb).

---

## 1. The 2-minute background

**Patents.** A company that invents something files a *patent application* at a patent office (European, US, Chinese…) to get exclusive rights. Each application lists its **applicants** (the owners, usually companies or universities) and its **inventors** (the people who did the work).

**PATSTAT** is the European Patent Office's database of patent data from almost every office in the world: a relational database of ~140 million documents. We query it with SQL or Python.

**TIP** is the European Patent Office's online Jupyter platform where PATSTAT is already connected. The notebooks only run there.

**Words you will meet**

| Term | Meaning | Data science analogy |
|---|---|---|
| Application (`appln_id`) | One filing at one office | One row in the main table |
| Family (`docdb_family_id`) | All the applications that protect the **same invention** in different countries | A group-by key; we count **families = inventions** |
| Applicant | The owner of the patent (company, university, person) | The "player" Step 2 is about |
| CPC code (e.g. `G06N 10/40`) | A hierarchical technology label; each patent has several | A multi-label category |
| Priority year (`earliest_filing_year`) | The year the invention was **first** filed anywhere | The timestamp we use |
| TEST / PROD | A ~10k-document sample of PATSTAT / the full database | Dev set / full data |

**Our sector** is the set of families found by quantum CPC codes (e.g. `G06N10`) **or** keywords ("qubit", "quantum comput"…) in titles and abstracts. This was Step 0. Step 1 described its size, technologies and geography.

---

## 2. What Step 2 asks

Step 1 looked at the **technology**. Step 2 looks at the **players**: *who competes in this field, and how?* The slides must answer four questions:

| # | Question | In simple words | How we measure it |
|---|---|---|---|
| Q1 | How concentrated is the field, and is it consolidating? | Do a few players own most inventions? Is that getting stronger? | Concentration indices (CR4, HHI, Gini…) overall and over time |
| Q2 | Who are the incumbents and who are the new entrants? | Old players vs newcomers | First year each applicant appears in the sector |
| Q3 | Which subfields are growing fastest? | Which parts of quantum are hot | Growth of CPC groups between two periods |
| Q4 | Which forces shape the field? | Politics, money, society, tech | **PEST** analysis from sources outside PATSTAT |

---

## 3. The pipeline

```
Step 0 sector families
   │
   ├─► (a) get the applicants of each family
   ├─► (b) clean the applicant names          ◄── the hardest part
   ├─► (c) give each applicant a type and a country
   │
   ├─► Q1 concentration      (families per applicant)
   ├─► Q2 incumbents/entrants (first year per applicant)
   ├─► Q3 subfields           (families per CPC group, two periods)
   └─► Q4 PEST                (desk research, no data)
```

### (a) Applicants of the sector

Join path: `families (TLS201) → person links (TLS207, keep applt_seq_nr > 0) → persons (TLS206)`.

Always filter:
- `ipr_type = 'PI'`: real patents only. This drops utility models (cheaper "small patents") and designs.
- `appln_id < 900000000`: drops "dummy" rows that PATSTAT uses internally.

### (b) Clean the applicant names ("the name game")

The same company is written in many ways ("IBM", "International Business Machines Corp", "IBM CORP."). If we count spellings as different firms, big players look small and **every concentration number is wrong**.

PATSTAT gives three name columns:

| Column | What it is | Use it? |
|---|---|---|
| `person_name` | As printed on the patent | ❌ never for counting |
| `psn_name` | EPO-standardised name | ✅ |
| `han_name` | OECD-harmonised name, usually merges more | ✅ best starting point |

Then clean further (Section 2 of the notebook):
- **Method A, dictionary:** uppercase, remove punctuation and legal forms (INC, LTD, GMBH, CORP, KK…).
- **Method B, `cleanco`:** a Python package that knows legal forms of many countries.
- **By hand, for the top players:** merge subsidiaries into their group (no PATSTAT name does this).

**How to tell whether the cleaning is good:** the notebook gives a **gold standard**, `PATSTAT_500_label_datav4.csv` (names grouped by hand). We score our method on **pairs of names**:
- **Precision**: of the pairs we merged, the share that really belong together. It's low if we merge too much.
- **Recall**: of the pairs that belong together, the share we merged. It's low if we merge too little.
- **F1**: their harmonic mean.

This is the "Your turn" exercise in Section 2.4.

**What we found in our quantum data (TEST)**

| Problem | Example | Fixed by |
|---|---|---|
| Upper/lower case, legal form | "Strong Force…" vs "STRONG FORCE…"; "SPICEWARE CO." vs "SPICEWARE CO., LTD." | `han_name` ✅ |
| Prefix with city | "HEFEI ORIGIN QUANTUM…" vs "Origin Quantum…" | `han_name` ✅ |
| Different script | "1QB INFORMATION TECHNOLOGIES" vs "１キュービー…" (Japanese) | ❌ by hand |
| Legal form changed | "Quantum Technologies UG" vs "Quantum Technologies GmbH" | ❌ by hand |
| Subsidiaries | "State Grid Central China Branch", "State Grid Xinjiang…" | ❌ group consolidation |

29 raw spellings → 28 (`psn_name`) → 26 (`han_name`).

### (c) Type and country of each applicant

- **Type** comes from `psn_sector`: COMPANY, UNIVERSITY, INDIVIDUAL, GOV NON-PROFIT, UNKNOWN. ⚠️ It can be wrong; in our data, a German company was labelled INDIVIDUAL. Individuals are usually analysed separately from firms.
- **Country** comes from `person_ctry_code`. One firm can have different countries on different patents, so take the **most frequent** one.
- ⚠️ **Missing countries:** for applications filed in China and Japan the country is often empty (two blanks). In our data almost every Chinese applicant had no country, so China is **under-counted** unless we fix it, e.g. by using the office (`appln_auth = 'CN'`) as a fallback.

---

## 4. The four questions in detail

### Q1 · Concentration

Input: the number of families of each applicant. A family co-owned by two firms counts for each of them.

| Measure | Formula / idea | High value means |
|---|---|---|
| **CR4**, **CR8** | Share of all families held by the 4 (8) largest applicants | Concentrated |
| **HHI** (Herfindahl) | Σ (share of each applicant)², from 0 to 1 | Concentrated (1 = monopoly) |
| **1/HHI** | "Number of equal-sized players" the market is equivalent to | **Less** concentrated |
| **CV** | std / mean of families per applicant | Unequal sizes |
| **Gini** | Inequality of the Lorenz curve, 0 to 1 | Unequal sizes |
| **Lotka slope L** | Slope of log(number of applicants with n families) vs log(n) | Closer to 0 = more concentrated |

These six come from Liston-Heyes & Pilkington (2004), a paper on fuel cells that the notebook replicates in Section 4. For our slides, the key numbers are **HHI, 1/HHI and CR4**.

**Consolidating?** Compute HHI and CR4 over **3-year windows** (`WINDOW = 3`). If HHI and CR4 rise and 1/HHI falls over time, fewer players own more of the inventions, so the field is consolidating.

### Q2 · Incumbents and entrants

- **Incumbent:** first family in the sector **before** `SPLIT_YEAR` (default 2015).
- **Entrant:** first family **from** `SPLIT_YEAR` on.

Outputs:
- **Top applicants table** (`TOP_N = 15`): name, type, country, families, first year, incumbent or entrant.
- **Per year**:
  - active applicants;
  - new to the sector;
  - **new to patenting** (their first patent ever, in any field);
  - share of families filed by entrants;
  - **rate of disappearance** (active this year, never again).

Caveats:
- In the first years everyone looks "new", because we don't see before `YEAR_MIN`. Read entry from a few years later.
- Disappearance isn't reliable in the last ~3 years, because recent patents aren't published yet.

### Q3 · Fastest-growing subfields

A subfield is a CPC group inside the sector. For quantum:

| Subfield | CPC |
|---|---|
| Hardware (qubits, physical realisation) | `G06N 10/40` |
| Algorithms | `G06N 10/60` |
| Error correction | `G06N 10/70` |
| Software / programming | `G06N 10/80` |
| Quantum cryptography | `H04L 9/0852` |

Count the families per subfield in two 5-year periods (e.g. 2013–17 vs 2018–22), compute the growth, and plot **size vs growth**:
- top right: big and growing;
- top left: small but fast;
- bottom: declining.

### Q4 · PEST

Patent data say **who, what, where**, but not **why**. PEST is desk research (reports, news, policy documents):

| Force | Quantum examples to research |
|---|---|
| **P**olitical | US National Quantum Initiative, EU Quantum Flagship, export controls on quantum tech |
| **E**conomic | Venture capital in start-ups, big-tech investment, government funding |
| **S**ocial | Shortage of quantum-skilled workers, public and media attention |
| **T**echnological | Qubit quality, error-correction progress, threat to today's encryption |

---

## 5. Pitfalls checklist

- [ ] **Same sector definition as the team** (same codes and keywords as Step 0 and Step 1).
- [ ] **Clean the sector first.** On TEST, `G06N10` also pulled in "quantum-inspired" energy patents, so State Grid and other power companies showed up as "quantum players". Rule to add: keep a code-found family only if its title or abstract mentions "quantum" or "qubit".
- [ ] Count **families**, not applications.
- [ ] Count applicants on **cleaned names** (`han_name` + extra cleaning), never on `person_name`.
- [ ] **Fill in missing countries** (China and Japan especially) before country statements.
- [ ] Separate **individuals** from firms and universities.
- [ ] Stop time series at the **last complete year** (`LAST_COMPLETE_YEAR = YEAR_MAX - 3`).
- [ ] Develop on **TEST**, report **PROD** numbers only. On TEST one German firm held 13 of 40 quantum applications, which is a sample artefact.
- [ ] **Citations and family size are skewed**: report medians, not only means (TEST: median 3 citations vs mean 12.5).

---

## 6. What goes into the slides

| Slide | Content |
|---|---|
| Concentration | HHI, 1/HHI, CR4 (+ the other measures in a table); a chart of HHI / CR4 over 3-year windows; one sentence: concentrated or not, consolidating or not |
| Players | Top-15 applicants table (type, country, families, first year, incumbent/entrant); chart of new entrants per year |
| Subfields | Size vs growth chart of the CPC groups; which subfields are hot |
| PEST | One table with the four forces, with sources |
| Appendix | Name-cleaning method and its F1 on the gold standard; filters used; TEST/PROD; last complete year |

---

## 7. Status

**Done (learning, on TEST)**
- TIP connection from VS Code; notebooks 01 (Step 0), 02 (Step 1) and 10 (attributes) worked through on quantum computing.
- First look at quantum applicants: name problems, wrong types and missing Chinese countries identified (Section 3 above).

**To do**
1. Agree the final sector definition with the team, including the "mentions quantum" rule.
2. Notebook 11, Section 2: name cleaning + gold-standard exercise (precision / recall / F1).
3. Q1–Q3 on our sector, first on TEST, then on PROD.
4. Q4 PEST research.
5. Slides.
