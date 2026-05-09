---

## Verdict

**ACCEPTED** — Goal1622 is accepted as latest-main reproducibility evidence for the v1.6.4 `COLLECT_K_BOUNDED` required-backend packet.

---

## Checked Evidence

| Item | Check | Detail |
|---|---|---|
| `accepted` flag | Pass | `true` in JSON |
| `status` | Pass | `accepted_packet_execution` |
| `environment_label` | Pass | `representative_rtx_a4500_latest_main_repro_packet` |
| `git_commit` | Pass | `6fde3868de2525414d9902afcbc9d24b64831113` (matches `git reset --hard origin/main` in report) |
| Required backends | Pass | `fake_native`, `embree`, `optix` — all present, none skipped |
| Goal1614 bounds stress subpackage | Pass | `accepted_local_bounds_stress`, 9 cases all `pass` across all 3 backends |
| Goal1615 reduced-copy benchmark subpackage | Pass | `accepted_reduced_copy_benchmark_evidence`, 9 records all `pass`, `input_materialization_count_delta: 3` on every case across all 3 backends |
| `failed_subpackages` | Pass | empty list `[]` |
| GPU identity | Pass | NVIDIA RTX A4500, driver 550.127.05, 20470 MiB — matches pod report |
| Test suite | Pass | All three test methods in `goal1622_..._test.py` cover acceptance flags, pod environment, and claim-flag falsity |
| Evidence ledger (Goal1621) | Pass | Marks `representative_rtx_collect_k_required_backend_performance_packet` as satisfied; Goal1622 extends this chain to latest-main |

---

## Blockers

None. All required backends passed. No failed subpackages. All prohibited claim flags are explicitly `false` in both the JSON artifact and the report narrative.

---

## Claim Boundary

The following are **not authorized** by this acceptance — confirmed `false` in every claim-flag field across the JSON top-level, both subpackages, and every individual record:

- **Public speedup wording** — not authorized (`public_speedup_wording_authorized: false`)
- **True zero-copy wording** — not authorized (`true_zero_copy_wording_authorized: false`)
- **Stable `COLLECT_K_BOUNDED` promotion** — blocked; requires a separate stable-promotion decision package and fresh 3-AI consensus (`stable_collect_k_promotion_authorized: false`)
- **Broad RTX/GPU wording** — not authorized (`broad_rtx_wording_authorized: false`)
- **Representative RTX performance evidence** — not authorized (`representative_rtx_performance_evidence_authorized: false`)
- **Release tags or release action** — not authorized (`release_action_authorized: false`)
- **Timing as performance evidence** — all timing fields are flagged `timing_recorded_for_diagnostics_only: true`

What is authorized: Goal1622 closes the latest-main reproducibility requirement for the v1.6.4 `COLLECT_K_BOUNDED` required-backend packet on an RTX A4500 pod at commit `6fde3868`.
