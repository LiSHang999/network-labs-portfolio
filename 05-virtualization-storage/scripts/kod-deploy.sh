#!/bin/bash
{
echo "=== extract kodbox ==="
mkdir -p /var/www/html/kodbox
cd /var/www/html/kodbox
unzip -o -q /root/kodbox.1.69.zip 2>&1
chmod -R 777 /var/www/html/kodbox
ls -la /var/www/html/kodbox | head -20
echo "=== create database ==="
mysql -e "CREATE DATABASE IF NOT EXISTS kodbox DEFAULT CHARACTER SET utf8mb4; CREATE USER IF NOT EXISTS 'kodbox'@'localhost' IDENTIFIED BY 'Kodbox@123'; GRANT ALL PRIVILEGES ON kodbox.* TO 'kodbox'@'localhost'; FLUSH PRIVILEGES;" 2>&1
echo "mysql exit: $?"
mysql -e "SHOW DATABASES;" 2>&1
echo "=== httpd php module ==="
httpd -M 2>/dev/null | grep -i php || echo "no mod_php loaded"
echo "=== php-fpm status ==="
systemctl is-active php-fpm 2>&1
echo "=== phpinfo test ==="
echo '<?php phpinfo(); ?>' > /var/www/html/phpinfo.php
curl -s http://localhost/phpinfo.php | grep -o 'PHP Version [0-9.]*' | head -1
echo "=== kodbox http status ==="
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/kodbox/
} > /root/kod.txt 2>&1
