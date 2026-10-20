# -*- coding: utf-8 -*-
"""在 ESXi 上用 python3 起一个只提供 /ks.cfg 的 HTTP 服务（后台保持 SSH 会话）。"""
import os
import time

import paramiko

HOST = "192.168.61.143"
USER = "root"
PASS = os.environ["ESXI_PASS"]

SERVER = r'''
import socket, os, sys
DATA = open('/tmp/www/ks.cfg','rb').read()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 8000))
s.listen(20)
sys.stderr.write('listening %d bytes\n' % len(DATA))
while True:
    c, a = s.accept()
    try:
        req = c.recv(4096)
        line = req.split(b'\r\n')[0].decode('latin-1')
        sys.stderr.write('REQ %s %s\n' % (a, line))
        path = line.split(' ')[1] if ' ' in line else '/'
        if path in ('/ks.cfg', '/ks.cfg?'):
            body = DATA
            hdr = b'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\nContent-Length: %d\r\nConnection: close\r\n\r\n' % len(body)
        else:
            body = b'not found\n'
            hdr = b'HTTP/1.0 404 Not Found\r\nContent-Length: %d\r\nConnection: close\r\n\r\n' % len(body)
        c.sendall(hdr + body)
    except Exception as e:
        sys.stderr.write('ERR %s\n' % e)
    finally:
        try: c.close()
        except Exception: pass
'''

def main():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS, timeout=15,
              look_for_keys=False, allow_agent=False)
    sftp = c.open_sftp()
    try:
        sftp.mkdir("/tmp/www")
    except IOError:
        pass
    with open("www/ks.cfg", "rb") as f:
        data = f.read()
    with sftp.open("/tmp/www/ks.cfg", "wb") as f:
        f.write(data)
    with sftp.open("/tmp/www/ksserve.py", "w") as f:
        f.write(SERVER)
    print("uploaded", len(data), flush=True)
    sftp.close()
    chan = c.get_transport().open_session()
    chan.exec_command("python3 /tmp/www/ksserve.py")
    while True:
        while chan.recv_ready():
            print("SRV:", chan.recv(4096).decode('utf-8', 'replace').rstrip(), flush=True)
        if chan.exit_status_ready():
            print("server exited", flush=True)
            break
        time.sleep(1)

if __name__ == "__main__":
    main()
