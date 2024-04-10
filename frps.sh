#!/bin/bash

# 默认值设置
DEFAULT_FRP_VERSION="0.52.0"
DEFAULT_ARCH="amd64"
DEFAULT_BIND_PORT="7000"
DEFAULT_ENABLE_DASHBOARD="yes"
DEFAULT_DASHBOARD_PORT="7500"
DEFAULT_DASHBOARD_USER="admin"
DEFAULT_DASHBOARD_PWD="admin"
INSTALL_DIR="/usr/local/frp"
DEFAULT_TOKEN="12345678"
DEFAULT_VHOST_HTTP_PORT="80"
DEFAULT_VHOST_HTTPS_PORT="443"

actions() {
    # 安装或者卸载 frps 服务
    case $1 in
        install)
            echo "Starting the installation process..."
            # 请在这里添加安装逻辑
            # ...

            

# 环境检查
if [[ $(id -u) -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
fi

# 获取用户输入的 FRP 版本和架构，提供默认值
read -p "Enter the version of FRP you want to install [$DEFAULT_FRP_VERSION]: " FRP_VERSION
FRP_VERSION="${FRP_VERSION:-$DEFAULT_FRP_VERSION}"

read -p "Enter the architecture of your system [$DEFAULT_ARCH]: " FRP_ARCH
FRP_ARCH="${FRP_ARCH:-$DEFAULT_ARCH}"

# 获取用户输入的配置细节，提供默认值
read -p "Enter the port you want frps to bind [$DEFAULT_BIND_PORT]: " BIND_PORT
BIND_PORT="${BIND_PORT:-$DEFAULT_BIND_PORT}"

read -p "Enter your authentication token [$DEFAULT_TOKEN]: " TOKEN
TOKEN="${TOKEN:-$DEFAULT_TOKEN}"

    # 获取vhost_http_port和vhost_https_port的配置细节，提供默认值
read -p "Enter the HTTP port for virtual hosting [$DEFAULT_VHOST_HTTP_PORT]: " VHOST_HTTP_PORT
VHOST_HTTP_PORT="${VHOST_HTTP_PORT:-$DEFAULT_VHOST_HTTP_PORT}"

read -p "Enter the HTTPS port for virtual hosting [$DEFAULT_VHOST_HTTPS_PORT]: " VHOST_HTTPS_PORT
VHOST_HTTPS_PORT="${VHOST_HTTPS_PORT:-$DEFAULT_VHOST_HTTPS_PORT}"


read -p "Do you want to enable dashboard? (yes/no) [$DEFAULT_ENABLE_DASHBOARD]: " ENABLE_DASHBOARD
ENABLE_DASHBOARD="${ENABLE_DASHBOARD:-$DEFAULT_ENABLE_DASHBOARD}"

if [ "$ENABLE_DASHBOARD" == "yes" ]; then
    read -p "Dashboard bind port [$DEFAULT_DASHBOARD_PORT]: " DASHBOARD_PORT
    DASHBOARD_PORT="${DASHBOARD_PORT:-$DEFAULT_DASHBOARD_PORT}"

    read -p "Dashboard user [$DEFAULT_DASHBOARD_USER]: " DASHBOARD_USER
    DASHBOARD_USER="${DASHBOARD_USER:-$DEFAULT_DASHBOARD_USER}"

    read -p "Dashboard password [$DEFAULT_DASHBOARD_PWD]: " DASHBOARD_PWD
    DASHBOARD_PWD="${DASHBOARD_PWD:-$DEFAULT_DASHBOARD_PWD}"
fi

# 版本比较以确定配置文件类型
if [[ $(awk 'BEGIN {print ("'${FRP_VERSION}'" >= "0.52.0")}') == 1 ]]; then
    CONFIG_FILE_TYPE="toml"
else
    CONFIG_FILE_TYPE="ini"
fi

# 设置 FRP 的下载链接
FRP_DOWNLOAD_URL="https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_${FRP_ARCH}.tar.gz"
# 设置安装目录
INSTALL_DIR="/usr/local/frp"

# 安装 wget 和 tar，如果没有的话
if ! command -v wget &> /dev/null || ! command -v tar &> /dev/null; then
    echo "Installing wget and tar packages..."
    apt-get update && apt-get install -y wget tar
fi

# 下载解压 FRP
mkdir -p ${INSTALL_DIR}
wget ${FRP_DOWNLOAD_URL} -O frp.tar.gz
tar zxvf frp.tar.gz -C ${INSTALL_DIR} --strip-components=1
rm frp.tar.gz

# 根据使用的配置文件类型，并依据用户输入创建 FRP 配置文件
CONFIG_FILE="${INSTALL_DIR}/frps.${CONFIG_FILE_TYPE}"
if [ "${CONFIG_FILE_TYPE}" == "toml" ]; then
    cat > ${CONFIG_FILE} << EOF
[common]
bind_addr = 0.0.0.0
bind_port = ${BIND_PORT}
token = ${TOKEN}
EOF
    if [ "$ENABLE_DASHBOARD" == "yes" ]; then
        cat >> ${CONFIG_FILE} << EOF
dashboard_port = ${DASHBOARD_PORT}
dashboard_user = "${DASHBOARD_USER}"
dashboard_pwd = "${DASHBOARD_PWD}"
vhost_http_port = ${VHOST_HTTP_PORT}
vhost_https_port = ${VHOST_HTTPS_PORT}
EOF
    fi
else # ini
    cat > ${CONFIG_FILE} << EOF
[common]
bind_port = ${BIND_PORT}
EOF
    if [ "$ENABLE_DASHBOARD" == "yes" ]; then
        cat >> ${CONFIG_FILE} << EOF
dashboard_port = ${DASHBOARD_PORT}
dashboard_user = ${DASHBOARD_USER}
dashboard_pwd = ${DASHBOARD_PWD}
EOF
    fi
fi

# 创建 systemd 服务文件
cat >/etc/systemd/system/frps.service <<EOF
[Unit]
Description=frps (Fast Reverse Proxy)
After=network.target

[Service]
Type=simple
User=root
ExecStart=${INSTALL_DIR}/frps -c ${CONFIG_FILE}
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd，启用并启动 frps 服务
systemctl daemon-reload
systemctl enable frps
systemctl start frps

# 显示服务状态
systemctl status frps --no-pager

            echo "Installation Complete! FRP has been started and enabled on boot."
            ;;
        uninstall)
            echo "Starting the uninstallation process..."
            # 停止服务
            systemctl stop frps
            # 禁用服务
            systemctl disable frps
            # 删除服务文件
            rm -f /etc/systemd/system/frps.service
            systemctl daemon-reload
            # 删除安装目录
            rm -rf $INSTALL_DIR
            echo "Uninstallation complete. frps has been removed from your system."
            ;;
        *)
            echo "Invalid action. Please start the script again and choose 'install' or 'uninstall'."
            exit 1
            ;;
    esac
}

# 环境检查
if [[ $(id -u) -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
fi

# 提示用户选择操作
read -p "Do you want to 'install' or 'uninstall' frps? [install/uninstall]: " ACTION
ACTION="${ACTION,,}"  # 转换为小写

if [ "$ACTION" != "install" ] && [ "$ACTION" != "uninstall" ]; then
    echo "Invalid action selected. Exiting."
    exit 1
fi

if [ "$ACTION" == "uninstall" ]; then
    actions uninstall
    exit 0
fi

# 如果是安装，继续提示输入配置细节...
# ...

if [ "$ACTION" == "install" ]; then
    actions install
    exit 0
fi

