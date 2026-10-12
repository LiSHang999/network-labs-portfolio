#!/bin/bash
echo "=== installing rpm ==="
rpm -ivh /root/bridge-utils-1.5-9.el7.x86_64.rpm 2>&1
echo "RPM_EXIT=$?"
echo "=== brctl version ==="
brctl --version 2>&1
echo "BRCTL_EXIT=$?"
