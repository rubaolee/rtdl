# Goal5473: LibRTS Exact Dataset Acquisition Decision

Date: 2026-07-11

Status:

```text
completed_exact_dataset_access_probe__defer_download_to_suitable_host__review_pending
```

## Result

The exact-data blocker is now a quantified resource decision rather than a
vague missing-file statement.

Official sources:

```text
three SharePoint archive links: direct HEAD/download resolution currently ends at HTTP 401
Zenodo record: 14209767
Zenodo file: PPoPPAE-v2.tar.gz
size: 23,062,425,365 bytes
MD5: 89e589f086038f1cd3af9e3ed67da8c8
Zenodo availability: confirmed
```

The SharePoint result does not prove permanent unavailability. The author
download script uses `onedrivedownloader==1.1.3`, but that package simply rewrites
the links to `?download=1`; the resulting location currently requires
authorization. Zenodo remains the authoritative available fallback.

## Current Linux Host

```text
GPU: NVIDIA GeForce GTX 1070
VRAM: 8,192 MiB
RAM: 16,714,764,288 bytes (~15.6 GiB)
free disk: 112,937,418,752 bytes (~105 GiB)
Zenodo 10-second transfer probe: 529,369 bytes/sec
estimated complete download: 43,566 sec (~12.10 hours)
```

The host has enough space for two compressed archive sizes, but extraction size
is unknown. More importantly, it has one third of the paper-recommended RAM and
one third of the recommended VRAM. Spending about 12 hours downloading the
archive to a host that cannot run the full paper matrix is rejected.

## Required Exact-Execution Host

```text
Linux
RTX 3090-class or newer RTX GPU with RT cores
>= 24 GiB VRAM
>= 64 GiB RAM
>= 70 GiB free disk before acquisition
recommended sustained Zenodo download >= 10 MiB/sec
```

At 10 MiB/sec the compressed archive takes about 37 minutes rather than 12.1
hours. The download must be resume-safe, MD5-verified, and followed by a disk
capacity check before extraction.

## Decision

Do not download on `192.168.1.20`. Preserve it for bounded functional evidence.
The next exact-data execution requires a suitable POD or equivalent host.

POD is not required for more metadata/log work, but it is now required before
the exact dataset blocker can be removed and before full figure execution.

## Claim Boundary

Not claimed:

- exact inputs acquired;
- SharePoint permanently unavailable;
- any paper figure reproduced;
- performance ratio authorized;
- GTX 1070 as paper-comparable hardware;
- Embree relevance.
