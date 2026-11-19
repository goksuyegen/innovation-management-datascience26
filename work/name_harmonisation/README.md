# Applicant-name harmonisation: method comparison (Step 2)

Which method should turn PATSTAT names (`psn_name`) into applicants? We compare five methods on the course gold
standard, then on our own sector's names.

| File | What it is |
|---|---|
| `name_methods.py` | the methods: A, A+, B, first word, **Terrorizer** (re-implementation, see below) |
| `compare_gold_standard.py` | scores every method on the gold standard; grid search of Terrorizer's parameters |
| `results_gold_standard.csv` | **results** on the gold standard |
| `results_terrorizer_grid.csv` | the 288 Terrorizer settings tried, scored on the tune half |
| `check_sector_names.py` | check on our sector's names (needs `sector_psn_names.csv` from TIP) |
| `results_sector_check.csv`, `sector_groups_*.csv` | ⏳ results of the sector check (after the export from TIP) |

Run outside TIP (no PATSTAT needed): `python compare_gold_standard.py`. Needs `sentence-transformers`,
`networkx`, `cleanco`, `pandas`. The Terrorizer embedding model is downloaded from Hugging Face on the first run.

## Methods

| Method | How it works |
|---|---|
| A · dictionary | upper-case, letters/digits only, remove legal forms (LTD, INC…) at the start and end; used in `11_exercise.ipynb` so far |
| A+ · dictionary + abbreviations | A + Unicode normalisation (full-width letters), abbreviations (UNIV → UNIVERSITY…), filler words (OF, AND, THE), non-Latin names kept as they are |
| B · cleanco | `cleanco` legal forms, then A |
| first word | first word of the A-cleaned name; called "method C" in `11_exercise.ipynb`, but it is **not** the tutorial's method C |
| **Terrorizer** | the tutorial's method C (Prof. Ascione, https://github.com/graziasveva/Terrorizer): name embeddings + token rules → network of similar names → communities = applicants |

**Terrorizer re-implementation.** The package is not on PyPI, and the repository code does not run as it is: the
`terrorizer_disambiguator` function from the README is missing, `get_vector` returns only the last vector, and the
branch for more than 1,000 names uses an undefined variable. `name_methods.py` keeps its four stages and its scoring
rule:

1. **Preprocessing.**
2. **Knowledge augmentation.** Not used: it needs a separate knowledge-base download, and it adds domain features
   that our names don't have.
3. **Matching.** Two names are linked when their score reaches `match_threshold`:
   `score = cosine(name embeddings) + w_shared_token·[share a word] + w_first_token·[same first word]`.
   The embedding model is `Vsevolod/company-names-similarity-sentence-transformer`, with an IDF-weighted average of
   word vectors.
4. **Network.** Edges of high-bridgeness nodes are removed (optional), then Louvain communities are found.

## Results on the gold standard (3,192 names, 481 organisations)

Terrorizer has parameters, so the gold standard was split **by organisation**:
- the **tune half** (1,456 names, 240 organisations) was used for the grid search;
- every method is then scored on the **test half** (1,736 names, 241 organisations), which Terrorizer never saw.

| Method | Groups found (true: 241) | Precision | Recall | **F1** |
|---|---|---|---|---|
| no cleaning | 1,736 | 1.000 | 0.000 | 0.000 |
| A · dictionary | 1,623 | 1.000 | 0.002 | 0.004 |
| A+ · dictionary + abbreviations | 1,621 | 1.000 | 0.002 | 0.004 |
| B · cleanco | 1,612 | 1.000 | 0.002 | 0.005 |
| first word | 283 | 0.988 | 0.934 | **0.960** |
| **Terrorizer** | 252 | 0.968 | 0.955 | **0.961** |

Best Terrorizer setting on the tune half: `w_shared_token = 0.1`, `w_first_token = 0.6`, `match_threshold = 0.9`,
no bridgeness pruning. The resolution (0.5 or 1.0) makes no difference.

### Reading the results
- **Terrorizer and first word are tied** (F1 0.961 vs 0.960). Terrorizer finds the number of organisations best
  (252 groups vs the true 241). It merges a bit more, so recall is higher and precision lower.
- **The tuned Terrorizer leans heavily on the first word.** With `w_first_token = 0.6` and a threshold of 0.9, two
  names that share their first word need only a cosine similarity ≥ 0.3 to be linked, which is a low bar. Without
  the same first word they need ≥ 0.8–0.9. So on this gold standard, Terrorizer ends up close to "first word +
  similarity check". That is because in this gold standard (large Western and Japanese firms such as Nokia, Toyota,
  BASF, Pfizer…) **the first word is the brand**.
- **Bridgeness pruning never helped.** Every setting with it scored lower, because it cuts the edges of the central
  names that hold a large group together.
- **A, A+ and B have perfect precision but almost no recall here**, because the gold groups are *ultimate owners*
  (subsidiaries such as "SONY INTERACTIVE ENTERTAINMENT AMERICA" belong to Sony). Removing legal forms can never
  merge those. The A+ changes (abbreviations, non-Latin names) don't show up here, because these names have few
  abbreviations.
- **Caveat for our sector.** In our data most names are Chinese and start with a city or province ("ZHEJIANG…",
  "CHINA…"). On these names first word wrongly merged unrelated organisations, and a first-word-heavy Terrorizer may
  do the same. The gold-standard score alone cannot choose the method. → `check_sector_names.py` (⏳ needs the
  export of our names from TIP).

### Sentence for the appendix (draft)
> "We compared five name-harmonisation methods on the course gold standard (3,192 names, 481 organisations),
> tuning Terrorizer's parameters on half of the organisations and scoring all methods on the other half.
> Terrorizer (F1 = 0.96) and a first-word rule (F1 = 0.96) clearly beat dictionary cleaning (F1 < 0.01), which
> cannot merge subsidiaries. [Result of the sector check and final choice.]"
