# -*- coding: utf-8 -*-
"""任务2.1：由 centos6.5 克隆出 file 虚拟机，串口改 9005，移除光驱，启动。"""
import sys

from pyVim.connect import Disconnect
from pyVmomi import vim

import p2


def main():
    si = p2.connect()
    try:
        src = p2.find_vm(si, "centos6.5")
        if src is None:
            sys.exit("centos6.5 not found")
        if src.runtime.powerState != "poweredOff":
            sys.exit("centos6.5 must be powered off, now " + src.runtime.powerState)

        existing = p2.find_vm(si, "file")
        if existing:
            print("file already exists:", existing.runtime.powerState)
            vm = existing
        else:
            ds = p2.find_ds(si, "datastore-centos6")
            spec = vim.vm.CloneSpec(
                location=vim.vm.RelocateSpec(
                    pool=src.resourcePool, datastore=ds),
                powerOn=False, template=False)
            task = src.CloneVM_Task(folder=src.parent, name="file", spec=spec)
            vm = p2.wait_task(task, timeout=1800)
            print("cloned ->", vm.name)

        # 收集需要修改的设备
        changes = []
        for d in vm.config.hardware.device:
            t = type(d).__name__
            if t.endswith("VirtualSerialPort"):
                d.backing.serviceURI = "tcp://127.0.0.1:9005"
                d.connectable.connected = True
                d.connectable.startConnected = True
                changes.append(vim.vm.device.VirtualDeviceSpec(
                    operation=vim.vm.device.VirtualDeviceSpec.Operation.edit,
                    device=d))
                print("serial -> 9005")
            elif t.endswith("VirtualCdrom"):
                changes.append(vim.vm.device.VirtualDeviceSpec(
                    operation=vim.vm.device.VirtualDeviceSpec.Operation.remove,
                    device=d))
                print("cdrom removed")
        if changes:
            p2.wait_task(vm.ReconfigVM_Task(spec=vim.vm.ConfigSpec(deviceChange=changes)))

        if vm.runtime.powerState != "poweredOn":
            p2.wait_task(vm.PowerOnVM_Task())
        print("file power:", vm.runtime.powerState)
    finally:
        Disconnect(si)


if __name__ == "__main__":
    main()
