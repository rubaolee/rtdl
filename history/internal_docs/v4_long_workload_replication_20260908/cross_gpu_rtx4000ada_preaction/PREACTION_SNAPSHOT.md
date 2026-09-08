# RTX 4000 Ada cross-GPU replication preaction snapshot

Date: 2026-09-08 America/New_York.

Status: `FROZEN_BEFORE_REPLICATION_WORKER_ZERO`.

This directory freezes the complete dry-run and the inputs needed to authorize
one separately identified cross-GPU reproducibility transaction. It is not a
same-host temporal replay, is not pooled with the prior RTX A4500 result, and
contains no formal performance result.

## Registered identities

- Harness/control commit:
  `beb4b1e735b4b081ede394a9fb42eb2c8b264bea`.
- Measured successor commit:
  `02e84374fc092d2bb916cca633eda9592b4ecf07`; tree
  `8aad15d686bbc9e1c3b11df998898a0a063a01f1`.
- GPU: NVIDIA RTX 4000 Ada Generation, UUID
  `GPU-2a00572b-6cef-b9e6-db0a-c127783a5d46`, driver `550.127.05`,
  compute capability `8.9`.
- CPU affinity: exact logical CPU set `{8}` for every worker.
- Input: official cit-Patents RT-2A1 binary, SHA-256
  `c5b2c9203eeabb46414965755c33befdb1810e71cb51155eb940a68a6179d855`.
- Expected checked U64 output: `7,515,023`; output SHA-256
  `f3a9d76129db60b207374aef74b6d5abb6a126a6d4fc7bc88b830a7fc1995e2c`.

## Bound artifacts

| Artifact | SHA-256 |
| --- | --- |
| Formal config | `d9df1b75cb39139f0b580f91319447b9eca24bd27031bd02d125f1ddcc199643` |
| Dry-run summary | `26802297b75f119db412f8794892e2cb1506446269f4a3fbfdf09ef96c8ce223` |
| Preregistration | `feb8a8eeb6df43ac679a49b119428d78f7d00cea681e0ac0ba17646eaeff6509` |
| One-input data manifest | `db3affa051b24642a386f7f16c3590126d2e895d966e386fbecbaa0587185cae` |
| Base config | `c800c40b1d6c5583d55c2a44651db6df7293901d82cbef7c259681b71a1a63f4` |
| PyOptiX build-receipt file | `b6db0ed5c830e101d0641c5e16f69ae74d1b9298c135e8ff00eb42de9bb9679f` |
| Prebuilt-PTX manifest | `85887fd35c644258353543baedf9b423030e3d627b96e7d2bf183590222eed7f` |
| Native build manifest | `fb5be39eb016bfe0d55b5d6956da7dad05d72354e3cfdcbb08ce03f58a0ea154` |
| Triangle `.rtdlexe` build manifest | `30aa28e0b73d207cca8d28d5f630b8eeb4944d76eb40b61d0fd145942fc5ec81` |
| Transfer snapshot archive | `37155a90767d67f9e88fadedf7d47ba8a1dd2525f2297b35806c1b7ae14145a8` |

The PyOptiX receipt's internal canonical digest is
`00126d0e04250dcdb137e4deb14bec988bc420eb9e0d30aef0cf7c9ab3ff7994`;
the loaded extension SHA-256 is
`0a05db8ccb565ec513a391809bd8b539ccefdd25bd7b75a573ffc7bc5ad55933`.
The fresh RTDL native library SHA-256 is
`94d9e42be75c86c3186dac1d2a280873206698ea620f5666b83e4d49ce00686d`.
The signed triangle `.rtdlexe` SHA-256 is
`596642ec516415197677685ae660362e86d9ba6001a888ac8fab4afa1700d1ed`.

## Dry-run result

Both fresh workers passed with zero retry, discard, or timeout. Their input
identities and output hashes were identical. The one-sample diagnostic times
were 10.068177610 s for RTDL and 9.056743928 s for public PyOptiX, a ratio of
`1.111677407470143x`. This observation is a dry-run gate only; it is not the
registered eight-block estimate and cannot authorize a performance claim.

The local copy of the control code independently accepted the copied config,
dry summary, and preregistration through
`_validate_formal_authority`. Ordinary and optimized Python each passed 24/24
combined long-workload control tests on both the Mac and the Pod.

## Setup diagnostics

No formal worker ran during setup. A first virtual environment installation to
the network-backed `/workspace` mount was stopped after sustained filesystem
wait and replaced by a local `/tmp` environment. Two subsequent PyOptiX build
attempts failed before compilation because the local clone's `origin` URL did
not match the pinned public repository and because the virtual-environment
`ninja` directory was not on `PATH`. Both conditions were corrected without
changing source bytes. A display-only `jq` invocation and a one-line Python
probe also failed due to shell quoting after their preceding create-only
operations had succeeded; neither was an experiment worker.

## Formal authorization boundary

The only authorized next action is one execution of the frozen 16-worker
formal schedule using the exact remote paths and hashes in the committed
config. Any source, input, machine, RTDL executable, native library, PyOptiX
extension, schedule, threshold, affinity, retry/discard policy, or tool-byte
change invalidates this preregistration and requires a new transaction.
