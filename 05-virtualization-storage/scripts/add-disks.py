import glob, os

CRLF = '\r\n'

def find_vmx(name):
    return [x for x in glob.glob(r'G:\VMware\LC\**\*.vmx', recursive=True) if os.path.basename(x) == name][0]

def nvme_disk(idx, filename):
    return CRLF.join([
        f'nvme0:{idx}.present = "TRUE"',
        f'nvme0:{idx}.fileName = "{filename}"',
        f'nvme0:{idx}.mode = "persistent"',
    ])

# database: add nvme0:1..4
p = find_vmx('database.vmx')
raw = open(p, 'rb').read()
text = raw.decode('utf-8')
block = CRLF.join([nvme_disk(i, f'database-disk{i+1}.vmdk') for i in range(1, 5)])
text = text.rstrip('\r\n') + CRLF + CRLF + block + CRLF
open(p, 'wb').write(text.encode('utf-8'))
print('WROTE database.vmx (added nvme0:1..4)')

# file: add nvme0:1
p = find_vmx('file.vmx')
raw = open(p, 'rb').read()
text = raw.decode('utf-8')
block = nvme_disk(1, 'file-disk2.vmdk')
text = text.rstrip('\r\n') + CRLF + CRLF + block + CRLF
open(p, 'wb').write(text.encode('utf-8'))
print('WROTE file.vmx (added nvme0:1)')

# verify
for name in ('database.vmx', 'file.vmx'):
    p = find_vmx(name)
    print('=====', name, '=====')
    for line in open(p, encoding='utf-8').read().splitlines():
        if 'nvme0:' in line:
            print(' ', line)
