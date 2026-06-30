#!/usr/bin/env bash
set -u

cd /workspace/rtdl_goal4806_fast_min

OUT=artifacts/section57_same_source_county_zipcode_output_after_skip_tiny_until_nontiny_preserve_bg
rm -rf "$OUT"
mkdir -p "$OUT"
echo "started $(date -Is) pid=$$" > "$OUT/status.txt"
trap 'echo "signal TERM $(date -Is)" > "$OUT/status.txt"; echo 143 > "$OUT/exit_code.txt"; exit 143' TERM
trap 'echo "signal HUP $(date -Is)" > "$OUT/status.txt"; echo 129 > "$OUT/exit_code.txt"; exit 129' HUP
trap 'echo "signal INT $(date -Is)" > "$OUT/status.txt"; echo 130 > "$OUT/exit_code.txt"; exit 130' INT

source /tmp/rtdl_goal4806_venv/bin/activate

PYTHONPATH=src RTDL_OPTIX_LIBRARY_PATH=/workspace/rtdl_goal4806_fast_min/build/librtdl_optix.so \
python scripts/rayjoin_paper_reproduction_suite.py run-rtdl \
  --dataset-root /workspace/rayjoin_section57_same_source_cdb \
  --case-id overlay_county_zipcode \
  --backend optix \
  --warmup 0 \
  --repeat 1 \
  --assemble-overlay-output \
  --overlay-output "$OUT/section57_overlay_county_zipcode_rtdl_after_skip_tiny_until_nontiny_preserve_bg.txt" \
  --input-provenance same_source_regenerated_cdb \
  --output-json "$OUT/section57_overlay_county_zipcode_rtdl_after_skip_tiny_until_nontiny_preserve_bg.json" \
  > "$OUT/run.stdout.txt" 2> "$OUT/run.stderr.txt"

code=$?
echo "$code" > "$OUT/exit_code.txt"
echo "finished $(date -Is) code=$code" > "$OUT/status.txt"
exit "$code"
