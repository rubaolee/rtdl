#!/usr/bin/env bash
set -uo pipefail

ROOT=/tmp/rtdl-v4-affinity-02e84374f
PY=/workspace/rtdl-v4-paper-apps-run/venv/bin/python
BASE=/workspace/rtdl-v4-long-perf-successor-02e84374f-affinity/FORMAL_CONFIG_02E84374F_A4500_CPU8_V2.json
OUT=/workspace/rtdl-v4-long-perf-successor-02e84374f-affinity/CPU_SENSITIVITY_V1
export CUDA_VISIBLE_DEVICES=0

if [[ -e "$OUT" ]]; then
    printf 'refusing to overwrite %s\n' "$OUT" >&2
    exit 2
fi

mkdir -p "$OUT"/{configs,workers,journals,stdout,stderr,launches}
date --iso-8601=ns > "$OUT/STARTED_AT.txt"
sha256sum "$BASE" > "$OUT/BASE_CONFIG.sha256"
git -C "$ROOT" rev-parse HEAD > "$OUT/SOURCE_COMMIT.txt"
git -C "$ROOT" rev-parse HEAD^{tree} > "$OUT/SOURCE_TREE.txt"
git -C "$ROOT" status --porcelain=v1 > "$OUT/SOURCE_STATUS.txt"
grep -E 'Cpus_allowed_list|Mems_allowed_list' /proc/self/status > "$OUT/CPUSET_PRE.txt"
lscpu > "$OUT/LSCPU.txt"
lscpu -e=CPU,CORE,SOCKET,NODE,ONLINE > "$OUT/CPU_TOPOLOGY.txt"
nvidia-smi -q > "$OUT/NVIDIA_SMI_PRE.txt"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader \
    > "$OUT/GPU_PROCESSES_PRE.txt" 2>&1 || true
for path in /sys/fs/cgroup/cpu/cpu.cfs_quota_us \
            /sys/fs/cgroup/cpu/cpu.cfs_period_us \
            /sys/fs/cgroup/cpuset/cpuset.cpus; do
    if [[ -r "$path" ]]; then
        printf '%s=' "$path" >> "$OUT/CGROUP_PRE.txt"
        cat "$path" >> "$OUT/CGROUP_PRE.txt"
    fi
done

"$PY" - "$BASE" "$OUT" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

