# Goal5298 - X-HD Author-Only Graphics Level-B Precheck

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5298 executes the next step recommended by Goal5297:

```text
Upload the missing public Stanford graphics files to the current POD and run
author-only Level-B graphics value prechecks before any new RTDL comparison.
```

This is a data/provenance and author-denominator step. It does not run RTDL.

## POD

```text
host = 213.173.108.24
port = 13502
wrapper = scripts/current_pod_ssh.py
preflight = POD_OK
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
```

Author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

## Upload / Data State

Goal5298 uses:

```text
/tmp/xhd_goal5298/data/dragon.ply
/tmp/xhd_goal5298/data/happy_buddha.ply
/tmp/xhd_goal5298/data/asian_dragon.ply
/tmp/xhd_goal5298/data/asian_dragon_scaled_1e-3.ply
/tmp/xhd_goal5298/data/thai_statuette.ply
/tmp/xhd_goal5298/data/thai_statuette_scaled_1e-3.ply
```

The missing files from Goal5297 were uploaded with the POD wrapper:

```text
happy_buddha.ply
thai_statuette.ply
thai_statuette_scaled_1e-3.ply
```

Remote SHA256 checks matched the local Goal5297 manifest:

```text
dragon.ply                         fea87ff48f2aba22fb53e7b67c3ff3f7b8c2a3b3a0653af62c48bba67c6d5744
happy_buddha.ply                   2283371216d748a08376a3c88698e283cc8f18d10ced348d6d133051bcf217ab
asian_dragon.ply                   4a31c6b8951b0f9f4b351d183cb5d5d27e2d1a5916b27e6516acfb9a91ad7f85
asian_dragon_scaled_1e-3.ply       4f98d1f809cfb6dcb448e469fdd94a606de17b45ccb160f5cd1a5423508f01fe
thai_statuette.ply                 01470da9fc1241dcb4b075cc057ff6bf88d8dc721ce24b5847b9efdfbb8c0345
thai_statuette_scaled_1e-3.ply     047024cf12fc541634d02612f0d72ea03ef9babb8239f4ca6a1a6a9422da272e
```

These are still public same-source files, not exact author paper input bytes.

## Command Shape

The app-owned Goal5298 runner invokes the author binary as:

```text
hd_exec
  -input1 <case input1>
  -input2 <case input2>
  -input_type ply
  -n_dims 3
  -serialize /tmp/xhd_goal5298/ser
  -variant rt
  -execution gpu
  -repeat 1
  -json <case output>
  -overwrite=true
  -check=false
  -normalize=false
  -lb=256
```

Runner:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5298_author_graphics_precheck.py
```

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
```

Raw author JSON files:

```text
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/dragon_happy_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/dragon_asian_scaled_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/thai_happy_scaled_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/thai_asian_scaled_author.json
```

## Matrix

```text
case                  author HDResult        paper-log HDResult      abs diff        matched
dragon_happy          0.12572988867759705    0.12572969496250153    1.937e-7       true
dragon_asian_scaled   0.06545527279376984    0.06536811590194702    8.716e-5       false
thai_happy_scaled     0.21912431716918945    0.21912434697151184    2.980e-8       true
thai_asian_scaled     0.28763842582702637    0.28763845562934875    2.980e-8       true
```

Summary:

```text
matched_paper_log_value_count = 3 / 4
all_cases_matched_paper_log_value = false
```

## Interpretation

Three graphics Level-B candidates are now author-rerun value matched to the
paper-branch author logs on the current POD:

```text
Dragon -> HappyBuddha
ThaiStatuette scaled -> HappyBuddha
ThaiStatuette scaled -> AsianDragon scaled
```

Dragon -> AsianDragon remains a no-go for paper-log value matching under the
available local scaled mapping:

```text
paper log target = 0.06536811590194702
current POD author rerun = 0.06545527279376984
abs diff = 8.715689182281494e-05
```

This confirms the earlier Dragon -> AsianDragon warning rather than resolving
it.

## What This Enables

Allowed next work:

```text
1. Use the three value-matched cases as Level-B graphics candidates for
   author-only diagnostics or later RTDL comparison.
2. Keep Dragon -> AsianDragon out of value-matched Figure 5 / graphics matrix
   claims unless a better input/provenance mapping is found.
3. If proceeding to RTDL, start with one of the matched candidates and keep the
   same denominator split: author HDResult, author Running.AvgTime, author
   process wall, RTDL route wall, RTDL total, and load/setup.
```

## Claim Boundary

Not authorized:

```text
exact paper dataset reproduction
full X-HD paper reproduction
Figure 5 reproduction
Figure 7 reproduction
Figure 8 reproduction
Figure 10 reproduction
RTDL comparison from Goal5298
author-vs-RTDL performance ratio
promoting public Stanford files to exact paper inputs
```

## Validation

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
py -m unittest tests.goal5298_xhd_author_graphics_precheck_test
```
