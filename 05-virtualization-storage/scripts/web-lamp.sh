#!/bin/bash
{
echo "=== repolist ==="
yum repolist 2>&1 | head
echo "=== install LAMP (this may take a while) ==="
yum install -y httpd mariadb-server php php-mysqlnd php-gd php-mbstring php-xml php-json php-zip php-curl php-intl 2>&1 | tail -30
echo "=== enable + start services ==="
systemctl enable --now httpd mariadb 2>&1
systemctl is-enabled httpd mariadb 2>&1
systemctl is-active httpd mariadb 2>&1
echo "=== versions ==="
httpd -v 2>&1 | head -1
php -v 2>&1 | head -1
mysql --version 2>&1
echo "=== firewall (should be off) ==="
systemctl is-active firewalld 2>&1
getenforce 2>&1
} > /root/lamp.txt 2>&1
