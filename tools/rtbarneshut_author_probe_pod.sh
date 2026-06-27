#!/usr/bin/env bash
set -u

OUT="${OUT:-/root/rtbarneshut_author_probe_20260626}"
SRC="${SRC:-/root/external/RT-BarnesHut-author}"
REPO="${REPO:-https://github.com/vani-nag/OWLRayTracing.git}"
BRANCH="${BRANCH:-BarnesHutRT}"
OPTIX_ROOT="${OPTIX_ROOT:-/root/vendor/optix-dev}"

mkdir -p "$OUT" "$(dirname "$SRC")"
exec > >(tee -a "$OUT/probe.log") 2>&1

echo "=== RT-BarnesHut author probe ==="
date -Is
hostname
echo "OUT=$OUT"
echo "SRC=$SRC"
echo "REPO=$REPO"
echo "BRANCH=$BRANCH"
echo "OPTIX_ROOT=$OPTIX_ROOT"

echo "=== GPU / toolchain ==="
nvidia-smi || true
cmake --version || true
which git || true
git --version || true
which nvcc || true
ls -l /usr/local/cuda*/bin/nvcc /usr/bin/nvcc 2>/dev/null || true
find / -path '*/bin/nvcc' -type f 2>/dev/null | head -20 || true
which gcc || true
gcc --version | head -5 || true
which g++ || true
g++ --version | head -5 || true
find "$OPTIX_ROOT" -maxdepth 3 -type f \( -name 'optix.h' -o -name 'optix_stubs.h' \) -print 2>/dev/null || true

echo "=== source checkout ==="
if [ ! -d "$SRC/.git" ]; then
  git clone --branch "$BRANCH" --depth 1 "$REPO" "$SRC"
else
  git -C "$SRC" status --short || true
fi
cd "$SRC" || exit 2
git rev-parse HEAD || true
git branch --show-current || true
git log --oneline -1 || true

echo "=== CMake configure ==="
rm -rf build
cmake -S . -B build \
  -DOptiX_ROOT_DIR="$OPTIX_ROOT" \
  -DOptiX_INCLUDE="$OPTIX_ROOT/include" \
  -DOWL_BUILD_SAMPLES=ON \
  -DOWL_BUILD_ADVANCED_TESTS=OFF
CONFIG_RC=$?
echo "CONFIG_RC=$CONFIG_RC"

echo "=== CMake build rtbarneshut ==="
BUILD_RC=999
if [ "$CONFIG_RC" -eq 0 ]; then
  cmake --build build --target rtbarneshut -j"$(nproc)"
  BUILD_RC=$?
fi
echo "BUILD_RC=$BUILD_RC"

echo "=== sanity run if executable and dataset exist ==="
RUN_RC=999
if [ "$BUILD_RC" -eq 0 ] && [ -x build/rtbarneshut ]; then
  if [ -f treelogy_synthetic_1M.txt ]; then
    ./run_script.sh sanitycheck 1
    RUN_RC=$?
  else
    echo "SANITY_DATASET_MISSING=treelogy_synthetic_1M.txt"
  fi
fi
echo "RUN_RC=$RUN_RC"

python3 - <<'PY' "$OUT" "$CONFIG_RC" "$BUILD_RC" "$RUN_RC"
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
payload = {
    "config_rc": int(sys.argv[2]),
    "build_rc": int(sys.argv[3]),
    "run_rc": int(sys.argv[4]),
    "probe_log": str(out / "probe.log"),
}
(out / "status.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

echo "=== status ==="
cat "$OUT/status.json" || true
