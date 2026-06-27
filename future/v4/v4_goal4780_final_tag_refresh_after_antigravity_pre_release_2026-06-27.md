# V4 Goal4780 Final Tag Refresh After Antigravity Pre-Release Approval

Date: 2026-06-27

Status: `ready_to_refresh_v4_0_0_tag_after_antigravity_pre_release_approval`

## External Approval

Antigravity approved the V4 pre-release items 1-5 packet:

- review: `future/v4/reviews/antigravity_v4_pre_release_items_1_to_5_completion_2026-06-27.md`
- verdict: `approve_v4_pre_release_items_1_to_5_complete`
- authorization: proceed to final Linux tagging and clean-checkout validation.

This closes the pre-release items 1-5 blocker that was previously left open
because the Antigravity CLI produced no stdout.

## Final Pre-Tag Validation

Windows:

```text
py -3 scripts/v4_release_clean_checkout_gate.py
status: passed

py -3 -m unittest discover -s tests -p "v4*.py"
Ran 659 tests in 122.585s
OK (skipped=1)
```

Linux clean checkout (`192.168.1.20`,
`/home/lestat/work/rtdl_v4_release_final_20260627`):

```text
python3 scripts/v4_release_clean_checkout_gate.py
status: passed

python3 -m unittest discover -s tests -p 'v4*.py'
Ran 659 tests in 43.006s
OK (skipped=1)
```

## Tag Policy

The public release tag is `v4.0.0`.

The tag target commit is resolved by the Git tag object itself. Public docs do
not hard-code a commit SHA.

After this record is committed, the release procedure is:

```text
git tag -f -a v4.0.0 -m "RTDL V4.0.0" HEAD
git push --force origin refs/tags/v4.0.0
py -3 scripts/v4_release_clean_checkout_gate.py --require-tag-head
```

Then the Linux clean checkout must force-fetch the tag and run:

```text
python3 scripts/v4_release_clean_checkout_gate.py --require-tag-head
```

## Claim Boundary

The tag refresh does not add new performance claims. The current public boundary
remains:

- V4.0.0 is a published Python eDSL/operator-pushdown release and V2/V3
  superset.
- The NVIDIA RT-core 10-app V2.14/V3.0.2/V4.0 matrix is complete.
- V4.0 has bounded material rows over V2.14 and similar-speed rows elsewhere.
- Broad all-app speedup, public true-zero-copy, raw OptiX callbacks, Tier-3
  PTX/module callbacks, C ABI/embedding, non-Python host bindings, and broad
  CuPy performance claims remain unauthorized.

