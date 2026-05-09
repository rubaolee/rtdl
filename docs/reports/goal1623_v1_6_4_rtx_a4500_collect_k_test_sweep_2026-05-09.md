# Goal1623 v1.6.4 RTX A4500 Collect-K Test Sweep

Date: 2026-05-09

## Verdict

ACCEPTED as latest-main RTX A4500 collect-k test-sweep evidence.

This is not public speedup evidence, not true zero-copy evidence, not stable
`COLLECT_K_BOUNDED` promotion, and not release action.

## Environment

- Pod SSH endpoint: `root@213.173.108.199 -p 18169`
- Checkout: `/root/work/rtdl`
- Git commit: `f4e28bf259021e431150172ed494ab7e3592057c`
- GPU: `NVIDIA RTX A4500`
- Driver: `550.127.05`
- GPU memory: `20470 MiB`
- Test transcript:
  `docs/reports/goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_2026-05-09.txt`

## Scope

The pod pulled pushed GitHub `main`, reset the checkout to `origin/main`, and
ran every `tests/*collect_k*test.py` module with:

```bash
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=$PWD/build:${LD_LIBRARY_PATH:-}
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
python3 -m unittest <100 collect-k test modules>
```

## Outcome

- Collect-k test modules discovered: `100`
- Tests run: `390`
- Result: `OK`
- Return code: `0`

This sweep also verifies the small Goal1573 helper-gate cleanup committed at
`f4e28bf259021e431150172ed494ab7e3592057c`, after an earlier stale source-string
assertion exposed that the derived-carry-alias diagnostic helper was being
bypassed by an inline env check.

## Claim Boundary

Goal1623 is latest-main RTX A4500 test-sweep evidence for the collect-k
development track. It does not authorize public speedup wording, true zero-copy
wording, whole-app speedup claims, broad RTX/GPU wording, stable
`COLLECT_K_BOUNDED` promotion, release tags, or release action.

Stable promotion remains blocked until a separate stable-promotion decision
package and explicit 3-AI consensus accepts it.
