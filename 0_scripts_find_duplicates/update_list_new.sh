find "/Volumes/behavgenom_archive$/thecus/Laura-phase2" -type f | \
grep -E "\.(avi|info\.xml|log\.csv)$" | \
grep -v _seg\.avi > single_worm_new.txt