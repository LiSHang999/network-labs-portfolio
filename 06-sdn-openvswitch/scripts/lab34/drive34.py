#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""实验3.4 驱动：通过 SSH 向 Guest :0 桌面的 xterm 输入命令并截图。

分阶段运行，便于逐段核对：
  env-switch / env-host / ps / enslave / netserver / host-apt /
  host-before / qos / host-after / mirror / collect
"""
import os
import sys
import time
import shlex
import paramiko

PASS = os.environ["VMPASS"]
SW = os.environ.get("SW", "192.168.61.142")
H1 = os.environ.get("H1", "192.168.61.141")
JUMP = os.environ.get("JUMP", "")
USER = "ubuntu"
XPRE = "export DISPLAY=:0 XAUTHORITY=$(cat /tmp/xauth34); "


class Guest:
    def __init__(self, host):
        self.host = host
        self.c = None
        self.base = None
        self.connect()

    def connect(self):
        sock = None
        if JUMP and self.host != JUMP:
            base = paramiko.SSHClient()
            base.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            base.connect(JUMP, username=USER, password=PASS, timeout=10,
                         banner_timeout=20, auth_timeout=20,
                         look_for_keys=False, allow_agent=False)
            self.base = base
            sock = base.get_transport().open_channel(
                "direct-tcpip", (self.host, 22), ("127.0.0.1", 0))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(self.host, username=USER, password=PASS, timeout=10,
                  banner_timeout=20, auth_timeout=20,
                  look_for_keys=False, allow_agent=False, sock=sock)
        self.c = c

    def run(self, cmd, sudo=False, timeout=120, quiet=True):
        full = "sudo -S -p '' /bin/bash -lc " + shlex.quote(cmd) if sudo else cmd
        ch = self.c.get_transport().open_session()
        ch.get_pty()
        ch.exec_command(full)
        if sudo:
            ch.sendall(PASS + "\n")
        out = []
        end = time.time() + timeout
        while True:
            if ch.recv_ready():
                out.append(ch.recv(65536).decode("utf-8", "replace"))
                continue
            if ch.recv_stderr_ready():
                out.append(ch.recv_stderr(65536).decode("utf-8", "replace"))
                continue
            if ch.exit_status_ready():
                break
            if time.time() > end:
                ch.close()
                raise TimeoutError(cmd[:80])
            time.sleep(0.05)
        rc = ch.recv_exit_status()
        ch.close()
        text = "".join(out)
        if not quiet:
            sys.stdout.write(text)
        return rc, text

    # ---- xterm 操作 ----
    def focus(self):
        rc, out = self.run(XPRE + "W=$(xdotool search --class xterm | tail -1); echo $W; xdotool windowactivate --sync $W", sudo=True)
        return out.strip().splitlines()[-1] if out.strip() else "?"

    def typ(self, text, enter=True, delay=25):
        self.run(XPRE + "xdotool type --clearmodifiers --delay %d -- %s" % (delay, shlex.quote(text)), sudo=True)
        if enter:
            self.run(XPRE + "xdotool key --clearmodifiers Return", sudo=True)

    def key(self, k):
        self.run(XPRE + "xdotool key --clearmodifiers %s" % k, sudo=True)

    def clear(self):
        self.typ("clear")
        time.sleep(0.4)

    def shot(self, name):
        self.run("mkdir -p /tmp/shots34; /usr/local/bin/shot34 /tmp/shots34/%s.png; echo SHOT-%s" % (name, name), sudo=True)
        print("  [shot] %s" % name)


def sw():
    return Guest(SW)


def h1():
    return Guest(H1)


def phase_env_switch():
    g = sw()
    g.focus()
    g.clear()
    g.typ("apt install --reinstall -y netperf")
    time.sleep(16)
    g.shot("01-apt-netperf")
    g.clear()
    g.typ("ifconfig")
    time.sleep(1.5)
    g.shot("02-ifconfig-switch")
    g.clear()
    g.typ("ovs-vsctl show")
    time.sleep(1.2)
    g.typ("ovs-vsctl del-br br0")
    time.sleep(1.2)
    g.typ("ovs-vsctl show")
    time.sleep(1.5)
    g.shot("03-ovs-delbr")
    print("env-switch done")


def phase_env_host():
    g = h1()
    g.focus()
    g.clear()
    g.typ("ifconfig")
    time.sleep(1.5)
    g.shot("04-ifconfig-host")
    g.clear()
    g.typ("ping 192.168.61.142")
    time.sleep(6)
    g.shot("05-ping-replies")
    g.key("ctrl+c")
    time.sleep(1.5)
    g.shot("06-ping-stats")
    print("env-host done")


def phase_ps():
    g = sw()
    g.focus()
    g.clear()
    g.typ("ps -ef | grep ovs")
    time.sleep(1.5)
    g.shot("07-ps-ovs")
    print("ps done")


def phase_enslave():
    g = sw()
    g.focus()
    g.clear()
    # 预埋：挂载后 6 秒自动截图，再执行恢复脚本
    g.run("rm -f /tmp/shots34/08-addbr-addport.png; "
          "setsid nohup bash -c 'sleep 6; /usr/local/bin/shot34 /tmp/shots34/08-addbr-addport.png; "
          "sleep 1; bash /tmp/recover34.sh' >/tmp/sched34.log 2>&1 </dev/null &", sudo=True)
    time.sleep(0.5)
    g.typ("ovs-vsctl add-br br0")
    time.sleep(1.0)
    try:
        g.typ("ovs-vsctl add-port br0 ens33")
    except Exception as e:
        print("  add-port 输入时连接中断（预期）:", e)
    try:
        g.c.close()
    except Exception:
        pass
    print("  等待 br0 恢复 ...")
    time.sleep(16)
    last = None
    for _ in range(12):
        try:
            g2 = sw()
            rc, out = g2.run("ip -4 -o addr show br0; ip route | head -3")
            print(out)
            last = g2
            break
        except Exception as e:
            last = e
            time.sleep(4)
    if not isinstance(last, Guest):
        raise SystemExit("br0 恢复失败: %s" % last)
    g2 = last
    g2.focus()
    g2.clear()
    g2.typ("ifconfig ens33 0 up")
    time.sleep(0.6)
    g2.typ("ifconfig br0 192.168.61.142/24 up")
    time.sleep(0.6)
    g2.typ("ifconfig")
    time.sleep(1.5)
    g2.shot("09-br0-ifconfig")
    print("enslave done")


def phase_netserver():
    g = sw()
    g.focus()
    g.clear()
    g.typ("netserver -p 9991")
    time.sleep(2)
    g.typ("ps -ef | grep netserver")
    time.sleep(1.5)
    g.shot("10-netserver")
    print("netserver done")


def phase_host_apt():
    g = h1()
    g.focus()
    g.clear()
    g.typ("apt install --reinstall -y netperf")
    time.sleep(16)
    g.shot("11-apt-netperf-host")
    print("host-apt done")


def phase_host_before():
    g = h1()
    g.focus()
    g.clear()
    g.typ("netperf -t UDP_STREAM -H 192.168.61.142 -P 9991")
    time.sleep(14)
    g.shot("12-netperf-before")
    print("host-before done")


def phase_qos():
    g = sw()
    g.focus()
    g.clear()
    g.typ("ovs-vsctl set interface ens33 ingress_policing_rate=100000")
    time.sleep(0.8)
    g.typ("ovs-vsctl set interface ens33 ingress_policing_burst=50000")
    time.sleep(1.2)
    g.shot("13-qos-set")
    print("qos done")


def phase_host_after():
    g = h1()
    g.focus()
    g.clear()
    g.typ("netperf -t UDP_STREAM -H 192.168.61.142 -P 9991")
    time.sleep(14)
    g.shot("14-netperf-after1")
    g.clear()
    g.typ("netperf -t UDP_STREAM -H 192.168.61.142 -P 9991")
    time.sleep(14)
    g.shot("15-netperf-after2")
    print("host-after done")


def phase_mirror():
    g = sw()
    g.focus()
    def _uuid(out):
        for line in reversed(out.splitlines()):
            s = line.strip().strip('"')
            if len(s) == 36 and s.count("-") == 4:
                return s
        raise SystemExit("无法解析 UUID，原始输出: %r" % out)

    rc, br = g.run("ovs-vsctl get port br0 _uuid", sudo=True)
    rc, en = g.run("ovs-vsctl get port ens33 _uuid", sudo=True)
    br, en = _uuid(br), _uuid(en)
    print("  br0=%s  ens33=%s" % (br, en))
    g.clear()
    g.typ("ovs-vsctl show")
    time.sleep(1.5)
    g.shot("16-ovs-show-scene2")
    g.clear()
    g.typ("ovs-vsctl list port br0")
    time.sleep(1.8)
    g.shot("17-list-port-br0")
    g.clear()
    g.typ("ovs-vsctl list port ens33")
    time.sleep(1.8)
    g.shot("18-list-port-ens33")
    g.clear()
    cmd = ("ovs-vsctl -- set bridge br0 mirrors=@m -- --id=@m create mirror "
           "name=mymirror select-dst-port=%s select-src-port=%s output-port=%s" % (en, en, br))
    g.typ(cmd)
    time.sleep(2)
    g.shot("19-mirror")
    rc, out = g.run("ovs-vsctl list mirror", quiet=False)
    print("mirror done")


def phase_prep_switch():
    """重启后清理 OVS 状态并重建 :0 桌面的 root xterm（经 host1 跳板）。"""
    g = Guest(SW)
    g.run("pkill -x ovs-vswitchd; pkill -x ovsdb-server; sleep 1; "
          "rm -f /usr/local/var/run/openvswitch/db.sock /usr/local/var/run/openvswitch/*.pid "
          "/usr/local/etc/openvswitch/.conf.db.~lock~; "
          "rm -f /usr/local/etc/openvswitch/conf.db; "
          "ovsdb-tool create /usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema; "
          "sh /root/start-ovs.sh; sleep 3; ovs-vsctl show", sudo=True, quiet=False)
    g.run("DISPLAY=:0 XAUTHORITY=$(cat /tmp/xauth34) xrandr --output Virtual1 --mode 1280x800 2>/dev/null; "
          "bash /tmp/prep34.sh", sudo=True, quiet=False)
    g = Guest(SW)
    g.focus()
    g.typ("clear")
    time.sleep(0.5)
    g.typ("su - root")
    time.sleep(2)
    g.typ(PASS, delay=20)
    time.sleep(2)
    g.typ("clear")
    time.sleep(0.5)
    g.typ("echo READY-ROOT")
    time.sleep(1)
    g.shot("00-ready")
    print("prep-switch done")


SEQ34 = r'''#!/bin/bash
export DISPLAY=:0 XAUTHORITY=$(cat /tmp/xauth34)
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
W=$(xdotool search --class xterm | tail -1)
xdotool windowactivate --sync $W
sleep 1
xdotool type --clearmodifiers --delay 20 -- 'ovs-vsctl add-br br0'; xdotool key Return
sleep 1
xdotool type --clearmodifiers --delay 5 -- 'ovs-vsctl add-port br0 ens33'; xdotool key Return
sleep 4
/usr/local/bin/shot34 /tmp/shots34/08-addbr-addport.png
ifconfig ens33 0 up
ifconfig br0 192.168.61.142/24 up
ip route replace default via 192.168.61.2 dev br0
sleep 2
xdotool type --clearmodifiers --delay 20 -- 'ifconfig ens33 0 up'; xdotool key Return
sleep 1
xdotool type --clearmodifiers --delay 20 -- 'ifconfig br0 192.168.61.142/24 up'; xdotool key Return
sleep 1
xdotool type --clearmodifiers --delay 20 -- 'ifconfig'; xdotool key Return
sleep 2
/usr/local/bin/shot34 /tmp/shots34/09-br0-ifconfig.png
echo DONE > /tmp/seq34.done
'''


def phase_enslave_local():
    """在 switch1 本地以 systemd 服务跑挂载+恢复+截图序列，SSH 断开也不影响。"""
    g = Guest(SW)
    g.run("cat > /tmp/seq34.sh <<'EOS'\n" + SEQ34 + "EOS\nchmod 755 /tmp/seq34.sh; "
          "rm -f /tmp/seq34.done /tmp/shots34/08-addbr-addport.png /tmp/shots34/09-br0-ifconfig.png; "
          "systemd-run --unit=lab34-seq --collect /bin/bash /tmp/seq34.sh; "
          "echo SCHEDULED", sudo=True, quiet=False)
    print("  等待本地序列执行 ...")
    time.sleep(20)
    try:
        gh = Guest(H1)
        gh.run("ip neigh del 192.168.61.142 dev ens33 2>/dev/null; ping -c 2 -W 2 192.168.61.142", sudo=True, quiet=False)
    except Exception as e:
        print("  host1 刷新邻居失败:", e)
    g2 = None
    for i in range(10):
        try:
            g2 = Guest(SW)
            rc, out = g2.run("ip -4 -o addr show br0; ip route | head -3; cat /tmp/seq34.done 2>&1; ls /tmp/shots34/")
            print(out)
            if "DONE" in out or "09-br0" in out:
                break
        except Exception as e:
            print("  重连中:", e)
            time.sleep(5)
    if g2 is None:
        raise SystemExit("无法重连 switch1")
    print("enslave-local done")


def phase_collect():
    import base64
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
    os.makedirs(outdir, exist_ok=True)
    for host in (SW, H1):
        g = Guest(host)
        rc, listing = g.run("ls /tmp/shots34/*.png 2>/dev/null")
        for path in listing.split():
            rc, b64 = g.run("base64 -w 76 " + path)
            data = base64.b64decode("".join(b64.split()))
            local = os.path.join(outdir, os.path.basename(path))
            open(local, "wb").write(data)
            print("%s -> %s (%d bytes)" % (host, local, len(data)))


if __name__ == "__main__":
    cmd = sys.argv[1]
    fn = {
        "env-switch": phase_env_switch,
        "env-host": phase_env_host,
        "ps": phase_ps,
        "enslave": phase_enslave,
        "prep-switch": phase_prep_switch,
        "enslave-local": phase_enslave_local,
        "netserver": phase_netserver,
        "host-apt": phase_host_apt,
        "host-before": phase_host_before,
        "qos": phase_qos,
        "host-after": phase_host_after,
        "mirror": phase_mirror,
        "collect": phase_collect,
    }[cmd]
    fn()
