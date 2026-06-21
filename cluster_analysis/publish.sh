#!/usr/bin/env bash
# يبني الخريطة وينشرها على فرع main داخل clusters/ ليتحدّث الرابط:
#   https://saff2026.github.io/khitba/clusters/
set -e
cd /home/user/khitba
python3 cluster_analysis/build_full_map.py >/dev/null
cp cluster_analysis/governorates_map.html cluster_analysis/index.html
cp cluster_analysis/governorates_map.html docs/index.html
cp cluster_analysis/governorates_map.html /tmp/_pub_map.html
DEV=$(git rev-parse --abbrev-ref HEAD)
git add -A && git commit -q -m "Update map build" || true
git push -u origin "$DEV" >/dev/null 2>&1 || true
git fetch origin main >/dev/null 2>&1
git checkout main >/dev/null 2>&1
git pull origin main >/dev/null 2>&1 || true
mkdir -p clusters
cp /tmp/_pub_map.html clusters/index.html
git add clusters/index.html
git commit -q -m "Update published clusters map" || true
git push origin main >/dev/null 2>&1
git checkout "$DEV" >/dev/null 2>&1
echo "نُشر على https://saff2026.github.io/khitba/clusters/"
