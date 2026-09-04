# Goal5843 v3 terminal archive-verifier failure

Date: 2026-09-04

Status:
`TERMINAL__V3_POST_DOWNLOAD_ARCHIVE_VERIFIER_MODE_NORMALIZATION_DEFECT__NO_RETRY`

## Immutable v3 execution record

Goal5843 v3 executed once from clean source commit
`ec4c9375833957f82149d165039aa3202dd791c6` on the owner-supplied pod reached
through `root@194.68.245.56:22160` with the project working key. The bound GPU
was NVIDIA RTX A6000
`GPU-f50facdf-7752-c71d-2c4a-c4df8c0155cc`, compute capability 8.6, driver
580.159.03.

The no-retry transaction reached `WORKER_ZERO` and all six pod stages returned
zero. It retained all 108 preregistered composites, 216 FIRST/STEADY subworker
receipts, and 7,020 registered execution timing samples. The independent pod
recount matched the controller. Those facts do not make v3 a completed
Goal5843 transaction because the required downloaded-archive verification
subsequently failed.

The complete v3 archive is preserved without modification as
`FORMAL_TRANSACTION_V3_TERMINAL_ARCHIVE_VERIFIER_FAILURE.tar.gz`, SHA-256
`bf24cc9954e9f6970ea58ff6584f79bf1de32b2e5118003a06723cb8ba61f118`.
The exact v3 preregistration is preserved as `PREREGISTRATION_V3.json`, file
SHA-256
`af04ea3df90b00e2639d24d9d2ec9bee30aa21f98b7cbda9183050191c2182eb`,
internal seal
`90c0e00f372df6fb9ba2985c80b43fe17b3ad00be60471f8f67d398ba1dc6b9a`.
No v3 row may be pooled into a successor transaction or used for a public or
manuscript claim.

## Failure

The pinned command
`scripts/goal5843_verify_downloaded_archive.py` safely extracted the downloaded
archive and then stopped with:

```text
RuntimeError: bound-artifact bytes differ: execution_paths.native_library
```

The failure occurred before any key export, local recount, or archive
verification receipt was written. The formal pod transaction was not retried,
deleted, edited, or reclassified.

## Root cause

The native DSO bytes did not differ. All four relevant identities were exactly
`ad8dc4e4eff214274493d1bc891a192f5105df1b34f6f01fbbd177baaef6b4d1`:

- the execution authority's bound native-library SHA-256;
- the custody receipt's native-library SHA-256;
- the pod's live and preserved DSO SHA-256;
- the downloaded tar member and safely extracted file SHA-256.

The mismatch was only file mode. The pod source and tar header recorded
`0777`. Python's security-preserving `tarfile.extractall(filter="data")`
correctly normalized that regular executable to `0755`. The verifier then
incorrectly compared the normalized extracted mode against the original
custody mode. Non-executable pod files similarly normalize from `0666` to
`0644`, so the check was incompatible with the verifier's own safe-extraction
policy.

## Successor repair

The v4 repair keeps safe extraction and all byte, path, type, seal, authority,
and recount checks. It verifies the original custody mode against the tar
member header, while verifying size and SHA-256 against the safely extracted
file. A regression test proves that an original `0777` tar member may safely
extract as `0755`, while a tar-header mode substitution is rejected.

The repair changes no task, input, output, arm, schedule, sample count,
estimand, performance threshold, runtime, provider, native engine, or frozen
Goal5838 core byte. Because it occurs after v3 `WORKER_ZERO`, the existing
failure policy requires a new preregistration and a completely new formal
transaction. v3 remains terminal evidence rather than a retry source.
