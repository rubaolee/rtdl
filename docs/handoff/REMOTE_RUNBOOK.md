# Remote Runbook

Host:
- alias: `lestat-lx1`
- target: `lestat@192.168.1.20`

Expected Linux workspace:
- repo: `/home/lestat/work/rtdl_python_only`
- temporary performance workspace used earlier:
  - `/home/lestat/work/rtdl_goal69_run`

Recommended first checks:
```bash
ssh lestat-lx1 'echo OK && uptime && free -h'
ssh lestat-lx1 'ps aux | grep goal69 | grep -v grep'
```

Sync repo:
```bash
rsync -av --delete /Users/rl2025/rtdl_python_only/ lestat-lx1:/home/lestat/work/rtdl_python_only/
```

Remote build:
```bash
ssh lestat-lx1 'cd /home/lestat/work/rtdl_python_only && make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev'
```

Focused local validation before remote run:
```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_py_test tests.goal69_pip_positive_hit_performance_test
```

Remote Goal 69 narrow OptiX run:
```bash
ssh lestat-lx1 '
  cd /home/lestat/work/rtdl_python_only &&
  mkdir -p build/goal69_county_zipcode_optix &&
  PYTHONPATH=src:. \
  RTDL_OPTIX_PTX_COMPILER=nvcc \
  RTDL_NVCC=/usr/bin/nvcc \
  python3 scripts/goal69_pip_positive_hit_performance.py \
    --cases county_zipcode \
    --backends optix \
    --output-dir build/goal69_county_zipcode_optix
'
```

Expected output artifacts:
- `/home/lestat/work/rtdl_python_only/build/goal69_county_zipcode_optix/goal69_summary.json`
- `/home/lestat/work/rtdl_python_only/build/goal69_county_zipcode_optix/goal69_summary.md`

If OptiX run succeeds, next Embree run:
```bash
ssh lestat-lx1 '
  cd /home/lestat/work/rtdl_python_only &&
  mkdir -p build/goal69_county_zipcode_embree &&
  PYTHONPATH=src:. \
  python3 scripts/goal69_pip_positive_hit_performance.py \
    --cases county_zipcode \
    --backends embree \
    --output-dir build/goal69_county_zipcode_embree
'
```

Key local docs to update after results:
- `/Users/rl2025/rtdl_python_only/docs/reports/goal69_pip_performance_status_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/...gemini-review...`

If SSH is failing:
- verify whether the host is actually reachable from another terminal
- if not reachable, fix host/network first
- do not fabricate a performance result without the Linux run
