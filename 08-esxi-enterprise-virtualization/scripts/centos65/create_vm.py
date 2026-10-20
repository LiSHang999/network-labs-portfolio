# -*- coding: utf-8 -*-
"""在 ESXi 上创建 centos6.5 虚拟机并开机，使用自动安装 ISO。"""
import io
import os
import time
from pathlib import Path

import paramiko

HOST = "192.168.61.143"
USER = "root"
PASS = os.environ["ESXI_PASS"]
VMDIR = "/vmfs/volumes/datastore-centos6/vm/centos6.5"
VMX = VMDIR + "/centos6.5.vmx"
DISK = VMDIR + "/centos6.5.vmdk"
ISO = "/vmfs/volumes/datastore-centos6/iso/CentOS-6.5-i386.iso"

VMX_TEXT = """.encoding = "UTF-8"
config.version = "8"
virtualHW.version = "10"
guestOS = "otherLinuxGuest"
firmware = "bios"
displayName = "centos6.5"
memSize = "2048"
numvcpus = "1"
cpuid.coresPerSocket = "1"
scsi0.present = "TRUE"
scsi0.virtualDev = "lsilogic"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "centos6.5.vmdk"
scsi0:0.deviceType = "scsi-hardDisk"
ide1:0.present = "TRUE"
ide1:0.fileName = "%s"
ide1:0.deviceType = "cdrom-image"
ethernet0.present = "TRUE"
ethernet0.virtualDev = "e1000"
ethernet0.networkName = "VM Network"
ethernet0.addressType = "generated"
ethernet0.startConnected = "TRUE"
bios.bootOrder = "cdrom,hdd"
bios.bootDelay = "3000"
RemoteDisplay.vnc.enabled = "TRUE"
RemoteDisplay.vnc.port = "5901"
RemoteDisplay.vnc.password = "__VNC_PASS__"
tools.syncTime = "FALSE"
""".replace("__VNC_PASS__", os.environ.get("VNC_PASS", "")) % ISO


def run(c, cmd, timeout=300):
    print("### " + cmd, flush=True)
    _in, out, err = c.exec_command(cmd, timeout=timeout)
    o = out.read().decode("utf-8", "replace")
    e = err.read().decode("utf-8", "replace")
    if o.strip():
        print(o[-3000:], flush=True)
    if e.strip():
        print("ERR: " + e[-2000:], flush=True)
    return o, e


def main():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

    run(c, f"mkdir -p {VMDIR}")
    run(c, f"ls -l {ISO}")
    run(c, f"vmkfstools -c 16G -d thin {DISK}")
    run(c, f"ls -lh {VMDIR}")

    sftp = c.open_sftp()
    with sftp.file(VMX, "w") as f:
        f.write(VMX_TEXT)
    sftp.close()
    run(c, f"cat {VMX}")

    out, _ = run(c, f"vim-cmd solo/registervm {VMX}")
    vmid = ""
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit():
            vmid = line
            break
    print("VMID=", vmid, flush=True)
    if not vmid:
        raise RuntimeError("registervm 未返回 VMID")

    run(c, "vim-cmd vmsvc/getallvms")
    run(c, f"vim-cmd vmsvc/power.on {vmid}")
    time.sleep(3)
    run(c, f"vim-cmd vmsvc/power.getstate {vmid}")
    run(c, f"vim-cmd vmsvc/get.summary {vmid}")
    c.close()


if __name__ == "__main__":
    main()
