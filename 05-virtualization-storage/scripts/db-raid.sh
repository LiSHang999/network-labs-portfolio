#!/bin/bash
{
echo "=== create RAID10 (4x5GB) ==="
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/nvme0n2 /dev/nvme0n3 /dev/nvme0n4 /dev/nvme0n5 --force --run 2>&1
sleep 5
echo "=== LVM on md0 ==="
pvcreate -y /dev/md0 2>&1
vgcreate vg_data /dev/md0 2>&1
lvcreate -y -L 9G -n lv_data vg_data 2>&1
mkfs.xfs -f /dev/vg_data/lv_data 2>&1
mkdir -p /data
mount /dev/vg_data/lv_data /data
grep -q '/data ' /etc/fstab || echo '/dev/vg_data/lv_data /data xfs defaults 0 0' >> /etc/fstab
mdadm --detail --scan >> /etc/mdadm.conf
echo "=== mdadm -D /dev/md0 ==="
mdadm -D /dev/md0
echo "=== lsblk ==="
lsblk
echo "=== df -hT /data ==="
df -hT /data
echo "=== test write ==="
echo "raid10+lvm ok" > /data/test.txt && cat /data/test.txt
} > /root/raid.txt 2>&1
