# -*- coding: utf-8 -*-
"""通过 SOAP ReconfigVM_Task 给 centos6.5 添加网络串口（VM 端 listen 127.0.0.1:9000）。"""
import http.cookiejar
import os
import ssl
import time
import urllib.request
import xml.etree.ElementTree as ET

HOST = "192.168.61.143"
URL = f"https://{HOST}/sdk"
NS = "urn:vim25"

ctx = ssl._create_unverified_context()
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ctx),
    urllib.request.HTTPCookieProcessor(jar),
)


def call(inner):
    env = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soapenv:Body>{inner}</soapenv:Body></soapenv:Envelope>'''
    req = urllib.request.Request(
        URL,
        data=env.encode("utf-8"),
        headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:vim25/8.0"},
    )
    with opener.open(req, timeout=60) as resp:
        return ET.fromstring(resp.read())


def q(tag):
    return f"{{{NS}}}{tag}"


def main():
    sc = call('<RetrieveServiceContent xmlns="urn:vim25"><_this type="ServiceInstance">ServiceInstance</_this></RetrieveServiceContent>')
    sm = sc.find(".//" + q("sessionManager")).text
    pc = sc.find(".//" + q("propertyCollector")).text
    call(f'<Login xmlns="urn:vim25"><_this type="SessionManager">{sm}</_this><userName>root</userName><password>{os.environ['ESXI_PASS']}</password></Login>')

    # 查询现有串口设备 key
    rp = call(
        f'<RetrievePropertiesEx xmlns="urn:vim25"><_this type="PropertyCollector">{pc}</_this>'
        f'<specSet><propSet><type>VirtualMachine</type><all>false</all><pathSet>config.hardware.device</pathSet></propSet>'
        f'<objectSet><obj type="VirtualMachine">1</obj></objectSet></specSet><options/></RetrievePropertiesEx>'
    )
    old_keys = []
    for el in rp.iter():
        if el.tag.endswith("VirtualSerialPort"):
            k = el.find(q("key"))
            if k is not None and k.text:
                old_keys.append(k.text)
    print("existing serial keys", old_keys)

    removes = "".join(
        f'<deviceChange><operation>remove</operation><device xsi:type="vim.vm.device.VirtualSerialPort"><key>{k}</key></device></deviceChange>'
        for k in old_keys
    )

    spec = f'''
<spec>
  {removes}
  <deviceChange>
    <operation>add</operation>
    <device xsi:type="vim.vm.device.VirtualSerialPort">
      <key>-1</key>
      <deviceInfo><label>Serial port 0</label><summary>serial</summary></deviceInfo>
      <backing xsi:type="vim.vm.device.VirtualSerialPort.URIBackingInfo">
        <direction>server</direction>
        <serviceURI>tcp://127.0.0.1:9000</serviceURI>
      </backing>
      <connectable><connected>true</connected><startConnected>true</startConnected></connectable>
      <yieldOnMsrRead>true</yieldOnMsrRead>
      <unitNumber>0</unitNumber>
    </device>
  </deviceChange>
</spec>'''
    try:
        r = call(f'<ReconfigVM_Task xmlns="urn:vim25"><_this type="VirtualMachine">1</_this>{spec}</ReconfigVM_Task>')
    except urllib.error.HTTPError as exc:
        print("HTTP", exc.code)
        print(exc.read().decode("utf-8", "replace"))
        return
    task = r.find(".//" + q("returnval")).text
    print("task", task)
    for _ in range(30):
        time.sleep(2)
        tr = call(
            f'<RetrievePropertiesEx xmlns="urn:vim25"><_this type="PropertyCollector">{pc}</_this>'
            f'<specSet><propSet><type>Task</type><all>false</all><pathSet>info.state</pathSet><pathSet>info.result</pathSet><pathSet>info.error</pathSet></propSet>'
            f'<objectSet><obj type="Task">{task}</obj></objectSet></specSet><options/></RetrievePropertiesEx>'
        )
        state = None
        for ps in tr.findall(".//" + q("propSet")):
            name = ps.find(q("name"))
            val = ps.find(q("val"))
            if name is not None and name.text == "info.state" and val is not None:
                state = val.text
        print("state", state)
        if state in ("success", "error"):
            print(ET.tostring(tr, encoding="unicode")[:2000])
            break


if __name__ == "__main__":
    main()
