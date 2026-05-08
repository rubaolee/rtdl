# Goal 1524: v1.5 Gate Cross-Platform Rerun

## Verdict

The v1.5 primitive, migration, readiness, support-maturity, benchmark-evidence,
and public-wording gate batch is green on both Windows and the local Linux
validation host after the recent v1.5.4 non-pod work.

This is local/non-pod regression evidence only. It does not authorize new
public performance claims, stable `COLLECT_K_BOUNDED` promotion, true zero-copy
wording, or release action.

## Run Scope

The rerun covered the focused v1.5 gate batch from Goal1274 through Goal1408,
including:

- stable primitive contract and v1.5 blocker gates;
- generic any-hit/count and prepared any-hit/count paths;
- fixed-radius threshold count, grouped reductions, scalar reductions, and
  float min/max empty-input guards;
- app migration inventory for robot, DB, polygon, and Jaccard paths;
- internal readiness, standalone release, correctness, maturity, benchmark
  evidence, and public wording gates.

## Windows Result

```text
Ran 138 tests in 0.487s
OK
```

## Linux Result

Host: `192.168.1.20`

```text
Ran 138 tests in 0.105s
OK
```

## Claim Boundary

Goal1524 is a targeted local Windows plus Linux gate rerun. It does not prove
new OptiX pod performance, does not authorize public speedup wording, does not
authorize broad RTX/GPU wording, does not authorize whole-app claims, does not
authorize true zero-copy wording, does not promote `COLLECT_K_BOUNDED` to a
stable public primitive, and does not authorize release action.
