# -*- coding: utf-8 -*-
"""在 ESXi2 上创建 database 虚拟机（CentOS 6.5，数据网段，串口 9010）。"""
import p2
from pyVim.connect import Disconnect
from pyVmomi import vim

HOST = "192.168.61.20"
ISO = "[datastore-centos6] iso/CentOS-6.5-x86_64-auto2.iso"


def main():
    si = p2.connect(host=HOST)
    try:
        dc = p2.dc_of(si)
        if p2.find_vm(si, "database"):
            print("database exists")
            return
        host = dc.hostFolder.childEntity[0].host[0]
        ds = p2.find_ds(si, "datastore-centos6")

        ide = vim.vm.device.VirtualIDEController()
        ide.key = 200
        ide.busNumber = 0
        ide.device = [0, 1]

        sio = vim.vm.device.VirtualSIOController()
        sio.key = 400
        sio.device = [0, 1, 2, 3]

        scsi = vim.vm.device.VirtualLsiLogicController()
        scsi.key = 1000
        scsi.busNumber = 0
        scsi.sharedBus = vim.vm.device.VirtualSCSIController.Sharing.noSharing
        scsi.device = list(range(16))

        disk = vim.vm.device.VirtualDisk()
        disk.key = 2000
        disk.controllerKey = 1000
        disk.unitNumber = 0
        disk.capacityInKB = 16 * 1024 * 1024
        disk.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        disk.backing.fileName = "[datastore-centos6] vm/database/database.vmdk"
        disk.backing.diskMode = "persistent"

        cd = vim.vm.device.VirtualCdrom()
        cd.key = 3002
        cd.controllerKey = 200
        cd.unitNumber = 0
        cd.backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=ISO)
        cd.connectable = vim.vm.device.VirtualDevice.ConnectInfo(
            connected=True, startConnected=True, allowGuestControl=False)

        nic = vim.vm.device.VirtualE1000()
        nic.key = 4000
        nic.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo(
            deviceName="data", useAutoDetect=False)
        nic.connectable = vim.vm.device.VirtualDevice.ConnectInfo(
            connected=True, startConnected=True, allowGuestControl=False)
        nic.addressType = "generated"

        serial = vim.vm.device.VirtualSerialPort()
        serial.key = 9000
        serial.unitNumber = 0
        serial.controllerKey = 400
        serial.backing = vim.vm.device.VirtualSerialPort.URIBackingInfo(
            direction="server", serviceURI="tcp://127.0.0.1:9010")
        serial.connectable = vim.vm.device.VirtualDevice.ConnectInfo(
            connected=True, startConnected=True, allowGuestControl=False)

        spec = vim.vm.ConfigSpec(
            name="database", memoryMB=1024, numCPUs=1,
            guestId="centos6_64Guest",
            files=vim.vm.FileInfo(
                vmPathName="[datastore-centos6] vm/database/database.vmx"),
            deviceChange=[
                vim.vm.device.VirtualDeviceSpec(operation="add", device=d)
                for d in (ide, sio, scsi, disk, cd, nic, serial)
            ],
        )
        task = dc.vmFolder.CreateVM_Task(config=spec, pool=host.parent.resourcePool)
        vm = p2.wait_task(task, timeout=600)
        print("created", vm.name)

        # 设置启动顺序：光驱优先
        boot = vim.vm.BootOptions(bootOrder=[
            vim.vm.BootOptions.BootableCdromDevice(),
            vim.vm.BootOptions.BootableDiskDevice(deviceKey=2000),
        ])
        p2.wait_task(vm.ReconfigVM_Task(spec=vim.vm.ConfigSpec(bootOptions=boot)))
        print("boot order set")

        p2.wait_task(vm.PowerOnVM_Task())
        print("power", vm.runtime.powerState)
    finally:
        Disconnect(si)


if __name__ == "__main__":
    main()
