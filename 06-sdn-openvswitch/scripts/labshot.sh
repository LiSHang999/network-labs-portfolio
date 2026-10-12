#!/bin/bash
# ============================================================
# 实验3.1  Open vSwitch 的安装和配置
# 全流程真实执行 + 逐步真实截图（在 Guest :0 桌面的 xterm 中运行）
# ============================================================
export DISPLAY=:0
export XAUTHORITY=/home/ubuntu/.Xauthority
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

SHOT=/tmp/shots
rm -rf "$SHOT"; mkdir -p "$SHOT"
touch /tmp/labshot.running
rm -f /tmp/labshot.done

G=$'\e[1;32m'; B=$'\e[1;34m'; Y=$'\e[1;33m'; C=$'\e[1;36m'; N=$'\e[0m'
H=ubuntu-C241
P(){ printf "%s" "$(pwd | sed 's|/home/ubuntu|~|')"; }

step(){ clear; printf "%s\n\n" "${Y}========== $* ==========${N}"; }
say(){
  printf "${G}root@${H}${N}:${B}%s${N}# %s\n" "$(P)" "$1"
}
run(){ say "$1"; eval "$1"; echo; }
shot(){ sleep 1.5; import -window root "$SHOT/$1.png" 2>/dev/null; printf "  ${C}[截图 $1]${N}\n"; }

echo -e "${Y}实验3.1  Open vSwitch 的安装和配置${N}"
echo -e "${Y}==================== (1) 安装 Open vSwitch ====================${N}"
sleep 2

####################################################################
step "① 查看主机 IP 地址"
cd /home/ubuntu
run "ifconfig"
shot 01-ifconfig

####################################################################
step "② 查看当前系统内核版本"
run "uname -a"
run "uname -r"
shot 02-kernel

####################################################################
step "③ 下载 openvswitch-2.14.1.tar.gz"
cd /home/ubuntu
run "wget http://openvswitch.org/releases/openvswitch-2.14.1.tar.gz"
run "ls"
shot 03-wget

####################################################################
step "④ 创建新目录 lab，并将压缩文件移动到此目录下"
run "mkdir lab"
run "ls"
run "mv openvswitch-2.14.1.tar.gz /home/ubuntu/lab/"
run "ls"
shot 04-mkdir-lab

####################################################################
step "⑤ 在 lab 文件夹中，解压 openvswitch-2.14.1.tar.gz 文件"
run "cd lab/"
run "ls"
run "tar -zxvf openvswitch-2.14.1.tar.gz"
shot 05-untar

####################################################################
step "⑥ 进入 openvswitch-2.14.1 目录，查看内核源码编译目录"
run "cd /home/ubuntu/lab/openvswitch-2.14.1"
run "ls"
run "ls /lib/modules/"
shot 06-lib-modules

####################################################################
step "⑦ 生成 Makefile 文件"
say "./configure --with-linux=/lib/modules/$(uname -r)/build"
( sleep 8; shot 07a-configure-running ) &
./configure --with-linux=/lib/modules/$(uname -r)/build
wait
shot 07b-configure-done

####################################################################
step "⑧ 编译、安装 Open vSwitch"
say "make -j2"
( sleep 10; shot 08a-make-running ) &
make -j2
wait
shot 08b-make-done
run "make install"
shot 09-make-install

echo -e "${Y}==================== (2) 配置 Open vSwitch ====================${N}"
sleep 2

####################################################################
step "① 加载 Open vSwitch 内核模块 openvswitch.ko"
cd /home/ubuntu/lab/openvswitch-2.14.1
run "insmod ./datapath/linux/openvswitch.ko"
shot 10-insmod

####################################################################
step "② 创建 Open vSwitch 配置文件和数据库 conf.db"
run "mkdir -p /usr/local/etc/openvswitch/"
run "ovsdb-tool create /usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema"
run "ls -l /usr/local/etc/openvswitch/"
shot 11-create-confdb

####################################################################
step "③ 启动 OVSDB"
run "mkdir -p /usr/local/var/run/openvswitch"
say "ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --private-key=db:Open_vSwitch,SSL,private_key --certificate=db:Open_vSwitch,SSL,certificate --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert --pidfile --detach"
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
             --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
             --private-key=db:Open_vSwitch,SSL,private_key \
             --certificate=db:Open_vSwitch,SSL,certificate \
             --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
             --pidfile --detach
sleep 3
shot 12-ovsdb-server

####################################################################
step "④ 查看 OVSDB 是否启动成功"
run "ps -ef | grep ovsdb-server | grep -v grep"
shot 13-ps-ovsdb

####################################################################
step "⑤ 初始化数据库"
run "ovs-vsctl --no-wait init"
shot 14-init-db

####################################################################
step "⑥ 启动 Open vSwitch 守护进程"
run "ovs-vswitchd --pidfile --detach"
sleep 3
shot 15-ovs-vswitchd

####################################################################
step "⑦ 查看当前 OVS 进程"
run "ps -ef | grep ovs | grep -v grep"
shot 16-ps-ovs

####################################################################
step "⑧ 查看当前 OVS 的版本信息"
run "ovs-vsctl --version"
shot 17-ovs-version

####################################################################
step "附加：查看 OVS 桥接与数据库状态"
run "ovs-vsctl show"
run "ovs-vsctl list-br"
shot 18-ovs-show

####################################################################
clear
echo -e "${G}=========================================${N}"
echo -e "${G}  实验3.1 全部步骤执行完毕${N}"
echo -e "${G}=========================================${N}"
echo
echo -e "${Y}版本核对：${N}"
ovs-vsctl --version
echo
ls -l "$SHOT" | tail -25
sleep 3
shot 19-summary
import -window root "$SHOT/19-summary.png" 2>/dev/null

rm -f /tmp/labshot.running
echo "DONE" > /tmp/labshot.done
sleep 3600
