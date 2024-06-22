#!/bin/bash

# 颜色代码
red="\033[31m"
green="\033[32m"
yellow="\033[33m"
plain="\033[0m"

# 检查是否为Root
[[ $EUID -ne 0 ]] && echo -e "${red}错误: ${plain} 必须使用root权限运行脚本！\n" && exit 1

# 获取系统信息
cname=$(awk -F: '/model name/{name=$2} END{print name}' /proc/cpuinfo | sed 's/^[ \t]*//;s/[ \t]*$//')
cores=$(awk -F: '/model name/{core++} END{print core}' /proc/cpuinfo)
freq=$(awk -F'[ :]' '/cpu MHz/{print $4;exit}' /proc/cpuinfo)
tram=$(free -m | awk '/Mem/{ print $2}')
swap=$(free -m | awk '/Swap/{ print $2}')
up=$(awk '{a=$1/86400;b=($1%86400)/3600;c=($1%3600)/60} {printf("%d days, %d hour %d min\n",a,b,c)}' /proc/uptime)
opsy=$(hostnamectl | sed -n '1p')
arch=$(uname -m)
kern=$(uname -r)
disk_size=$(df -hPl | grep -wvE '\-|none|tmpfs|overlay|shmpnt' | awk '{print $2}' | xargs | sed 's/ /,/g')
tcpctrl=$(sysctl net.ipv4.tcp_congestion_control | awk -F ' ' '{print $3}')

# 打印系统信息
clear
println() {
    echo -e "\\n${green}$1${plain}\\n"
}

show_system_info() {
    println "硬件信息:"
    println " 处理器模型: $cname"
    println " 处理器内核数: $cores"
    println " 处理器频率: $freq MHz"
    println " 内存总数: $tram MB"
    println " 交换空间: $swap MB"
    println " 已运行时间: $up"
    println " 操作系统: $opsy"
    println " 系统架构: $arch"
    println " 内核版本: $kern"
    println " 磁盘总大小: $disk_size GB"
    println " TCP拥塞控制算法: $tcpctrl"
}

show_menu() {
    println "请选择分区操作:"
    echo -e " ${green}1)${plain} 查看当前分区情况"
    echo -e " ${green}2)${plain} 创建新分区"
    echo -e " ${green}3)${plain} 格式化分区"
    echo -e " ${green}4)${plain} 挂载分区"
    echo -e " ${green}5)${plain} 卸载分区"
    echo -e " ${green}6)${plain} 设置开机自动挂载"
    echo -e " ${green}7)${plain} 退出"
    read -p "请输入数字 [1-7]:" choose
}

# 显示系统信息
show_system_info

while true; do
    show_menu
    case "$choose" in
        1)
            fdisk -l | grep '^Disk'
            ;;
        2)
            println "请输入要创建分区的磁盘, 如 /dev/vda"
            read -p "磁盘: " disk
            fdisk $disk
            println "分区创建成功!"
            ;;
        3)
            println "请输入要格式化的分区, 如 /dev/vda1"
            read -p "分区: " part
            println "请选择文件系统类型:"
            echo -e " ${green}1)${plain} ext4"
            echo -e " ${green}2)${plain} xfs"
            read -p "请输入数字 [1-2]:" fs_type
            if [[ $fs_type == "1" ]]; then
                mkfs.ext4 $part
            elif [[ $fs_type == "2" ]]; then
                mkfs.xfs -f $part
            else
                println "输入错误, 请重试!"
            fi
            println "分区格式化成功!"
            ;;
        4)
            println "请输入要挂载的分区, 如 /dev/vda1"
            read -p "分区: " part
            println "请输入挂载点, 如 /mnt"
            read -p "挂载点: " mnt
            mkdir -p "$mnt"
            mount "$part" "$mnt"
            println "分区挂载成功!"
            ;;
        5)
            println "请输入要卸载的挂载点, 如 /mnt"
            read -p "挂载点: " mnt
            umount "$mnt"
            println "分区卸载成功!"
            ;;
        6)
            println "请输入要开机自动挂载的分区, 如 /dev/vda1"
            read -p "分区: " part
            println "请输入挂载点, 如 /mnt"
            read -p "挂载点: " mnt
            mkdir -p "$mnt"
            echo "$part $mnt $(blkid $part | awk '{print $3}' | sed 's/\"//g') defaults 0 0" >> /etc/fstab
            println "已设置开机自动挂载!"
            ;;
        7)
            exit 0
            ;;
        *)
            println "输入错误, 请重试!"
            ;;
    esac
done
