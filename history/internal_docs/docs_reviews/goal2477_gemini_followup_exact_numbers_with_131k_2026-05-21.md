I have verified the median numbers in `docs/reports/goal2477_intersection_direct_grouped_union_experiment_2026-05-21.md` against the referenced artifact summaries.

### Verification Results

All report table values for scales 32768, 65536, and 131072 match the artifact JSON files exactly (when rounded to 10 decimal places as shown in the report):

| Scale | Metric | Report Value | Artifact Value (Full Precision) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **32768** | Total median off | 0.0449019494 s | 0.0449019493535161 | Match |
| | Total median direct | 0.0455493266 s | 0.045549326576292515 | Match |
| | Grouped native off | 0.0249677366 s | 0.024967736564576626 | Match |
| | Grouped native direct | 0.0252259923 s | 0.025225992314517498 | Match |
| **65536** | Total median off | 0.1091199862 s | 0.10911998618394136 | Match |
| | Total median direct | 0.1088011730 s | 0.10880117304623127 | Match |
| | Grouped native off | 0.0691061830 s | 0.06910618301481009 | Match |
| | Grouped native direct | 0.0679963250 s | 0.06799632497131824 | Match |
| **131072** | Total median off | 0.3323279414 s | 0.33232794143259525 | Match |
| | Total median direct | 0.3347260887 s | 0.33472608868032694 | Match |
| | Grouped native off | 0.2503216779 s | 0.2503216778859496 | Match |
| | Grouped native direct | 0.2511681039 s | 0.25116810388863087 | Match |

**Verdict: Accepted**
