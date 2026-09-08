# RTDL application-performance projection

This anonymous package supports a standard-library-only offline recount of the
separate long-workload application transaction described in the paper. It does
not install RTDL, run GPU code, reproduce private custody, or contain the raw
GPU archive.

From the extracted package root, run:

```sh
python3 verify.py --artifact-root .
python3 -O verify.py --artifact-root .
```

Both commands must print one JSON object with status
`PASS__APPLICATION_PROJECTION_RECOUNT` and exit zero. See `CLAIM_SCOPE.md` for
the exact interpretation.
