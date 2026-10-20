# -*- coding: utf-8 -*-
"""在 CentOS 6.5 minimal ISO 中加入 ks.cfg，并把 isolinux 默认启动项改成自动安装。"""
import os
from pathlib import Path

import pycdlib

BASE = Path(__file__).resolve().parent
SRC = Path(r"E:\Claude Code\虚拟化项目2\iso\CentOS-6.5-x86_64-minimal.iso")
OUT = BASE / "CentOS-6.5-x86_64-auto.iso"
ROOT_PW = os.environ["KS_ROOT_PASSWORD"]
KS_LOCAL = BASE / "ks.cfg"
CFG_LOCAL = BASE / "isolinux-auto.cfg"

KS = rf"""#version=DEVEL
install
unsupported_hardware
cdrom
lang en_US.UTF-8
keyboard us
timezone Asia/Shanghai
rootpw --plaintext {ROOT_PW}
selinux --disabled
firewall --disabled
network --bootproto=static --ip=192.168.61.30 --netmask=255.255.255.0 --gateway=192.168.61.2 --nameserver=192.168.61.2 --device=eth0 --onboot=yes --noipv6
bootloader --location=mbr --driveorder=sda --append="crashkernel=auto"
zerombr
clearpart --all --initlabel
part /boot --fstype=ext4 --size=500
part pv.01 --size=1 --grow
volgroup vg00 pv.01
logvol / --fstype=ext4 --name=lv_root --vgname=vg00 --size=1 --grow
logvol swap --name=lv_swap --vgname=vg00 --size=2048
reboot --eject

%packages
@core
openssh-server
openssh-clients
%end

%post
cat > /etc/sysconfig/network-scripts/ifcfg-eth0 <<'EOF'
DEVICE=eth0
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.61.30
NETMASK=255.255.255.0
GATEWAY=192.168.61.2
DNS1=192.168.61.2
NM_CONTROLLED=no
EOF
sed -i 's/^HOSTNAME=.*/HOSTNAME=centos6.5/' /etc/sysconfig/network
grep -q '192.168.61.30' /etc/hosts || echo '192.168.61.30 centos6.5' >> /etc/hosts
chkconfig network on
%end
"""


def main():
    cfg = (BASE / "isolinux.cfg.orig").read_text(encoding="utf-8")
    cfg = cfg.replace("timeout 600", "timeout 10")
    cfg = cfg.replace(
        "  append initrd=initrd.img\n",
        "  append initrd=initrd.img ks=cdrom:/ks.cfg text unsupported_hardware "
        "ip=192.168.61.30::192.168.61.2:255.255.255.0::eth0:off sshd sshpw=root:{ROOT_PW} "
        "console=tty0 console=ttyS0,115200\n",
        1,
    )
    KS_LOCAL.write_text(KS, encoding="utf-8", newline="\n")
    CFG_LOCAL.write_text(cfg, encoding="utf-8", newline="\n")

    iso = pycdlib.PyCdlib()
    iso.open(str(SRC))
    iso.update_file_contents(str(CFG_LOCAL), iso_path="/ISOLINUX/ISOLINUX.CFG;1")
    iso.add_file(
        str(KS_LOCAL),
        iso_path="/KS.CFG;1",
        rr_name="ks.cfg",
        joliet_path="/ks.cfg",
        file_mode=0o644,
    )
    iso.write(str(OUT))
    iso.close()
    print("built", OUT, OUT.stat().st_size)

    # 校验
    chk = pycdlib.PyCdlib()
    chk.open(str(OUT))
    chk.get_file_from_iso(local_path=str(BASE / "check-isolinux.cfg"), iso_path="/ISOLINUX/ISOLINUX.CFG;1")
    chk.get_file_from_iso(local_path=str(BASE / "check-ks.cfg"), iso_path="/KS.CFG;1")
    chk.close()
    txt = (BASE / "check-isolinux.cfg").read_text(encoding="utf-8")
    assert "ks=cdrom:/ks.cfg text" in txt, "isolinux.cfg 未正确修改"
    assert ROOT_PW in (BASE / "check-ks.cfg").read_text(encoding="utf-8")
    print("verify OK")


if __name__ == "__main__":
    main()
