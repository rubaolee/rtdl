# V3 Functional RC and Installation

## Frozen qualification identity

The final clean qualification used these exact identities:

| Item | SHA-256 |
| --- | --- |
| Portable artifact v6 | `a570367ebdc3b2ac3544d3e36046017acb6e9a854a2b25b10145461978fa28db` |
| Base source archive | `3a9785a9...f019` |
| Fresh execution source | `3d3fda2dfe5e547a966fc170ae5216dc8265f48254023b9cdfd6b0b69c88f685` |
| Fresh source tree | `52338200c1079473293941ff2a953cd0e482e684c1b3bd23d8912ba6dfce3526` |
| Fresh target native | `5829b59028203e9a5defd7bcd99e5b26a62162b60558b33651ee8254c2b3158c` |
| Evidence archive | `2454845b018f43618e5093991d1b72a7403e1978a6b231755d02f1b6f9f44ea2` |

The artifact carries no private `.codex` dependency and no prebuilt target
native.  The validator builds a fresh native and freezes that exact binary with
the regenerated proof evidence and materialized source.  Native builds are not
claimed byte-reproducible across toolchains.

## Linux validation path

The portable artifact is a controlled validation package, not a PyPI wheel.
On a supported Linux host with NVIDIA driver, CUDA toolkit, OptiX SDK, compiler,
and Python dependencies:

```bash
sha256sum goal5747_v3_nine_app_portable_artifact_v6_20260809.tar.gz
mkdir v3-rc && tar -xzf goal5747_v3_nine_app_portable_artifact_v6_20260809.tar.gz -C v3-rc
cd v3-rc
python3 goal5747_portable_release_validate.py --help
```

Read the artifact's own `README.md` and use the validator's current command-line
contract.  Do not guess flags from an older bundle.  The validator performs
create-only extraction, source and dependency checks, target rematerialization,
native build, proof regeneration, nine-app functional execution, and an
independent recount before it emits activation metadata.

After success, source the emitted `ACTIVATE_V3.sh` in the validated output
directory, then verify:

```bash
source /absolute/path/to/ACTIVATE_V3.sh
python3 -c 'import rtdsl; print(rtdsl.__file__)'
```

## Supported claim

This process establishes a usable functional release candidate on the tested
Linux configuration.  It does not establish a universal installation promise,
modern-RTX performance, production-GA, or a public binary distribution.
