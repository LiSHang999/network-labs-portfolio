import glob, os, shutil

PVN_ID = '52 4c 5e 98 70 6a 82 1b-0f eb 97 5d 76 2e 8a 85'
CRLF = '\r\n'

def eth1_block(mac):
    lines = [
        'ethernet1.present = "TRUE"',
        'ethernet1.virtualDev = "vmxnet3"',
        'ethernet1.connectionType = "pvn"',
        f'ethernet1.pvnID = "{PVN_ID}"',
        'ethernet1.startConnected = "TRUE"',
        'ethernet1.addressType = "generated"',
        'ethernet1.pciSlotNumber = "224"',
        'ethernet1.allowguestconnectioncontrol = "false"',
        f'ethernet1.generatedAddress = "{mac}"',
        'ethernet1.generatedAddressOffset = "10"',
    ]
    return CRLF.join(lines)

def find_vmx(name):
    return [x for x in glob.glob(r'G:\VMware\LC\**\*.vmx', recursive=True) if os.path.basename(x) == name][0]

for name, mac in [('web.vmx', '00:0c:29:79:6c:15'), ('file.vmx', '00:0c:29:4f:a3:47')]:
    cur = find_vmx(name)
    bak = cur + '.bak-net'
    # restore pristine original
    shutil.copy(bak, cur)
    raw = open(cur, 'rb').read()
    text = raw.decode('utf-8')

    if name == 'web.vmx':
        # ethernet0 was missing connectionType -> set NAT
        old = 'ethernet0.virtualDev = "vmxnet3"' + CRLF
        new = ('ethernet0.virtualDev = "vmxnet3"' + CRLF +
               'ethernet0.connectionType = "nat"' + CRLF +
               'ethernet0.startConnected = "TRUE"' + CRLF)
        assert old in text, 'web ethernet0.virtualDev not found'
        text = text.replace(old, new, 1)

    # append ethernet1 block
    block = eth1_block(mac)
    text = text.rstrip('\r\n') + CRLF + CRLF + block + CRLF

    open(cur, 'wb').write(text.encode('utf-8'))
    print('WROTE', name)

# verify
for name in ('web.vmx', 'file.vmx', 'database.vmx'):
    p = find_vmx(name)
    print('=====', name, '=====')
    for line in open(p, encoding='utf-8').read().splitlines():
        if 'connectionType' in line or 'pvnID' in line or 'generatedAddress' in line:
            print(' ', line)
