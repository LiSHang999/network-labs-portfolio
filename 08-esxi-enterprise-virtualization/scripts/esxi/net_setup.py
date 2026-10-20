# -*- coding: utf-8 -*-
"""任务2.2/2.3 网络骨架：两台 ESXi 建 sw-data/data、sw-store/store、vmk1。"""
import sys

import esh

HOSTS = {
    "192.168.61.143": "192.168.50.10",
    "192.168.61.20": "192.168.50.20",
}


def ensure_vswitch(host, name, uplink):
    out = esh.runv(host, "esxcli network vswitch standard list")
    if ("Name: %s\n" % name) not in out:
        esh.runv(host, "esxcli network vswitch standard add -v %s" % name, check=True)
    # 上行链路幂等添加
    esh.run(host, "esxcli network vswitch standard uplink add -u %s -v %s" % (uplink, name))


def ensure_pg(host, pg, vswitch):
    out = esh.runv(host, "esxcli network vswitch standard portgroup list")
    if ("Name: %s\n" % pg) not in out:
        esh.runv(host, "esxcli network vswitch standard portgroup add -p %s -v %s" % (pg, vswitch), check=True)


def ensure_vmk(host, name, pg, ip):
    out = esh.runv(host, "esxcli network ip interface list")
    if ("Name: %s\n" % name) not in out:
        esh.runv(host, "esxcli network ip interface add -i %s -p %s" % (name, pg), check=True)
    esh.runv(host, "esxcli network ip interface set -i %s -e true" % name)
    esh.runv(host, "esxcli network ip interface ipv4 set -i %s -t static -I %s -N 255.255.255.0" % (name, ip), check=True)


def main():
    for host, vmk1_ip in HOSTS.items():
        print("=" * 30, host)
        ensure_vswitch(host, "sw-data", "vmnic1")
        ensure_pg(host, "data", "sw-data")
        ensure_vswitch(host, "sw-store", "vmnic2")
        ensure_pg(host, "store", "sw-store")
        ensure_vmk(host, "vmk1", "store", vmk1_ip)
        esh.runv(host, "esxcli network ip interface ipv4 get")
        esh.runv(host, "esxcli network vswitch standard list | grep -A8 'Name: sw-'")


if __name__ == "__main__":
    main()
