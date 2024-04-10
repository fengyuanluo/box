#!/bin/bash

# 默认设置
DEFAULT_VERSION="0.52.0"
DEFAULT_ARCH="amd64"
FRPC_CONFIG_DIR="/etc/frp"
FRPC_BIN="/usr/bin/frpc"
FRPC_SERVICE="/etc/systemd/system/frpc.service"

prompt_for_input() {
    # 用户输入架构
    read -p "请选择架构 ($DEFAULT_ARCH 为默认): [amd64/arm/arm64]: " ARCH
    ARCH=${ARCH:-$DEFAULT_ARCH}

    # 用户输入版本
    read -p "请输入frpc的版本 ($DEFAULT_VERSION 为默认): " VERSION
    VERSION=${VERSION:-$DEFAULT_VERSION}
}

# 确定配置文件名称
determine_config_file_format() {
    if [[ "$(printf '%s\n' "0.52.0" "$VERSION" | sort -V | head -n1)" == "0.52.0" ]]; then
        FRPC_CONFIG_FILE="$FRPC_CONFIG_DIR/frpc.toml"
    else
        FRPC_CONFIG_FILE="$FRPC_CONFIG_DIR/frpc.ini"
    fi
}

# 安装函数
install_frpc() {
    # 下载并安装frpc
    wget "https://github.com/fatedier/frp/releases/download/v${VERSION}/frp_${VERSION}_linux_${ARCH}.tar.gz"
    tar zxvf "frp_${VERSION}_linux_${ARCH}.tar.gz"
    cp "frp_${VERSION}_linux_${ARCH}/frpc" $FRPC_BIN
    chmod +x $FRPC_BIN
    
    # 创建配置文件目录
    mkdir -p $FRPC_CONFIG_DIR
    
    # 根据版本号创建配置文件
    determine_config_file_format

    # 创建基本的配置文件
    if [[ $FRPC_CONFIG_FILE == *.toml ]]; then
        cat > $FRPC_CONFIG_FILE << EOF
# frpc.toml
[common]
server_addr = "example.com"
server_port = 7000
EOF
    else
        cat > $FRPC_CONFIG_FILE << EOF
# frpc.ini
[common]
server_addr = example.com
server_port = 7000
EOF
    fi
    
    # 创建系统服务
    cat > $FRPC_SERVICE << EOF
[Unit]
Description=Frp Client Service
After=network.target

[Service]
Type=simple
User=nobody
ExecStart=${FRPC_BIN} -c ${FRPC_CONFIG_FILE}
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    # 启动并使守护进程生效
    systemctl enable frpc
    systemctl start frpc

    echo "frpc 安装并启动成功。配置文件位于 ${FRPC_CONFIG_FILE}"
}

# 卸载函数
uninstall_frpc() {
    # 停止服务并禁用
    systemctl stop frpc
    systemctl disable frpc

    # 删除服务文件
    rm -f $FRPC_SERVICE
    systemctl daemon-reload
    
    # 删除frpc二进制文件和配置文件
    rm -f $FRPC_BIN
    rm -rf $FRPC_CONFIG_DIR

    echo "frpc 卸载成功。"
}

# 显示安装/卸载菜单
echo "欢迎使用 frpc 安装/卸载脚本"
echo "1. 安装 frpc"
echo "2. 卸载 frpc"
read -p "请选择操作 [1-2]: " operation

case "$operation" in
    1)
        prompt_for_input
        install_frpc
        ;;
    2)
        uninstall_frpc
        ;;
    *)
        echo "选择了无效的操作。"
        exit 1
        ;;
esac