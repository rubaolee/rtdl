#!/usr/bin/env bash
set -u

output_root=/tmp/particle-rtdlexe-37e-prepared-3block
source_root=/tmp/rtdl-v4-long-recount-bf7550f82
python=/workspace/rtdl-v4-paper-apps-run/venv/bin/python
config=/tmp/CONFIG_PARTICLE_RTDLEXE_37E730831_DIAGNOSTIC.json

if [[ -e "$output_root" ]]; then
    echo "diagnostic output already exists: $output_root" >&2
    exit 91
fi
mkdir -p "$output_root"
cd "$source_root" || exit 92

run_one() {
    local block=$1
    local position=$2
    local arm=$3
    local output="$output_root/b${block}_p${position}_${arm}.json"
    local journal="$output_root/b${block}_p${position}_${arm}.jsonl"
    CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src:. "$python" \
        scripts/v4_long_workload_worker.py \
        --config "$config" \
        --unit particle_tracking \
        --arm "$arm" \
        --endpoint prepared \
        --repetitions 32 \
        --warmups 1 \
        --output "$output" \
        --journal "$journal"
    local status=$?
    printf 'block=%s position=%s arm=%s rc=%s\n' \
        "$block" "$position" "$arm" "$status"
}

run_one 0 0 new_v4
run_one 0 1 pyoptix
run_one 1 0 pyoptix
run_one 1 1 new_v4
run_one 2 0 new_v4
run_one 2 1 pyoptix

for output in "$output_root"/*.json; do
    jq -r \
        '[input_filename,.status,.arm,.primary_median_ns,.output_sha256,.retained_sample_count,.retry_count,.discard_count]|@tsv' \
        "$output"
done
