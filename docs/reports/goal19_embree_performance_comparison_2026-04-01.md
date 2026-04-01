# Goal 19 Report: RTDL vs Native Embree Performance Comparison

## Scope

Goal 19 compares the current RTDL Embree runtime modes against the pure native C++ + Embree executables on matched `lsi` and `pip` workloads.

- fixture repeats: `25`
- larger-profile repeats: `20`
- total wall time: `8.74 min`

## Deterministic Fixture Comparison

### lsi

- build/probe: `200` / `120`
- dict matches native: `True`
- raw matches dict: `True`
- prepared raw matches dict: `True`
- dict median: `0.025207709 s`
- raw median: `0.001355875 s`
- prepared raw median: `0.000961084 s`
- native median: `0.001882791 s`
- dict gap vs native: `13.39x`
- raw gap vs native: `0.72x`
- prepared raw gap vs native: `0.51x`

### pip

- build/probe: `200` / `120`
- dict matches native: `True`
- raw matches dict: `True`
- prepared raw matches dict: `True`
- dict median: `0.011843875 s`
- raw median: `0.000687583 s`
- prepared raw median: `0.000319666 s`
- native median: `0.000377791 s`
- dict gap vs native: `31.35x`
- raw gap vs native: `1.82x`
- prepared raw gap vs native: `0.85x`

## Larger Profile Comparison

### lsi

- build/probe: `2000` / `1500`
- dict matches native: `True`
- dict median: `7.787854041 s`
- raw median: `0.075481354 s`
- prepared raw median: `0.068297104 s`
- native median: `0.076683750 s`
- dict gap vs native: `101.56x`
- raw gap vs native: `0.98x`
- prepared raw gap vs native: `0.89x`

### pip

- build/probe: `2500` / `2000`
- dict matches native: `True`
- dict median: `16.801933437 s`
- raw median: `0.064903604 s`
- prepared raw median: `0.062115667 s`
- native median: `0.074566666 s`
- dict gap vs native: `225.33x`
- raw gap vs native: `0.87x`
- prepared raw gap vs native: `0.83x`

## Interpretation

This report answers the current Embree-phase performance question only for `lsi` and `pip`, because those are the workloads with real native C++ baselines. The larger-profile section uses matched inputs and native summary hashes to ensure correctness before timing claims.
