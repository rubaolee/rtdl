# V4 Benchmark Harness Protocol

The tutorial programs teach small RTDL V4 ideas. The benchmark app runners add
a repeatable measurement protocol around those ideas.

Use this checklist when you move from a tutorial program to a benchmark app:

1. Prepare data once when the structure can be reused.
2. Run one warmup pass before timing.
3. Measure the hot relation work separately from setup and validation.
4. Measure continuation work separately when the app reduces rows after the RT
   relation is built.
5. Record the result validation rule.
6. Record capacity or overflow behavior when an operator keeps only a bounded
   number of rows.
7. Keep the end-to-end application time separate from the hot-path time.

## Minimal Protocol Shape

```python
from time import perf_counter

def timed(label, fn):
    start = perf_counter()
    value = fn()
    return label, value, perf_counter() - start

def prepare():
    return {"prepared": True, "capacity": 2}

def hot(prepared):
    rows = [{"group": 1, "value": 3}, {"group": 1, "value": 4}]
    overflowed = len(rows) > prepared["capacity"]
    return {"rows": rows[: prepared["capacity"]], "overflowed": overflowed}

def validate(result):
    return sum(row["value"] for row in result["rows"]) == 7 and not result["overflowed"]

_, prepared, setup_s = timed("setup", prepare)
timed("warmup", lambda: hot(prepared))
_, result, hot_s = timed("hot", lambda: hot(prepared))
_, ok, validation_s = timed("validation", lambda: validate(result))

print({"setup_s": setup_s, "hot_s": hot_s, "validation_s": validation_s, "correct": ok})
```

## What `--run-harness` Means

The clean `v4_app.py` files are the user entrypoints for app structure. Use
`--run-harness` when you want the fuller runner that prepares larger fixtures,
repeats measurements, and prints detailed records.

The important rule is simple: do not mix protocol numbers. A hot-path number
answers "how fast was the measured operator path?" An end-to-end number answers
"how long did the whole app runner take?" Both are useful, but they should stay
separate.

## Capacity And Overflow

Some app paths keep a bounded number of rows per group. A correct runner must
report when the bound was too small. Silent row loss is not a valid result.

The same idea appears in contact witnesses, nearest/ranked summaries, and
limited row collection.
