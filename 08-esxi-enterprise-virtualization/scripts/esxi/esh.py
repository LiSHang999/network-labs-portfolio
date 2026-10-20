# -*- coding: utf-8 -*-
"""ESXi SSH 执行封装。"""
import os

import paramiko

USER = "root"
PASS = os.environ["ESXI_PASS"]


def run(host, cmd, timeout=60):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username=USER, password=PASS, timeout=15,
              look_for_keys=False, allow_agent=False)
    try:
        ch = c.get_transport().open_session()
        ch.exec_command(cmd)
        out = ch.makefile("rb").read().decode("utf-8", "replace")
        err = ch.makefile_stderr("rb").read().decode("utf-8", "replace")
        rc = ch.recv_exit_status()
        return rc, out, err
    finally:
        c.close()


def runv(host, cmd, timeout=60, check=False):
    rc, out, err = run(host, cmd, timeout)
    print("$ [%s] %s" % (host, cmd))
    if out.strip():
        print(out.rstrip())
    if err.strip():
        print("ERR:", err.rstrip())
    print("rc =", rc)
    if check and rc != 0:
        raise RuntimeError("command failed on %s: %s" % (host, cmd))
    return out
