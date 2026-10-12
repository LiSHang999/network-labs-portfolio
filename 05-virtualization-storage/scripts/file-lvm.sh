#!/bin/bash
{
echo "=== LVM on 20G disk ==="
pvcreate -y /dev/nvme0n2 2>&1
vgcreate vg_file /dev/nvme0n2 2>&1
lvcreate -y -l 100%FREE -n lv_file vg_file 2>&1
mkfs.xfs -f /dev/vg_file/lv_file 2>&1
mkdir -p /file
mount /dev/vg_file/lv_file /file
grep -q '/file ' /etc/fstab || echo '/dev/vg_file/lv_file /file xfs defaults 0 0' >> /etc/fstab
echo "=== lsblk ==="
lsblk
echo "=== df -hT /file ==="
df -hT /file
echo "=== test write ==="
echo "lvm ok" > /file/test.txt && cat /file/test.txt
} > /root/lvm.txt 2>&1
