#!/bin/bash

# 获取系统上所有磁盘列表
echo "检测到的磁盘列表:"
lsblk -d -n -p -o NAME,SIZE

# 让用户选择磁盘
read -p "请输入要分区的磁盘（例如 /dev/sda）: " DISK
if [ ! -e "$DISK" ]; then
    echo "错误: 磁盘 $DISK 不存在，请重新运行脚本。"
    exit 1
fi

# 获取用户选择的文件系统
echo "支持的文件系统类型: ext4, xfs, ntfs"
read -p "请输入你选择的文件系统类型: " FS_TYPE

# 检查文件系统类型是否支持
if ! [[ "$FS_TYPE" =~ ^(ext4|xfs|ntfs)$ ]]; then
    echo "错误: 不支持的文件系统类型。"
    exit 1
fi

# 获取用户选择的分区数量
read -p "请输入要创建的分区数量（1-4）: " NUM_PARTS
if ! [[ "$NUM_PARTS" =~ ^[1-4]$ ]]; then
    echo "错误: 只能输入1到4的数字。"
    exit 1
fi

# 开始分区
for (( i=1; i<=$NUM_PARTS; i++ ))
do
    # 可以添加更多的用户输入步骤，来定义每个分区的大小
    echo "正在创建分区 $i ..."
    # 注意，这里简化了分区过程，实际应用中可能需要更复杂的方式来处理分区大小
    # 这里我们只是简单地创建等大小分区，且没有错误处理
    echo -e "n\np\n\n\n\nw" | fdisk $DISK
    # 为了确保分区表正确同步，等待几秒
    sleep 5
done

# 获取新创建的分区名
PARTITIONS=$(fdisk -l $DISK | grep "^$DISK" | awk '{print $1}')
echo "创建的分区："
echo "$PARTITIONS"

# 格式化每个新创建的分区
for PARTITION in $PARTITIONS
do
    echo "正在格式化分区 $PARTITION ..."
    mkfs -t $FS_TYPE $PARTITION
done

# 挂载分区（用户可以添加自定义挂载点和确认步骤）
for PARTITION in $PARTITIONS
do
    MOUNT_POINT="/mnt$(echo $PARTITION | grep -o -E '[^/]+$')"
    mkdir -p $MOUNT_POINT
    mount $PARTITION $MOUNT_POINT
    # 添加到fstab以实现开机自动挂载
    echo "$PARTITION  $MOUNT_POINT  $FS_TYPE  defaults  0  0" | tee -a /etc/fstab
done

# 显示磁盘和挂载情况
df -h
