#!/bin/bash
{
echo "=== rpm -q bridge-utils ==="
rpm -q bridge-utils 2>&1
echo "=== which brctl ==="
which brctl 2>&1
echo "=== ls -l /usr/sbin/brctl ==="
ls -l /usr/sbin/brctl 2>&1
echo "=== brctl --version ==="
brctl --version 2>&1
} > /root/verify.txt 2>&1
