# Goal2621 Contact-Manifold COLLECT_K_BOUNDED OptiX Pod Evidence

Date: 2026-05-25

## Scope

This evidence validates the bounded collision witness/contact-manifold candidate app against the generic app-name-free COLLECT_K_BOUNDED i64 row collector on OptiX. It does not add or claim native collision/contact engine logic.

## Environment

- SSH requested: `ssh root@69.30.85.198 -p 22148 -i ~/.ssh/id_ed25519`
- SSH key actually used on this Mac: `~/.ssh/id_ed25519_rtdl_codex`
- Repo on pod: `/root/rtdl_goal2621`
- Source commit: `8347f7eed1f96c986e72f7fcfb04f2f7a19308a5`
- Source state: transferred local Goal2621 uncommitted candidate files over the cloned commit; see git status in JSON evidence.
- GPU: `NVIDIA RTX A5000, driver 570.211.01, 24564 MiB`
- OptiX headers: `/root/vendor/optix-dev-9.0.0/include/optix.h`
- CUDA prefix: `/usr/local/cuda-12.8`

## Results

| Check | Result | Key Evidence |
| --- | --- | --- |
| OptiX backend build | PASS | `make build-optix OPTIX_PREFIX=/root/vendor/optix-dev-9.0.0 CUDA_PREFIX=/usr/local/cuda-12.8` rc=0 |
| Tiny OptiX parity | PASS | valid_count=3, matches_cpu_reference=True, native_collect_elapsed_sec=0.0005520973354578018 |
| Grid-512 OptiX parity | PASS | valid_count=512, cpu_reference_elapsed_sec=9.091012405231595, native_collect_elapsed_sec=0.00221424363553524 |
| Tiny fail-closed overflow | PASS | rc=1; message includes fail_closed_overflow and partial_result_returned=False |
| Standalone C++ grid-512 baseline | PASS | elapsed_sec=0.0232454, valid_count=512 |
| Candidate unit test | PASS | rc=0; unittest output is preserved in JSON evidence |

## Interpretation

- The OptiX native collector is ABI-visible and works for the app row schema through the generic `rtdl_optix_collect_k_bounded_i64` symbol.
- Overflow is fail-closed: the undersized capacity run exits non-zero and does not return partial witness rows.
- This is candidate promotion evidence, not yet a stable primitive promotion by itself; final promotion still requires explicit consensus update if we decide to claim `COLLECT_K_BOUNDED` as stable.
