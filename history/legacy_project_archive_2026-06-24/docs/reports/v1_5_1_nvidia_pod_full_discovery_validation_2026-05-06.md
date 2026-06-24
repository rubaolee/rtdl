# v1.5.1 NVIDIA Pod Full Discovery Validation

Date: 2026-05-06

## Verdict

Current `origin/main` passed full Linux/NVIDIA pod unittest discovery at commit `7c28beb37c52dff4aa014b93521611a4fc5b9954`.

This is validation evidence only. It does not publish v1.5.1, authorize public speedup wording, authorize broad RTX/GPU acceleration claims, or change the v1.5 release tag.

## Environment

- Pod SSH target: `root@213.173.102.217`, port `25443`
- SSH key used from Windows/WSL: `~/.ssh/id_ed25519_rtdl_codex`
- Pod checkout: `/root/work/rtdl_v1_5_1_pod`
- GPU: NVIDIA RTX A4500
- Driver: `550.127.05`
- GPU memory: `20470 MiB`
- OptiX runtime library: `/root/work/rtdl_v1_5_1_pod/build/librtdl_optix.so`

## Fixes Validated

- Commit `043b1ba8` hardened the smooth-camera visual demo cache key so stale frame metadata cannot be reused across backend, compare-backend, resolution, mesh, or theme changes.
- Commit `7c28beb3` aligned historical pod artifact gate tests with tracked repository evidence. Missing untracked historical logs or local-only archive files now remain explicit blockers instead of being treated as portable clean-checkout requirements.

## Commands

```bash
cd /root/work/rtdl_v1_5_1_pod
git fetch origin
git reset --hard origin/main
export RTDL_OPTIX_LIB=/root/work/rtdl_v1_5_1_pod/build/librtdl_optix.so
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'
```

Windows focused cross-check:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.report_smoke_test tests.goal179_smooth_camera_linux_backend_test tests.goal1136_changed_path_rtx_pod_artifact_intake_test tests.goal1168_goal1166_live_pod_intake_audit_test tests.goal1259_v1_1_pre_pod_gate_test
```

Linux host focused cross-check:

```bash
cd /home/lestat/work/rtdl_v1_5_linux_check
git fetch origin
git reset --hard origin/main
PYTHONPATH=src:. python3 -m unittest tests.goal1136_changed_path_rtx_pod_artifact_intake_test tests.goal1168_goal1166_live_pod_intake_audit_test tests.goal1259_v1_1_pre_pod_gate_test tests.goal179_smooth_camera_linux_backend_test tests.report_smoke_test
```

## Results

- NVIDIA pod full discovery: `Ran 2743 tests in 309.133s`, `OK (skipped=221)`.
- Linux host focused cross-check: `Ran 18 tests in 35.591s`, `OK (skipped=4)`.
- Windows focused cross-check: `Ran 18 tests in 74.271s`, `OK (skipped=4)`.
- Windows full discovery was attempted with a 10-minute timeout and did not complete within that timeout, so this report does not claim full Windows discovery green.

## Boundary

The passing pod discovery establishes that the current tracked tree is clean under the available Linux/NVIDIA runtime and that the previous Goal179 OptiX smoke mismatch was stale cache metadata rather than an OptiX parity failure. Historical artifact gates remain non-claim-grade when their old untracked logs or local-only archives are absent from a clean checkout.
