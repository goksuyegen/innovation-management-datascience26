"""Check the name-harmonisation methods on OUR sector's applicant names (no gold standard here).

There are no true labels for our names, so we look for merges that are very likely wrong:
  * two different universities in one group (both names contain UNIVERSITY and neither name's words are contained
    in the other's: "ZHEJIANG UNIVERSITY" + "ZHEJIANG OCEAN UNIVERSITY" is flagged,
    "HARBIN ENGINEERING UNIVERSITY" + "HARBIN ENGINEERING UNIVERSITY QINGDAO ..." is not);
  * two differently numbered institutes in one group ("NO 707 ..." + "NO 708 ...").
The share of families that sit in flagged groups tells how much a method would distort the counts.

Input : sector_psn_names.csv  (columns psn_name, families), saved from 11_exercise.ipynb on TIP
Run   : python check_sector_names.py
Output: results_sector_check.csv (one row per method), sector_groups_<method>.csv (multi-name groups, for review)
"""

import re
from pathlib import Path

import pandas as pd

from name_methods import Terrorizer, clean_a, clean_a_plus, clean_b, first_word

HERE = Path(__file__).resolve().parent


def words(name):
    return set(clean_a_plus(name).split())


def wrong_pair(a, b):
    "True if names a and b are very likely two different organisations."
    wa, wb = words(a), words(b)
    if wa <= wb or wb <= wa:
        return False
    if "UNIVERSITY" in wa and "UNIVERSITY" in wb:
        return True
    numbers_a = {w for w in wa if re.fullmatch(r"\d+(TH)?", w)}
    numbers_b = {w for w in wb if re.fullmatch(r"\d+(TH)?", w)}
    return bool(numbers_a and numbers_b and numbers_a != numbers_b)


def flagged_group(names):
    names = list(names)
    return any(wrong_pair(a, b) for i, a in enumerate(names) for b in names[i + 1:])


def main():
    sector = pd.read_csv(HERE / "sector_psn_names.csv")
    names = sector["psn_name"].astype(str).tolist()

    grid = pd.read_csv(HERE / "results_terrorizer_grid.csv")
    best = grid.iloc[0][["w_shared_token", "w_first_token", "match_threshold", "resolution",
                         "bridgeness_threshold"]].to_dict()
    best["bridgeness_threshold"] = None if pd.isna(best["bridgeness_threshold"]) else best["bridgeness_threshold"]

    terrorizer = Terrorizer()
    groups = {
        "A dictionary": [clean_a(n) for n in names],
        "A+ dictionary + abbreviations": [clean_a_plus(n) for n in names],
        "B cleanco": [clean_b(n) for n in names],
        "first word": [first_word(n) for n in names],
        "Terrorizer": Terrorizer.cluster(terrorizer.prepare(names), **best),
    }

    rows = []
    for method, labels in groups.items():
        df = sector.assign(group=labels)
        multi = df.groupby("group").filter(lambda g: len(g) > 1)
        flags = multi.groupby("group")["psn_name"].apply(flagged_group)
        multi = multi.assign(likely_wrong=multi["group"].map(flags))
        slug = re.sub(r"[^a-z0-9]+", "_", method.lower()).strip("_")
        (multi.sort_values(["likely_wrong", "group"], ascending=[False, True])
              .to_csv(HERE / f"sector_groups_{slug}.csv", index=False))
        rows.append({
            "method": method,
            "names": len(df),
            "groups (applicants)": df["group"].nunique(),
            "groups with >1 name": multi["group"].nunique(),
            "likely wrong groups": int(flags.sum()),
            "names in likely wrong groups": int(multi["likely_wrong"].sum()),
            "families in likely wrong groups (% of name-family links)":
                round(100 * multi.loc[multi["likely_wrong"], "families"].sum() / df["families"].sum(), 1),
        })
    result = pd.DataFrame(rows)
    result["Terrorizer setting"] = ["" if m != "Terrorizer" else str(best) for m in result["method"]]
    result.to_csv(HERE / "results_sector_check.csv", index=False)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
