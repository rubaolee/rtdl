# Goal5845 causal-wording correction

Date: 2026-09-05

Status: `HISTORICAL_RESULT_PRESERVED__CAUSAL_WORDING_CORRECTED`

This addendum corrects the mechanism description in
`FINAL_ENGINEERING_REPORT.md` without mutating its historical bytes, samples,
authority, or exact-arm result.

The exact Goal5845 measurement remains:

- RTDL prepared public median: 366,340 ns;
- pinned compatible-API PyOptix median: 3,486,126 ns;
- median within-block RTDL/PyOptix: `0.1049444491x`;
- reciprocal for those exact arms: `9.5288508222x`.

The accurate implementation contrast is:

1. RTDL performs semantic duplicate removal on the device, transfers the
   resulting 4,096 packed rows, and then performs final `std::sort` and
   `std::unique` over the native host buffer.
2. The pinned compatible PyOptix arm transfers 8,192 raw events, converts them
   through NumPy into Python list/tuple objects, and performs Python
   `sorted(set(...))` to return 4,096 canonical rows.

Therefore the old phrase "semantic sort/unique compaction before transfer" is
too broad. Device-side deduplication occurs before transfer; final canonical
ordering/uniquing still occurs on RTDL's native host path.

No measured phase decomposition attributes the 9.53x exact-arm difference
among D2H volume, NumPy/Python object conversion, allocation, Python set/sort,
native packed-row work, or other boundary costs. Row count alone cannot supply
that causal attribution.

The exact ratio remains valid internal evidence about the two named
implementations. It is not a best-possible PyOptix baseline, an intrinsic RTDL
speedup, or paper-facing performance evidence. Goal5848's strong device-
continuation PyOptix Arm C is the required paper comparator.
