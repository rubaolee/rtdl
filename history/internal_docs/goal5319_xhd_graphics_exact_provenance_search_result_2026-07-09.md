# Goal5319 - X-HD Graphics Exact-Provenance Search Result

## Verdict

```text
completed_graphics_exact_provenance_not_found_keep_level_b
```

Goal5319 searched whether the current public Stanford graphics candidates can
be promoted from Level-B same-source evidence to exact paper-input provenance.
They cannot be promoted yet.

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
```

## What Was Searched

This goal did not run new author or RTDL performance code. It searched and
consolidated:

- Goal5297 dataset acquisition manifest and local Stanford archive/file hashes.
- Goal5298 author-only graphics value precheck on current POD uploads.
- Goal5291 Dragon -> HappyBuddha Level-B status matrix.
- Goal5299 / Goal5300 Thai graphics RTDL comparison matrices.
- Goal5316 Figure-5 / Level-B status matrix.
- Paper-branch log mapping records for graphics basenames and point counts.
- Public Stanford archive HTTP HEAD metadata for four source archives.
- Repository evidence for graphics author hashes or preprocessing provenance.

## Public Same-Source Assets

Current public Stanford assets are well pinned:

```text
dragon_vrip.ply:
  vertices = 437,645
  sha256 = fea87ff48f2aba22fb53e7b67c3ff3f7b8c2a3b3a0653af62c48bba67c6d5744
  archive = https://graphics.stanford.edu/pub/3Dscanrep/dragon/dragon_recon.tar.gz

happy_vrip.ply:
  vertices = 543,652
  sha256 = 2283371216d748a08376a3c88698e283cc8f18d10ced348d6d133051bcf217ab
  archive = https://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz

asian_dragon.ply:
  vertices = 3,609,600
  sha256 = 4a31c6b8951b0f9f4b351d183cb5d5d27e2d1a5916b27e6516acfb9a91ad7f85
  archive = https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_dragon.ply.gz

thai_statuette.ply:
  vertices = 4,999,996
  sha256 = 01470da9fc1241dcb4b075cc057ff6bf88d8dc721ce24b5847b9efdfbb8c0345
  archive = https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_statuette.ply.gz
```

These hashes prove the local public assets. They do not prove that the author
used byte-identical inputs under `/local/storage/shared/HDDatasets/graphics`.

## Pair Status

Author-only precheck status:

```text
dragon -> happy_buddha:
  matched paper log = true
  paper log = 0.12572969496250153
  author rerun = 0.12572988867759705
  abs diff = 1.9371509552001953e-07

dragon -> asian_dragon scaled:
  matched paper log = false
  paper log = 0.06536811590194702
  author rerun = 0.06545527279376984
  abs diff = 8.715689182281494e-05

thai_statuette scaled -> happy_buddha:
  matched paper log = true
  paper log = 0.21912434697151184
  author rerun = 0.21912431716918945
  abs diff = 2.9802322387695312e-08

thai_statuette scaled -> asian_dragon scaled:
  matched paper log = true
  paper log = 0.28763845562934875
  author rerun = 0.28763842582702637
  abs diff = 2.9802322387695312e-08
```

Therefore the current graphics status is:

```text
3 value-matched Level-B graphics candidates
1 author-value no-go: dragon -> asian_dragon under current public/scaled mapping
```

RTDL evidence exists for the matched candidates, but it remains Level-B:

- Dragon -> HappyBuddha is the strongest current graphics Level-B row. Its
  RTDL route uses global-bound early break and is exact scalar only, not exact
  per-source witnesses.
- Thai graphics rows match scalar values, but their `1e-3` scaled inputs are
  app-owned conversions without author preprocessing proof.

## Why This Is Still Not Exact

Exact graphics paper-input status would require one of:

```text
author-provided graphics input files or archives
author-provided hashes for dragon.ply/happy_buddha.ply/asian_dragon.ply/thai_statuette.ply
byte-identical regenerated point files from a documented author preprocessing pipeline
external review accepting public Stanford archives plus documented app-owned scaling as exact-equivalent
```

Goal5319 found none of these.

Negative findings:

```text
author graphics files found = false
author graphics hashes found = false
byte-identical regeneration proven = false
author scaling/preprocessing proven = false
public Stanford archives exact-equivalence proven = false
external review accepting public graphics as exact = false
```

The paper logs provide basenames and point counts. That is not enough.

The public Stanford archives are excellent same-source evidence. They are not
the author's exact `HDDatasets/graphics/*.ply` byte provenance.

The scaled AsianDragon and ThaiStatuette files are app-owned `1e-3` conversions.
Even when they value-match paper logs, they are not author preprocessing proof.

## Decision

```text
exit_label = graphics_exact_provenance_not_found_keep_level_b
```

Allowed summary:

```text
Current public Stanford graphics assets provide strong Level-B same-source
evidence: three author reruns value-match paper logs and RTDL matches those
author reruns on the tested routes. Exact graphics paper-input provenance is
still not proven because author files/hashes and author preprocessing/scaling
proof are missing; Dragon->Asian remains a no-go under the current public/scaled
mapping.
```

Forbidden summaries:

```text
Public Stanford graphics files are proven byte-identical to author HDDatasets inputs.
The app-owned scaled AsianDragon/ThaiStatuette files are proven author preprocessing outputs.
All four Figure-5 graphics pairs are value-matched.
Figure 5 graphics is reproduced exactly.
Author-vs-RTDL graphics performance ratio is authorized.
```

## Validation

Commands run:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5319_graphics_exact_provenance_search.json
py -m unittest tests.goal5319_xhd_graphics_exact_provenance_search_test
```

Result:

```text
Ran 6 tests OK
```

The local Python launcher also printed the known noisy environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

Do not spend more RTDL timing on Dragon -> Asian under the current mapping.

Next productive routes are:

1. Seek external author graphics files/hashes or preprocessing/scaling scripts.
2. Keep Dragon -> HappyBuddha and the Thai matched rows as Level-B evidence.
3. Move to another exact-input target if no external graphics provenance
   appears.

POD is not needed unless a concrete provenance or value-matched input lead
requires author/RTDL verification.
