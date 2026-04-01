# Goal 23 Table 3 Bounded Results

Executed rows are bounded local analogues only. Missing families remain explicitly unexecuted.

| Paper Pair | Workload | Local Case | Fidelity | Execution Status | CPU Mean (s) | Embree Mean (s) | Speedup | Note |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| County ⊲⊳ Zipcode | `lsi` | `county_fixture_subset_lsi` | `fixture-subset` | `executed-local-analogue` | 0.000072 | 0.000124 | 0.58x | County-side local analogue only; zipcode exact-input not yet acquired. |
| County ⊲⊳ Zipcode | `lsi` | `county_tiled_x8_lsi` | `derived-input` | `executed-local-analogue` | 0.000732 | 0.000208 | 3.52x | Deterministic county fixture enlargement; zipcode exact-input not yet acquired. |
| County ⊲⊳ Zipcode | `pip` | `county_fixture_subset_pip` | `fixture-subset` | `executed-local-analogue` | 0.000073 | 0.000092 | 0.80x | County-side local analogue only; zipcode exact-input not yet acquired. |
| County ⊲⊳ Zipcode | `pip` | `county_tiled_x8_pip` | `derived-input` | `executed-local-analogue` | 0.001114 | 0.000322 | 3.46x | Deterministic county fixture enlargement; zipcode exact-input not yet acquired. |
| Block ⊲⊳ Water | `lsi` | `missing` | `missing/unacquired` | `missing` | - | - | - | Add public acquisition and conversion path before any bounded local analogue is treated as complete. |
| Block ⊲⊳ Water | `pip` | `missing` | `missing/unacquired` | `missing` | - | - | - | Add public acquisition and conversion path before any bounded local analogue is treated as complete. |
| LKAF ⊲⊳ PKAF | `lsi` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKAF ⊲⊳ PKAF | `pip` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKAS ⊲⊳ PKAS | `lsi` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKAS ⊲⊳ PKAS | `pip` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKAU ⊲⊳ PKAU | `lsi` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKAU ⊲⊳ PKAU | `pip` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKEU ⊲⊳ PKEU | `lsi` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKEU ⊲⊳ PKEU | `pip` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKNA ⊲⊳ PKNA | `lsi` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKNA ⊲⊳ PKNA | `pip` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKSA ⊲⊳ PKSA | `lsi` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
| LKSA ⊲⊳ PKSA | `pip` | `missing` | `missing/unacquired` | `missing` | - | - | - | Acquire or derive the continent pair before bounded local runs. |
