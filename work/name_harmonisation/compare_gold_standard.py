"""Compare the name-harmonisation methods on the gold standard (PATSTAT_500_label_datav4.csv).

Terrorizer has parameters, so tuning and scoring on the same names would flatter it. We split the gold standard
by organisation (random half / half): the grid search uses the TUNE half only, and every method is scored on the
TEST half (plus the whole file for the methods without parameters).

Run (outside TIP, no PATSTAT needed):  python compare_gold_standard.py
Outputs (same folder): results_gold_standard.csv, results_terrorizer_grid.csv
"""

import itertools
import time
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

from name_methods import Terrorizer, clean_a, clean_a_plus, clean_b, first_word

HERE = Path(__file__).resolve().parent
GOLD_FILE = HERE.parent.parent / "tutorial_1" / "PATSTAT_500_label_datav4.csv"
SEED = 0

GRID = {                                   # w_similarity is fixed at 1: the other weights are relative to it
    "w_shared_token": [0.0, 0.1],
    "w_first_token": [0.0, 0.2, 0.4, 0.6],
    "match_threshold": [0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
    "resolution": [0.5, 1.0],
    "bridgeness_threshold": [None, 1e-5, 1e-4],      # normalised bridgeness values are tiny: 1e-3 cut everything
}


def pairs_inside(group_sizes):
    return sum(comb(int(n), 2) for n in group_sizes)


def precision_recall_f1(gold_groups, predicted_groups):
    "Pairwise precision, recall and F1 (same definition as in 11_exercise.ipynb)."
    df = pd.DataFrame({"gold": list(gold_groups), "pred": list(predicted_groups)})
    tp = pairs_inside(df.groupby(["gold", "pred"]).size())
    tp_fp = pairs_inside(df.groupby("pred").size())
    tp_fn = pairs_inside(df.groupby("gold").size())
    precision = tp / tp_fp if tp_fp else 1.0
    recall = tp / tp_fn
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"groups found": df["pred"].nunique(), "true groups": df["gold"].nunique(),
            "precision": precision, "recall": recall, "F1": f1}


def main():
    gold = pd.read_csv(GOLD_FILE).rename(columns={"comp": "name", "Group": "gold_group"})
    gold = gold.drop_duplicates("name").reset_index(drop=True)
    orgs = gold["gold_group"].unique()
    rng = np.random.default_rng(SEED)
    tune_orgs = set(rng.choice(orgs, size=len(orgs) // 2, replace=False))
    samples = {
        "tune half": gold[gold["gold_group"].isin(tune_orgs)].reset_index(drop=True),
        "test half": gold[~gold["gold_group"].isin(tune_orgs)].reset_index(drop=True),
        "whole file": gold,
    }
    for label, s in samples.items():
        print(f"{label}: {len(s)} names, {s['gold_group'].nunique()} organisations")

    # ---------------------------------------------------------------- Terrorizer: grid search on the tune half
    terrorizer = Terrorizer()
    features = {label: terrorizer.prepare(s["name"].tolist()) for label, s in samples.items()}

    grid_rows = []
    keys = list(GRID)
    start = time.time()
    for values in itertools.product(*GRID.values()):
        params = dict(zip(keys, values))
        labels = Terrorizer.cluster(features["tune half"], **params)
        grid_rows.append({**params, **precision_recall_f1(samples["tune half"]["gold_group"], labels)})
    grid = pd.DataFrame(grid_rows).sort_values("F1", ascending=False)
    grid.to_csv(HERE / "results_terrorizer_grid.csv", index=False)
    print(f"grid search: {len(grid)} settings in {time.time() - start:.0f} s")
    best = grid.iloc[0][keys].to_dict()
    best["bridgeness_threshold"] = None if pd.isna(best["bridgeness_threshold"]) else best["bridgeness_threshold"]
    print("best Terrorizer setting on the tune half:", best)

    # ---------------------------------------------------------------- score every method
    rule_methods = {"A dictionary": clean_a, "A+ dictionary + abbreviations": clean_a_plus,
                    "B cleanco": clean_b, "first word": first_word}
    rows = []
    for label in ["test half", "whole file"]:
        s = samples[label]
        rows.append({"method": "no cleaning", "sample": label, **precision_recall_f1(s["gold_group"], s["name"])})
        for name, f in rule_methods.items():
            rows.append({"method": name, "sample": label,
                         **precision_recall_f1(s["gold_group"], s["name"].map(f))})
        labels = Terrorizer.cluster(features[label], **best)
        note = "tuned on the tune half" + (" (whole file includes it: optimistic)" if label == "whole file" else "")
        rows.append({"method": "Terrorizer", "sample": label, "note": note,
                     **precision_recall_f1(s["gold_group"], labels)})
    results = pd.DataFrame(rows)
    results["Terrorizer setting"] = np.where(results["method"] == "Terrorizer", str(best), "")
    results.round(3).to_csv(HERE / "results_gold_standard.csv", index=False)
    print(results.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
