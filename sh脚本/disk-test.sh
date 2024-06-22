#!/bin/bash

# 显示所有硬盘及其大小
echo "列出所有硬盘及其容量："
lsblk -o NAME,SIZE,TYPE | grep disk

# 获取全部硬盘列表
DISKS=$(lsblk -nd --output NAME | grep -E "^sd[a-z]+$")

# 如果没有硬盘，退出脚本
if [ -z "$DISKS" ]; then
    echo "没有找到任何硬盘设备。"
    exit 1
fi

# 用户选择硬盘
echo "请选择您要测试的硬盘设备："
select DISK_CHOICE in $DISKS; do
    if [ -n "$DISK_CHOICE" ]; then
        DISK="/dev/$DISK_CHOICE"
        echo "您选择了硬盘：$DISK"
        break
    else
        echo "无效的选择，请再试一次。"
    fi
done

# 测试文件的大小（1GB）
TEST_SIZE=$((1*1024*1024*1024))

# 临时测试文件的路径
TEMP_FILE=/tmp/test_disk_speed

# 获取用户输入的块大小
echo "请输入块大小（字节），多个大小请用空格分隔（例如 512 1024 4096 8192）："
read -a BLOCK_SIZES

echo "开始硬盘速度测试"

# 写入测试
for BLOCK_SIZE in "${BLOCK_SIZES[@]}"; do
    echo "使用 $BLOCK_SIZE 字节的块大小进行写入测试..."
    dd if=/dev/zero of=$TEMP_FILE bs=$BLOCK_SIZE count=$(($TEST_SIZE / $BLOCK_SIZE)) oflag=direct status=progress
    sync; sleep 1  # 清除缓存
done

# 确保测试文件存在
if [ ! -f $TEMP_FILE ]; then
    echo "测试文件未创建，读取测试将不会进行。"
    exit 1
fi

# 读取测试
for BLOCK_SIZE in "${BLOCK_SIZES[@]}"; do
    echo "使用 $BLOCK_SIZE 字节的块大小进行读取测试..."
    dd if=$TEMP_FILE of=/dev/null bs=$BLOCK_SIZE status=progress
    sync; sleep 1  # 清除缓存
done

# 清理临时文件
rm -f $TEMP_FILE

echo "硬盘速度测试完成"
