# -*- coding: utf-8 -*-
"""准备 store（CentOS 8）Workstation 虚拟机：存储网卡、VNC、100G 数据盘。"""
import os
import subprocess

VMX = r"G:\VMware\LC\CentOS 8\CentOS 8 64 位.vmx"
VMXDIR = os.path.dirname(VMX)
VDISK = os.path.join(VMXDIR, "store-data.vmdk")
VDISKMGR = r"G:\VMware\TOOL\vmware-vdiskmanager.exe"

ADD = [
    'ethernet1.present = "TRUE"',
    'ethernet1.virtualDev = "vmxnet3"',
    'ethernet1.connectionType = "pvn"',
    'ethernet1.pvnID = "7a 13 45 b2 9c 6d 44 01-22 9f 0a 8c 5d 3e 71 b6"',
    'ethernet1.startConnected = "TRUE"',
    'ethernet1.addressType = "generated"',
    'ethernet1.pciSlotNumber = "224"',
    'RemoteDisplay.vnc.enabled = "TRUE"',
    'RemoteDisplay.vnc.port = "5905"',
    'RemoteDisplay.vnc.password = os.environ.get("VNC_PASS", "")',
    'scsi0.present = "TRUE"',
    'scsi0.virtualDev = "pvscsi"',
    'scsi0:0.present = "TRUE"',
    'scsi0:0.fileName = "store-data.vmdk"',
    'scsi0:0.deviceType = "scsi-hardDisk"',
]


def main():
    with open(VMX, "r", encoding="gbk") as f:
        lines = f.read().splitlines()
    keys = {l.split("=")[0].strip().lower() for l in lines if "=" in l}
    for entry in ADD:
        k = entry.split("=")[0].strip().lower()
        if k not in keys:
            lines.append(entry)
    with open(VMX, "w", encoding="gbk", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")
    print("vmx patched")

    if not os.path.exists(VDISK):
        out = subprocess.run(
            [VDISKMGR, "-c", "-s", "100GB", "-a", "lsilogic", "-t", "0", VDISK],
            capture_output=True, text=True)
        print("vdisk:", out.returncode, out.stdout.strip(), out.stderr.strip())
    else:
        print("vdisk exists")


if __name__ == "__main__":
    main()
