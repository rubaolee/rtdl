# Goal 22 Table 3 Analogue

This table records the current RTDL-on-Embree status for the RayJoin Table 3 targets.

| Paper Pair | Workload | Dataset Handle | Dataset Status | Preferred Provenance | Local Profile | Current State |
| --- | --- | --- | --- | --- | --- | --- |
| County ⊲⊳ Zipcode | `lsi` | `USCounty__Zipcode` | `partial` | `exact-input preferred` | `table3_pair_bounded_local` | Use the checked-in county fixture for parity now; add zipcode acquisition and conversion in a later Goal 22 slice. |
| County ⊲⊳ Zipcode | `pip` | `USCounty__Zipcode` | `partial` | `exact-input preferred` | `table3_pair_bounded_local` | Use the checked-in county fixture for parity now; add zipcode acquisition and conversion in a later Goal 22 slice. |
| Block ⊲⊳ Water | `lsi` | `USACensusBlockGroupBoundaries__USADetailedWaterBodies` | `missing` | `exact-input preferred` | `table3_pair_bounded_local` | Add public acquisition and conversion path before any bounded local analogue is treated as complete. |
| Block ⊲⊳ Water | `pip` | `USACensusBlockGroupBoundaries__USADetailedWaterBodies` | `missing` | `exact-input preferred` | `table3_pair_bounded_local` | Add public acquisition and conversion path before any bounded local analogue is treated as complete. |
| LKAF ⊲⊳ PKAF | `lsi` | `lakes_parks_Africa` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKAF ⊲⊳ PKAF | `pip` | `lakes_parks_Africa` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKAS ⊲⊳ PKAS | `lsi` | `lakes_parks_Asia` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKAS ⊲⊳ PKAS | `pip` | `lakes_parks_Asia` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKAU ⊲⊳ PKAU | `lsi` | `lakes_parks_Australia` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKAU ⊲⊳ PKAU | `pip` | `lakes_parks_Australia` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKEU ⊲⊳ PKEU | `lsi` | `lakes_parks_Europe` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKEU ⊲⊳ PKEU | `pip` | `lakes_parks_Europe` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKNA ⊲⊳ PKNA | `lsi` | `lakes_parks_North_America` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKNA ⊲⊳ PKNA | `pip` | `lakes_parks_North_America` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKSA ⊲⊳ PKSA | `lsi` | `lakes_parks_South_America` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |
| LKSA ⊲⊳ PKSA | `pip` | `lakes_parks_South_America` | `missing` | `exact-input preferred, derived-input acceptable` | `table3_pair_bounded_local` | Acquire or derive the continent pair before bounded local runs. |

Local profile policy: `<=2 minutes per workload per pair; <=10 minutes total package`.
