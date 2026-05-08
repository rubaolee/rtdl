# Goal 1579: Next-Architecture Derived Carry Alias Validation

## Verdict

`goal1579_next_arch_validation_recorded`

## Acceptance

- Baseline accepted: `True`
- Alias accepted: `True`
- Baseline parity: `True`
- Alias parity: `True`
- Baseline topology: `True`
- Alias topology: `True`

## Sweep

| Count | Baseline ms | Alias ms | Delta ms | Baseline payload copies | Alias payload copies | Parity |
|---:|---:|---:|---:|---:|---:|---|
| 7 | 0.052350 | 0.087756 | 0.035406 | 0 | 0 | True |
| 8192 | 0.115850 | 0.129806 | 0.013956 | 0 | 0 | True |
| 12289 | 0.140496 | 0.140046 | -0.000450 | 1 | 1 | True |
| 16385 | 0.183868 | 0.164282 | -0.019586 | 3 | 0 | True |
| 20481 | 0.166656 | 0.164311 | -0.002345 | 2 | 1 | True |
| 24577 | 0.169211 | 0.174661 | 0.005450 | 2 | 1 | True |
| 32769 | 0.218634 | 0.200139 | -0.018495 | 4 | 0 | True |
| 45057 | 0.208605 | 0.207463 | -0.001142 | 2 | 1 | True |
| 49153 | 0.225006 | 0.214326 | -0.010680 | 3 | 1 | True |
| 65536 | 0.217572 | 0.216430 | -0.001142 | 0 | 0 | True |
| 65537 | 0.293937 | 0.269571 | -0.024366 | 5 | 0 | True |

## Claim Boundary

This runner records validation evidence only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
