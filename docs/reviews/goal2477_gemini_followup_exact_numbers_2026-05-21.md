The report table values in `docs/reports/goal2477_intersection_direct_grouped_union_experiment_2026-05-21.md` have been verified against the source data in `docs/reports/goal2477_direct_side_effect_ab_off/summary.json` and `docs/reports/goal2477_direct_side_effect_ab_on/summary.json`. All median values in the results table are exact when rounded to 10 decimal places.

### Verification Results

| Metric | Point Count | Report Value | Source Value (Full Precision) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Total median off** | 32768 | `0.0449019494 s` | `0.0449019493535161` | **Match** |
| **Total median direct** | 32768 | `0.0455493266 s` | `0.045549326576292515` | **Match** |
| **Grouped native off** | 32768 | `0.0249677366 s` | `0.024967736564576626` | **Match** |
| **Grouped native direct** | 32768 | `0.0252259923 s` | `0.025225992314517498` | **Match** |
| **Total median off** | 65536 | `0.1091199862 s` | `0.10911998618394136` | **Match** |
| **Total median direct** | 65536 | `0.1088011730 s` | `0.10880117304623127` | **Match** |
| **Grouped native off** | 65536 | `0.0691061830 s` | `0.06910618301481009` | **Match** |
| **Grouped native direct** | 65536 | `0.0679963250 s` | `0.06799632497131824` | **Match** |

**Verdict: Accepted**
