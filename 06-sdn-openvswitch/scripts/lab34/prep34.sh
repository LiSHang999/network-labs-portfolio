#!/bin/bash
# 实验3.4 截图环境准备：关熄屏/锁屏、创建 shot34、在 :0 桌面开 xterm
set -u
export DISPLAY=:0
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

GSPID=$(pgrep -u ubuntu -f 'gnome-session-binary' | head -1)
XAUTH=$(tr '\0' '\n' < /proc/$GSPID/environ 2>/dev/null | sed -n 's/^XAUTHORITY=//p')
[ -n "$XAUTH" ] || XAUTH=/home/ubuntu/.Xauthority
echo "$XAUTH" > /tmp/xauth34
export XAUTHORITY="$XAUTH"
DBA=$(tr '\0' '\n' < /proc/$GSPID/environ 2>/dev/null | sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p')

su ubuntu -c "DISPLAY=:0 XAUTHORITY=$XAUTH DBUS_SESSION_BUS_ADDRESS='$DBA' gsettings set org.gnome.desktop.session idle-delay 0" >/dev/null 2>&1
su ubuntu -c "DISPLAY=:0 XAUTHORITY=$XAUTH DBUS_SESSION_BUS_ADDRESS='$DBA' gsettings set org.gnome.desktop.screensaver idle-activation-enabled false" >/dev/null 2>&1
su ubuntu -c "DISPLAY=:0 XAUTHORITY=$XAUTH DBUS_SESSION_BUS_ADDRESS='$DBA' gsettings set org.gnome.desktop.screensaver lock-enabled false" >/dev/null 2>&1
xset s off >/dev/null 2>&1
xset -dpms >/dev/null 2>&1
xset dpms force on >/dev/null 2>&1
for s in $(loginctl list-sessions --no-legend 2>/dev/null | awk '{print $1}'); do
    loginctl unlock-session "$s" >/dev/null 2>&1
done

mkdir -p /tmp/shots34
rm -f /tmp/shots34/*.png

pkill -f 'xterm -T LAB3.4' 2>/dev/null
sleep 1

cat > /usr/local/bin/shot34 <<'EOS'
#!/bin/bash
export DISPLAY=:0
export XAUTHORITY=$(cat /tmp/xauth34)
import -window root "$1"
EOS
chmod 755 /usr/local/bin/shot34

setsid nohup su ubuntu -c "DISPLAY=:0 XAUTHORITY=$XAUTH exec xterm -T LAB3.4 -fa 'AR PL UMing CN' -fs 13 -geometry 120x42+62+30 -bg black -fg white" >/dev/null 2>&1 </dev/null &
sleep 3
echo "PREP-OK XAUTH=$XAUTH"