base_path = Path(sys.argv[1])
out = Path(sys.argv[2])
base = json.loads(base_path.read_text(encoding="utf-8"))
configs = {}
for cpu in range(48):
    config = json.loads(json.dumps(base))
    config["common"]["cpu_affinity"] = {"cpu_ids": [cpu]}
    path = out / "configs" / f"CONFIG_CPU_{cpu:02d}.json"
    payload = json.dumps(config, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")
    configs[str(cpu)] = {
        "relative_path": path.relative_to(out).as_posix(),
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }

units = (
    ("particle_tracking", 32),
    ("librts__parks__range_contains", 4),
)
orders = (("new_v4", "pyoptix"), ("pyoptix", "new_v4"))
rows = []
for cpu in range(48):
    for unit, repetitions in units:
        for block, order in enumerate(orders):
            for position, arm in enumerate(order):
                rows.append({
                    "ordinal": len(rows),
                    "cpu": cpu,
                    "unit": unit,
                    "endpoint": "prepared",
                    "block": block,
                    "position": position,
                    "arm": arm,
                    "repetitions": repetitions,
                    "warmups": 1,
                    "timeout_seconds": 900,
                    "config_relative": configs[str(cpu)]["relative_path"],
                    "config_sha256": configs[str(cpu)]["sha256"],
                })

schedule = {
    "schema": "rtdl.v4_long_workload.cpu_sensitivity.schedule.v1",
    "formal_evidence": False,
    "pooling_into_formal_transaction_forbidden": True,
    "preregistered_plan_commit": "c54bce034",
    "base_config_sha256": hashlib.sha256(base_path.read_bytes()).hexdigest(),
    "worker_count": len(rows),
    "retry_allowed": False,
    "discard_allowed": False,
    "rows": rows,
}
schedule_path = out / "SCHEDULE.json"
schedule_payload = json.dumps(schedule, indent=2, sort_keys=True) + "\n"
schedule_path.write_text(schedule_payload, encoding="utf-8")
(out / "SCHEDULE.sha256").write_text(
    hashlib.sha256(schedule_payload.encode()).hexdigest() + "  SCHEDULE.json\n",
    encoding="utf-8",
)
with (out / "SCHEDULE.tsv").open("w", encoding="utf-8") as stream:
    for row in rows:
        stream.write("\t".join(str(row[key]) for key in (
            "ordinal", "cpu", "unit", "block", "position", "arm",
            "repetitions", "warmups", "timeout_seconds", "config_relative",
        )) + "\n")
PY

sha256sum "$OUT"/configs/*.json > "$OUT/CONFIGS.sha256"
sha256sum "$OUT/SCHEDULE.tsv" > "$OUT/SCHEDULE_TSV.sha256"
printf 'ordinal\tcpu\tunit\tblock\tposition\tarm\treturn_code\toutput_sha256\tjournal_sha256\tstdout_sha256\tstderr_sha256\n' \
    > "$OUT/CONTROLLER_PROGRESS.tsv"

while IFS=$'\t' read -r ordinal cpu unit block position arm repetitions warmups timeout_seconds config_relative; do
    stem=$(printf 'w%03d__cpu%02d__%s__b%d__p%d__%s' \
        "$ordinal" "$cpu" "$unit" "$block" "$position" "$arm")
    config="$OUT/$config_relative"
    output="$OUT/workers/$stem.json"
    journal="$OUT/journals/$stem.jsonl"
    stdout="$OUT/stdout/$stem.bin"
    stderr="$OUT/stderr/$stem.bin"
    launch="$OUT/launches/$stem.json"
    started_ns=$(date +%s%N)
    set +e
    timeout --signal=TERM --kill-after=5s "${timeout_seconds}s" \
        "$PY" "$ROOT/scripts/v4_long_workload_worker.py" \
        --config "$config" --unit "$unit" --arm "$arm" \
        --endpoint prepared --repetitions "$repetitions" --warmups "$warmups" \
        --output "$output" --journal "$journal" >"$stdout" 2>"$stderr"
    return_code=$?
    set -e
    ended_ns=$(date +%s%N)
    output_sha=$(test -f "$output" && sha256sum "$output" | awk '{print $1}' || printf 'MISSING')
    journal_sha=$(test -f "$journal" && sha256sum "$journal" | awk '{print $1}' || printf 'MISSING')
    stdout_sha=$(sha256sum "$stdout" | awk '{print $1}')
    stderr_sha=$(sha256sum "$stderr" | awk '{print $1}')
    "$PY" - "$launch" "$ordinal" "$cpu" "$unit" "$block" "$position" "$arm" \
        "$return_code" "$started_ns" "$ended_ns" "$output_sha" "$journal_sha" \
        "$stdout_sha" "$stderr_sha" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
keys = (
    "ordinal", "cpu", "unit", "block", "position", "arm", "return_code",
    "started_epoch_ns", "ended_epoch_ns", "output_sha256", "journal_sha256",
    "stdout_sha256", "stderr_sha256",
)
raw = sys.argv[2:]
value = dict(zip(keys, raw, strict=True))
for key in ("ordinal", "cpu", "block", "position", "return_code",
            "started_epoch_ns", "ended_epoch_ns"):
    value[key] = int(value[key])
value["wall_ns"] = value["ended_epoch_ns"] - value["started_epoch_ns"]
value["timeout"] = value["return_code"] in (124, 137)
value["schema"] = "rtdl.v4_long_workload.cpu_sensitivity.launch.v1"
with path.open("x", encoding="utf-8") as stream:
    json.dump(value, stream, indent=2, sort_keys=True)
    stream.write("\n")
PY
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$ordinal" "$cpu" "$unit" "$block" "$position" "$arm" \
        "$return_code" "$output_sha" "$journal_sha" "$stdout_sha" "$stderr_sha" \
        >> "$OUT/CONTROLLER_PROGRESS.tsv"
    printf '%s\n' "$ordinal" > "$OUT/LAST_COMPLETED_ORDINAL.txt"
done < "$OUT/SCHEDULE.tsv"

grep -E 'Cpus_allowed_list|Mems_allowed_list' /proc/self/status > "$OUT/CPUSET_POST.txt"
nvidia-smi -q > "$OUT/NVIDIA_SMI_POST.txt"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader \
    > "$OUT/GPU_PROCESSES_POST.txt" 2>&1 || true
date --iso-8601=ns > "$OUT/COMPLETED_AT.txt"
sha256sum "$OUT"/workers/*.json > "$OUT/WORKERS.sha256"
sha256sum "$OUT"/journals/*.jsonl > "$OUT/JOURNALS.sha256"
sha256sum "$OUT"/stdout/*.bin > "$OUT/STDOUT.sha256"
sha256sum "$OUT"/stderr/*.bin > "$OUT/STDERR.sha256"
sha256sum "$OUT"/launches/*.json > "$OUT/LAUNCHES.sha256"
printf 'PASS__RAW_POPULATION_COMPLETE\n' > "$OUT/RAW_COMPLETE.txt"
