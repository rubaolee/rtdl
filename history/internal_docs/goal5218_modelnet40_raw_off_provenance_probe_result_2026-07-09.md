# Goal5218 ModelNet40 Raw OFF Provenance Probe Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_raw_off_probe__public_raw_off_not_author_paper_input
```

## Purpose

Goal5217 stabilized same-POD phase timing for the current Dragon -> HappyBuddha
Level-B workload. The next full-paper blocker is dataset provenance, not more
route micro-optimization.

Goal5218 probes a second paper-branch workload family: `ModelNet40`.

Question:

```text
Can the public Princeton ModelNet40 raw OFF files be treated as the author
paper inputs for a paper-branch run_all pair?
```

## Public Source

Official Princeton ModelNet page:

```text
https://modelnet.cs.princeton.edu/download.html
```

Official archive:

```text
http://modelnet.cs.princeton.edu/ModelNet40.zip
Content-Length: 2039180837
Content-Type: application/zip
```

The archive was downloaded only to the POD temporary directory:

```text
/tmp/xhd-modelnet40/ModelNet40.zip
```

It is not committed into the repository.

## Paper-Branch Workload Pair

From the Goal5176 paper-branch log index:

```text
category = ModelNet40
input1 = /local/storage/shared/HDDatasets/ModelNet40/glass_box/train/glass_box_0115.off
input2 = /local/storage/shared/HDDatasets/ModelNet40/glass_box/train/glass_box_0081.off
author logged point counts = [1107, 1200]
paper-branch HDResult = 0.22594279050827026
```

This is the smallest ModelNet40 pair in the paper-branch log index by total
point count among the inspected records.

## Extracted Public Raw OFF Files

Files extracted from the official archive:

```text
ModelNet40/glass_box/train/glass_box_0115.off
ModelNet40/glass_box/train/glass_box_0081.off
```

Observed public raw OFF metadata:

```text
glass_box_0115.off:
  vertex count = 1107
  face count = 960
  SHA256 = 6a6d23cb9619c32f0c6a17082b450452f13facade3a998ed676de948c53a1b5f

glass_box_0081.off:
  vertex count = 1200
  face count = 844
  SHA256 = d35c49cc061f73ec0211bd65c69177599a269300d1b915db1f9a36e523405048
```

The public raw OFF vertex counts exactly match the author paper-branch logged
point counts.

## Author Binary Probe

Command shape:

```text
hd_exec
  -input1 /tmp/xhd-modelnet40/extracted/ModelNet40/glass_box/train/glass_box_0115.off
  -input2 /tmp/xhd-modelnet40/extracted/ModelNet40/glass_box/train/glass_box_0081.off
  -n_dims 3
  -input_type off
  -variant rt
  -execution gpu
  -json ...
  -overwrite=true
  -check=false
```

Downloaded author output:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5218_modelnet40_glass_box_author_raw_off_probe_2026-07-09.json
```

Observed:

```text
author HDResult on public raw OFF = 1115.2059326171875
author Running.AvgTime = 5.169 ms
author input counts = [1107, 1200]
```

Comparison:

```text
paper-branch log HDResult       = 0.22594279050827026
public raw OFF author HDResult  = 1115.2059326171875
absolute difference             ~= 1114.9799898266792
```

## Interpretation

This probe rejects the simple hypothesis:

```text
public official ModelNet40 raw OFF files are byte/coordinate-equivalent to the
author paper input files for this pair.
```

Even though the point counts match exactly, the directed-Hausdorff value does
not. The likely cause is that the author paper inputs are normalized,
translated, scaled, or otherwise converted versions of the public OFF geometry,
or that the paper branch used a different prepared/processed copy.

The important result is not the precise cause; it is the boundary:

```text
point-count equality is not enough;
public raw ModelNet40 OFF is not currently a valid Level-C exact paper input.
```

## What This Proves

```text
The public ModelNet40 archive is reachable from the POD.
The selected paper-branch ModelNet40 filenames exist in the public archive.
The public raw OFF vertex counts match the author log counts.
Running author hd_exec on those raw OFF files does not reproduce the paper-log
HDResult.
```

## What This Does Not Prove

```text
full X-HD paper reproduction;
ModelNet40 exact paper input reproduction;
RTDL failure or success on ModelNet40;
the precise author preprocessing transform;
performance comparison.
```

## Claim Boundary

Allowed:

```text
Official public ModelNet40 raw OFF files are accessible and count-compatible
with at least one author paper-branch pair, but a direct author-binary probe on
raw OFF does not match the paper log. Therefore ModelNet40 still needs
preprocessing/provenance reconstruction before it can support Level-C exact
paper reproduction.
```

Not authorized:

```text
ModelNet40 exact inputs found;
ModelNet40 paper workload reproduced;
public raw OFF equals author input;
RTDL ModelNet40 correctness/performance claim.
```

## Next Recommendation

If continuing the ModelNet40 line, inspect author source and logs for the
preprocessing/normalization contract applied to OFF inputs. Do not run RTDL on
public raw OFF as a paper reproduction target until the transform is identified
and the author binary on transformed public input matches the paper log.
