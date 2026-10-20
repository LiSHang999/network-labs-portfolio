# -*- coding: utf-8 -*-
"""把 ESXi 主机加入 vCenter（带证书指纹，兼容 ESXi1/ESXi2）。"""
import os
import ssl
import sys

from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim

VC = "192.168.61.60"
VC_USER = "administrator@vsphere.local"
VC_PASS = os.environ["VCSA_SSO_PASS"]
THUMB = os.environ["ESXI_THUMBPRINT"]  # openssl s_client 或添加主机向导中获取


def connect():
    return SmartConnect(host=VC, user=VC_USER, pwd=VC_PASS, port=443,
                        sslContext=ssl._create_unverified_context())


def dc(si):
    return si.RetrieveContent().rootFolder.childEntity[0]


def show(si):
    d = dc(si)
    print("Datacenter:", d.name)
    for h in d.hostFolder.childEntity:
        hosts = h.host if hasattr(h, "host") else []
        for hh in hosts:
            print("  host:", hh.name, "connected=", hh.runtime.connectionState,
                  "power=", hh.runtime.powerState)
        for hh in hosts:
            for vm in hh.vm:
                print("    vm:", vm.name, vm.runtime.powerState)


def add(si, ip, user="root", pwd=None):
    pwd = pwd or os.environ["ESXI_PASS"]
    d = dc(si)
    for h in d.hostFolder.childEntity:
        if h.name == ip:
            print("already present:", ip, h.summary.runtime.connectionState)
            return h
    spec = vim.host.ConnectSpec(hostName=ip, userName=user, password=pwd,
                                sslThumbprint=THUMB, force=True)
    task = d.hostFolder.AddStandaloneHost_Task(spec=spec, addConnected=True)
    while task.info.state == "running":
        import time
        time.sleep(2)
    if task.info.state != "success":
        print("ADD FAILED:", task.info.error)
        return None
    h = task.info.result
    print("ADDED:", h.name)
    return h


if __name__ == "__main__":
    si = connect()
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "add":
            ip = sys.argv[2] if len(sys.argv) > 2 else "192.168.61.20"
            add(si, ip)
        show(si)
    finally:
        Disconnect(si)
