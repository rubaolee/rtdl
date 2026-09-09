# RT-DBSCAN Evidence Replay

The two archives preserve the failed predecessor and passing successor as
separate transactions.  Never pool their samples.

## Integrity

```bash
sha256sum ADVERSE_PREDECESSOR_COMPLETE_BUNDLE.tar.zst
sha256sum SUCCESSOR_COMPLETE_BUNDLE.tar.zst
```

Expected values are recorded in `MANIFEST.json` and `REPORT.md`.

## Successor Recount

The frozen configuration records absolute `/tmp` paths.  Reproduce those paths
rather than editing the configuration, because every referenced file has an
exact path/size/SHA-256 binding.

1. Check out commit `30a2273353d1d128977b0ea99b9194e8af9f3e47` into
   `/tmp/rtdl-dbscan-6d36dec08` with a clean tracked tree.
2. Extract `SUCCESSOR_COMPLETE_BUNDLE.tar.zst` under `/tmp`.
3. Use Python 3.12 with NumPy available and run:

```bash
PYTHONPATH=/tmp/rtdl-dbscan-6d36dec08/src:/tmp/rtdl-dbscan-6d36dec08 \
python /tmp/rtdl-dbscan-6d36dec08/scripts/nine_app_dbscan_formal_compare.py \
  recount \
  --config /tmp/rtdl-dbscan-formal-30a227335/CONFIG.json \
  --preregistration /tmp/rtdl-dbscan-formal-30a227335/PREREGISTRATION.json \
  --measurement-run /tmp/rtdl-dbscan-formal-30a227335/measure/RUN.json \
  --output /tmp/rtdl-dbscan-formal-30a227335/RECOUNT_EXTERNAL.json
```

The recount performs binding checks, independently rereads every retained
output, reruns the complete output comparator, reconstructs every worker and
block statistic, and uses the fixed bootstrap seed in the committed source.
`RECOUNT_EXTERNAL.json` should be byte-identical to the retained
`RECOUNT.json`.

The predecessor can be replayed analogously at commit
`c02eccd79d1acfd51b48a7176f8fe01581293ae8` using its archived path names.
The predecessor is expected to reproduce a failed engineering target, not the
successor result.
