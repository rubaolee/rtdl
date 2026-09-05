# Goal5847 Engineering Log

## 2026-09-05T14:33:51Z: Preregistration Frozen

- Implemented a minimal deploy-only AOT DSO with lazy runtime-compiler loading,
  a fail-closed asynchronous provider initialization capability, and the public
  family `.rtdlexe` build/load/bind/prepare route.
- Repaired the PyOptix worker's `(context, logger)` result unpacking before any
  formal transaction.
- Removed the measured prepared-steady RTDL regression by preallocating generic
  bounded-relation ABI storage and reusing an immutable decoded row tuple only
  after byte-identical native output and successful oracle/audit/cache commit.
- Local current-path regression: 191 tests passed with three environment skips.
  A 209-test superset had three known Goal5843 frozen-current-tree replay
  failures caused by later legitimate source evolution; these are not hidden
  or rewritten.
- Exact GPU validation passed relation correctness (4,096 canonical rows),
  triangle correctness (`65530`), true OptiX receipts, zero RTDL runtime
  compiler use, and five isolated mutation rejections.
- Exploratory RTDL steady medians after the repair were 295,638 ns, 297,183 ns,
  and 298,299 ns. Exploratory paired primary ratios were 0.238x, 0.202x, and
  0.278x; later paired post-import ratios were 2.321x and 2.187x. These values
  informed confidence only and are forbidden from the formal sample pool.
- Frozen `PREREGISTRATION.json` before launching any formal worker.

Formal transaction status: `NOT_STARTED`.

