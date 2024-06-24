#!/bin/sh

# 获取系统架构
ARCH=$(uname -m)

# 根据系统架构下载对应的CloudflareSpeedTest包
case $ARCH in
    x86_64)
        wget https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.5/CloudflareST_linux_amd64.tar.gz -O /tmp/cfddns.tar.gz
        ;;
    aarch64)
        wget https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.5/CloudflareST_linux_arm64.tar.gz -O /tmp/cfddns.tar.gz
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# 解压下载的包
tar -zxf /tmp/cfddns.tar.gz -C /root/cfddns
rm /tmp/cfddns.tar.gz