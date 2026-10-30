# Working on TIP: resources, VS Code, and not losing work

Practical notes for the team on running the course notebooks on the EPO Technology Intelligence Platform (TIP).

## Where things run

```
Your laptop (VS Code)      →  TIP server (your Python kernel)   →  BigQuery (PATSTAT itself)
editor and display only       runs pandas and models;               the database; runs the SQL
                              4 cores · 32 GB RAM · 30 GB disk      (filters, joins, counts)
```

- **BigQuery** is the Google database service where PATSTAT is stored. Filtering, joins and aggregations in a query run there, on Google's machines.
- **Your TIP server** is a personal container on the EPO's cloud. The *results* of each query are loaded into Python there, so the RAM and disk limits that matter are TIP's, not your laptop's.
- **Your laptop** only shows the editor. With a remote kernel, a more powerful laptop doesn't help.

Each team member has their own TIP server. Files you save on TIP are **not visible to the others**.

## Connecting from VS Code (optional)

The code runs on TIP either way, so results are identical whether you use VS Code or JupyterLab in the browser. VS Code makes git and editing easier.

1. Install the **Jupyter** and **JupyterHub** extensions (Microsoft) in VS Code.
2. Start your TIP server by opening TIP in the browser. VS Code cannot start it.
3. In TIP: **File → Hub Control Panel → Token**, then request an API token.
4. In VS Code, open a notebook and choose **Select Kernel → Existing JupyterHub Server**. Enter the TIP URL (up to `/hub/`), your username and the token.
5. Test the connection:
   ```python
   from epo.tipdata.patstat import PatstatClient
   PatstatClient()   # should print the TEST-database message
   ```

Keep a TIP browser tab open as well, for the **resource meters** (top right), the **terminal** and **restarting the server**.

> The `.ipynb` file is on your laptop, but anything the code reads or writes (`read_csv`, `to_csv`, saved figures, `%pip install`) happens **on TIP**.

## Using resources efficiently

Limits per user: **4 CPU cores · 32 GB RAM · 30 GB disk · a 7-day download quota**.

| Resource | What happens at the limit |
|---|---|
| CPU | Work beyond 4 cores just runs slower |
| RAM | At 100% the kernel **crashes or hangs** and all variables are lost |
| Disk | At 100% the server can break and **may not restart**. Free space immediately |
| Download | The connection is throttled to almost nothing |

### RAM

- **Let the database do the work.** Use `WHERE`, `COUNT`, `GROUP BY` in the query instead of downloading everything and filtering in pandas. "Patents per year" should come back as ~30 rows, not millions.
- **Select only the columns you need.** Abstracts and titles are long text and take a lot of memory.
- **Check the size before running a big query on PROD.** Run a `COUNT(*)` first, or test with `LIMIT 1000`.
- **Develop on TEST, run the final version on PROD.** `PatstatClient()` uses TEST (~10k documents) by default; use `PatstatClient(env="PROD")` for the full database.
- **Free large objects** with `del df`. Check a DataFrame's size with `df.memory_usage(deep=True).sum() / 1e9` (GB).
- **Shut down kernels you aren't using.** Each open kernel holds its own RAM.

### Disk

- Delete old exports you no longer need.
- Clear caches from the TIP terminal: `pip cache purge`, and downloaded models in `~/.cache/huggingface`.
- See what takes space: `du -sh ~/* ~/.cache/* | sort -h`

### Downloads

- Display `df.head()`, not a 100,000-row DataFrame. Output shown in VS Code likely counts toward the quota as well.

## Not losing work

| What | Where it lives | How it's lost | Protection |
|---|---|---|---|
| Code (`.ipynb`) | Your laptop (VS Code) or your TIP folder (browser) | Not saving or not pushing | Save often; commit and push often |
| Variables in the kernel | TIP RAM | Crash, disconnect, idle shutdown, restart | Save results to files (below) |
| Saved files (CSV, parquet) | Your TIP disk | Deleting them, or the disk filling up | Keep only what matters; commit small results |

**Save the result of every slow query to a file right away**, so that after a crash you load the file instead of re-running the query:

```python
from pathlib import Path

CACHE = Path.home() / "cache"
CACHE.mkdir(exist_ok=True)

def cached(name, run):
    """Load a saved result if one exists, otherwise run the query and save it."""
    path = CACHE / f"{name}.parquet"
    if path.exists():
        return pd.read_parquet(path)
    df = run()
    df.to_parquet(path)
    return df

df_ai = cached("ai_patents_PROD", lambda: patstat.df(q_ai))
```

- Put `TEST` or `PROD` in the name so you never mix them up.
- **Delete the file when you change the query**, otherwise you keep loading the old result.
- Parquet needs `pyarrow`. If it's missing, install it with `%pip install pyarrow`.

## Getting the same results as your teammates

- **Push the code, and optionally the outputs.** Saved cell outputs are visible on GitHub without re-running. Variables and files on your TIP server are not shared.
- **Use the same database.** TEST and PROD give completely different numbers. All final numbers come from PROD.
- **Note the PATSTAT edition.** It is updated twice a year, so counts can change slightly after an update.
- **Sort before `head()` or `LIMIT`.** Without `ORDER BY`, BigQuery may return rows in a different order on each run.
- **Fix random seeds** (e.g. `random_state=42` for UMAP).
- **Don't edit the same notebook at the same time.** Notebook merge conflicts are painful. Use one notebook per person, or take turns. `nbdime` makes notebook diffs readable.
- **Check the PATSTAT licence before committing raw data exports**, especially to a public repo. Code and aggregated results (counts, charts) are normally fine.

## Daily routine

1. Start your TIP server, from the browser.
2. `git pull`, then connect VS Code to the TIP kernel (or work in JupyterLab).
3. Work, caching slow query results as you go.
4. Save, commit, push.
5. Stop the server: **File → Hub Control Panel → Stop My Server**.
