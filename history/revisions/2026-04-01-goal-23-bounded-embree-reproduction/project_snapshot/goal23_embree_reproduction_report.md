# Goal 23 Embree Reproduction Report

- Generated: `2026-04-01T12:11:56`
- Boundary: `bounded-local executable slice only; missing source-identified families remain reported but unexecuted`
- Total package wall time: `286.25 s`

## Executed Slice

- Table 3: partial bounded local analogue rows only
- Figure 13: bounded synthetic `lsi` analogue
- Figure 14: bounded synthetic `pip` analogue
- Table 4: bounded overlay-seed analogue
- Figure 15: bounded overlay-seed speedup analogue

## Missing / Unexecuted Families

- `Block ⊲⊳ Water` / `lsi` remains `missing`: Add public acquisition and conversion path before any bounded local analogue is treated as complete.
- `Block ⊲⊳ Water` / `pip` remains `missing`: Add public acquisition and conversion path before any bounded local analogue is treated as complete.
- `LKAF ⊲⊳ PKAF` / `lsi` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKAF ⊲⊳ PKAF` / `pip` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKAS ⊲⊳ PKAS` / `lsi` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKAS ⊲⊳ PKAS` / `pip` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKAU ⊲⊳ PKAU` / `lsi` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKAU ⊲⊳ PKAU` / `pip` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKEU ⊲⊳ PKEU` / `lsi` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKEU ⊲⊳ PKEU` / `pip` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKNA ⊲⊳ PKNA` / `lsi` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKNA ⊲⊳ PKNA` / `pip` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKSA ⊲⊳ PKSA` / `lsi` remains `missing`: Acquire or derive the continent pair before bounded local runs.
- `LKSA ⊲⊳ PKSA` / `pip` remains `missing`: Acquire or derive the continent pair before bounded local runs.

## Table 3 Summary

- `county_fixture_subset_lsi`: `County ⊲⊳ Zipcode` / `lsi` / `fixture-subset` / speedup `0.58x`
- `county_tiled_x8_lsi`: `County ⊲⊳ Zipcode` / `lsi` / `derived-input` / speedup `3.52x`
- `county_fixture_subset_pip`: `County ⊲⊳ Zipcode` / `pip` / `fixture-subset` / speedup `0.80x`
- `county_tiled_x8_pip`: `County ⊲⊳ Zipcode` / `pip` / `derived-input` / speedup `3.46x`

## Table 4 Summary

- `overlay_fixture_subset`: `overlay-seed analogue / fixture-subset` / speedup `0.89x`
- `overlay_tiled_x8`: `overlay-seed analogue / derived-input` / speedup `1.34x`

## Figure Artifacts

- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/figures/figure13_lsi_bounded.svg`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/figures/figure14_pip_bounded.svg`
- `/Users/rl2025/rtdl_python_only/build/goal23_reproduction/figures/figure15_overlay_speedup_bounded.svg`

## Fidelity Labels

- `fixture-subset`: checked-in tiny public subset
- `derived-input`: deterministic enlargement or bounded reduction from an available source
- `synthetic-input`: deterministic synthetic generator
- `overlay-seed analogue`: current RTDL overlay path, not full polygon materialization
