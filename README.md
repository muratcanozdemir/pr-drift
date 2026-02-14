# PR Drift

**Unsupervised pull request drift detection using compression.**

This project implements a zero-dependency, unsupervised detector that models a GitHub repository as a statistical object. Instead of classifying PRs, it measures how much a new PR deviates from the historical distribution of changes using **zstd compression entropy**.

No embeddings. No training. No labels. No ML stack.

Only:

* Git diffs
* Compression
* Statistics

---

## Idea

Given a corpus of historical PR diffs:

```
D = {d1, d2, ..., dn}
```

We treat each diff as a string and define its *information content* as:

```
I(d) = compressed_size(d)
```

For a new PR `d_new`, we compare:

```
I(D ∪ {d_new}) - I(D)
```

This approximates:

> How surprising is this change relative to the past?

If the delta exceeds a threshold, the PR is flagged as **drift**.

---

## Why This Works

Compression algorithms approximate Kolmogorov complexity.

zstd in particular learns byte-level structure:

* file formats
* naming conventions
* diff patterns
* code style
* refactor signatures

If a PR is *structurally alien*, it compresses poorly relative to baseline.

This gives you:

* anomaly detection
* without features
* without models
* without labels

---

## Requirements

* Python **3.14+** (mandatory)
* No third-party dependencies

This relies on:

```python
import compression.zstd
```

If your Python doesn't have this, the project is invalid.

---

## Project Structure

```
pr-drift/
├── pr_drift/
│   ├── __init__.py
│   ├── detector.py
│   ├── storage.py
│   └── server.py
│
├── scripts/
│   └── replay.py
│
├── tests/
│   └── test_detector.py
│
├── pyproject.toml
└── README.md
```

---

## Core Components

### detector.py

Pure logic. No I/O.

* Maintains rolling baseline of diffs
* Computes compression deltas
* Emits z-scores

This is the entire "model".

---

### storage.py

Append-only store of historical PR diffs.

Default backend:

* newline-delimited text
* each entry = raw unified diff

No schema. No metadata. No indexes.

The only invariant:

> Old diffs must never be rewritten.

---

### server.py

Minimal HTTP service.

Endpoints:

```
POST /ingest   -> store new PR diff
POST /score    -> return drift score
```

Intended usage:

* GitHub Actions webhook
* SonarQube hook
* Internal CI pipeline

---

### replay.py

Offline evaluation tool.

Replays a repo history in chronological order and prints:

```
commit_hash, drift_score
```

This lets you:

* plot drift over time
* identify regime changes
* find refactors
* detect team churn

---

## Example

```bash
python scripts/replay.py --repo ./my-repo
```

Output:

```
2022-01-10, 0.12
2022-01-11, 0.09
2022-01-12, 3.87   <-- large refactor
2022-01-13, 0.15
```

---

## What This Is Not

This is not:

* a classifier
* a recommender
* a risk model
* a code quality tool

It does **one thing only**:

> Measures statistical novelty of diffs.

Everything else must be built on top.

---

## Failure Modes

This approach breaks if:

* history is too small
* repo undergoes total rewrite
* diffs are minified or obfuscated
* content is already random

It also cannot distinguish:

* good novelty vs bad novelty
* innovation vs sabotage

It only says:

> "This is weird."
> Not: "This is wrong."

---

## Scientific Status

This is equivalent to:

* Minimum Description Length
* Normalized Compression Distance
* Information-theoretic anomaly detection

There is no learning phase.

The only free parameters are:

* window size
* z-score threshold

These are falsifiable and measurable.

---

## Deployment Philosophy

This should run:

* inside CI
* on air-gapped networks
* without GPUs
* without internet
* without vendor APIs

If you add:

* embeddings
* LLMs
* vector DBs

You have destroyed the point of the project.

---

## License

MIT. Use it, fork it, delete it.

If it works, you don't need this repo anymore.
