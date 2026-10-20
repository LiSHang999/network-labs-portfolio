# -*- coding: utf-8 -*-
"""项目2 公共工具：连接 ESXi、查找对象、等待任务。"""
import os
import ssl
import time

from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim

HOST = "192.168.61.143"
USER = "root"
PASS = os.environ["ESXI_PASS"]


def connect(host=HOST, user=USER, pwd=PASS):
    return SmartConnect(host=host, user=user, pwd=pwd, port=443,
                        sslContext=ssl._create_unverified_context())


def dc_of(si):
    return si.RetrieveContent().rootFolder.childEntity[0]


def find_vm(si, name):
    for vm in dc_of(si).vmFolder.childEntity:
        if vm.name == name:
            return vm
    return None


def find_ds(si, name):
    for ds in dc_of(si).datastoreFolder.childEntity:
        if ds.name == name:
            return ds
    return None


def wait_task(task, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        if task.info.state == "success":
            return task.info.result
        if task.info.state == "error":
            raise RuntimeError(task.info.error)
        time.sleep(2)
    raise TimeoutError("task timeout")


def power_off(si, vm, timeout=180):
    if vm.runtime.powerState != "poweredOff":
        try:
            vm.ShutdownGuest()
        except Exception:
            pass
        start = time.time()
        while time.time() - start < timeout and vm.runtime.powerState != "poweredOff":
            time.sleep(2)
        if vm.runtime.powerState != "poweredOff":
            wait_task(vm.PowerOffVM_Task())


def power_on(si, vm, timeout=300):
    if vm.runtime.powerState != "poweredOn":
        wait_task(vm.PowerOnVM_Task())
    start = time.time()
    while time.time() - start < timeout:
        if vm.runtime.powerState == "poweredOn":
            return
        time.sleep(2)


def remove_device(si, vm, cls_or_key, keep_net=None):
    """按设备类型或 key 删除设备。cls_or_key 为设备 key。"""
    devs = [d for d in vm.config.hardware.device if d.key == cls_or_key]
    if not devs:
        return
    spec = vim.vm.ConfigSpec(deviceChange=[
        vim.vm.device.VirtualDeviceSpec(
            operation=vim.vm.device.VirtualDeviceSpec.Operation.remove, device=d)
        for d in devs])
    wait_task(vm.ReconfigVM_Task(spec=spec))


if __name__ == "__main__":
    si = connect()
    try:
        for vm in dc_of(si).vmFolder.childEntity:
            print(vm.name, vm.runtime.powerState)
    finally:
        Disconnect(si)
