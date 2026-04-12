# KITTI Linux Manual Download Handoff

Linux host:

- `lestat-lx1`

Canonical KITTI staging path:

- `/home/lestat/data/kitti_raw`

Official raw-data source:

- [KITTI raw data](https://www.cvlibs.net/datasets/kitti/raw_data.php)

Important boundary:

- the KITTI site requires manual login to download the raw dataset
- RTDL is prepared to use the data once it is present, but it cannot bypass the
  official login/download gate

Recommended operator steps on Linux:

```bash
ssh lestat-lx1
mkdir -p /home/lestat/data/kitti_raw
```

Download the desired KITTI raw-data archives through the official logged-in
site and unpack them under:

- `/home/lestat/data/kitti_raw`

Expected content for RTDL readiness:

- one or more sequence directories containing `velodyne/*.bin`

Verification command:

```bash
cd /home/lestat/work/rtdl_v05_live
PYTHONPATH=src:. python3 scripts/goal277_kitti_linux_ready.py \
  /home/lestat/data/kitti_raw \
  --write-json build/goal277_kitti_linux_ready_report.json
cat build/goal277_kitti_linux_ready_report.json
```

Ready condition:

- `current_status` is `ready`
- `velodyne_bin_count > 0`
