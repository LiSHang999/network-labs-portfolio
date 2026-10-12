#!/bin/bash
{
echo "=== hostname: $(hostname) ==="
echo "=== lsblk ==="
lsblk
echo "=== tools present? ==="
for c in mdadm pvcreate vgcreate lvcreate mkfs.xfs; do
  if command -v $c >/dev/null 2>&1; then echo "$c OK"; else echo "$c MISSING"; fi
done
echo "=== yum repolist ==="
yum repolist 2>&1 | head -20
echo "=== /mnt mount ==="
mount | grep -E '/mnt|sr0|cdrom' || echo "(no /mnt/cdrom mount)"
ls /mnt 2>&1 | head
echo "=== lsblk disk list (nvme) ==="
ls -l /dev/nvme* 2>&1
} > /root/storage-check.txt 2>&1
