#!/bin/bash

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
  echo "请以root权限运行该脚本"
  exit 1
fi

# 获取所有网络接口
get_interfaces() {
  ip -o link show | awk -F': ' '{print $2}'
}

# 安装dante
install_dante() {
  # 更新包列表并安装dante
  apt-get update
  apt-get install -y dante-server

  # 列出所有网络接口供用户选择
  echo "可用的网络接口:"
  interfaces=$(get_interfaces)
  select interface in $interfaces; do
    if [ -n "$interface" ]; then
      echo "你选择了接口: $interface"
      break
    else
      echo "无效的选择，请重新选择"
    fi
  done

  # 让用户输入端口号，或随机生成一个端口号
  read -p "请输入端口号（按Enter键跳过随机生成）: " PORT
  if [ -z "$PORT" ]; then
    PORT=$((RANDOM%64511+1024))
  fi

  # 配置文件路径
  CONFIG_FILE="/etc/danted.conf"

  # 创建dante配置文件
  cat <<EOL > $CONFIG_FILE
logoutput: stderr

internal: 0.0.0.0 port = $PORT
external: $interface

method: none

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: error
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: error
}
EOL

  # 重启dante服务
  systemctl restart danted

  # 打印代理信息
  echo "SOCKS5代理已创建"
  echo "IP地址: $(hostname -I | awk '{print $1}')"
  echo "端口号: $PORT"
}

# 卸载dante
uninstall_dante() {
  apt-get remove --purge -y dante-server
  rm -f /etc/danted.conf
  echo "Dante已卸载，并删除了配置文件"
}

# 主菜单
main_menu() {
  echo "请选择操作:"
  echo "1) 安装Dante"
  echo "2) 卸载Dante"
  echo "3) 退出"
  read -p "请输入选项(1/2/3): " choice

  case $choice in
    1)
      install_dante
      ;;
    2)
      uninstall_dante
      ;;
    3)
      exit 0
      ;;
    *)
      echo "无效的选项，请重新选择"
      main_menu
      ;;
  esac
}

# 运行主菜单
main_menu