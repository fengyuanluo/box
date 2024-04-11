#! /bin/bash
# By 洛风缘
#https://github.com/fengyuanluo/box

#彩色
red(){
    echo -e "\033[31m\033[01m$1\033[0m"
}
green(){
    echo -e "\033[32m\033[01m$1\033[0m"
}
yellow(){
    echo -e "\033[33m\033[01m$1\033[0m"
}
blue(){
    echo -e "\033[34m\033[01m$1\033[0m"
}

#主菜单
function start_menu(){
    clear
    red "洛风缘的懒人工具箱" 
    green " FROM: https://github.com/fengyuanluo/box "
    green " USE:  wget -O box.sh https://raw.githubusercontent.com/fengyuanluo/box/main/box.sh && chmod +x box.sh && clear && ./box.sh "
    yellow " =================================================="
    green " 1. 系统工具"
    green " 2. 测试工具"
    green " 3. 应用程序"
    yellow " =================================================="
    green " 0. 退出脚本"
    echo
    read -p "请输入数字:" menuNumberInput
    case "$menuNumberInput" in
        1 )
           system_tools
	;;
        2 )
           test_tools
	;;
        3 )
           applications
	;;
        0 )
            exit 1
        ;;
        * )
            clear
            red "请输入正确数字 !"
            start_menu
        ;;
    esac
}

function system_tools(){
    clear
    red " 系统工具菜单"
    green " 1. IPV.SH ipv4/6优先级调整一键脚本·下载"
    green " 2. IPT.SH iptable一键脚本"
    green " 3. Rclone&Fclone·下载"
    green " 4. ChangeSource Linux换源脚本·下载"
    green " 5. Besttrace 路由追踪·下载"
    green " 6. NEZHA.SH哪吒面板/探针"
    yellow " --------------------------------------------------"
    green " 11. 获取本机IP"
    green " 12. 安装最新BBR内核·使用YUM·仅支持CentOS"
    green " 13. 启动BBR FQ算法"
    green " 14. 系统网络配置优化"
    green " 15. Git 新版 安装·仅支持CentOS"
    green " 16. 宝塔面板 自动磁盘挂载工具"
    green " 17. BBR一键管理脚本"
    green " 18. SWAP一键安装/卸载脚本"
    green " 19. F2B一键安装脚本"
	green " 20. 磁盘分区管理工具"
    yellow " --------------------------------------------------"
    green " 0. 返回上级菜单"
    echo
    read -p "请输入数字:" menuNumberInput
    case "$menuNumberInput" in
        1 )
           ipvsh
	;;
        2 )
           iptsh
	;;
        3 )
           clonesh
	;;
        4 )
           cssh
	;;
	5 )
           gettrace
	;;
	6 )
           nezha
	;;
	11 )
           getip
	;;
	12 )
           bbrnew
	;;
	13 )
           bbrfq
	;;
	14 )
           system-best
	;;
	15 )
           yumgitsh
	;;
	16 )
           btdisk
	;;
	17 )
           tcpsh
	;;
	18 )
           swapsh
	;;
	19 )
           f2bsh
	;;
	20 )
			disk-partition
	;;
        0 )
            start_menu
        ;;
        * )
            clear
            red "请输入正确数字 !"
            system_tools
        ;;
    esac
}
function test_tools(){
    clear
    red " 测试工具菜单"
    green " 1. Speedtest-Linux 下载"
    green " 2. Superbench 综合测试"
    green " 3. MT.SH 流媒体解锁测试"
    green " 4. Lemonbench 综合测试"
    green " 5. UNIXbench 综合测试"
    green " 6. 三网Speedtest测速"
    green " 7. Memorytest 内存压力测试"
    green " 8. Route-trace 路由追踪测试"
    green " 9. YABS LINUX综合测试"
    green " 10. Disk Test 硬盘&系统综合测试"
    green " 11. TubeCheck Google/Youtube CDN分配节点测试"
    green " 12. RegionRestrictionCheck 流媒体解锁测试"
	green " 13. 磁盘性能测试"
    yellow " --------------------------------------------------"
    green " 0. 返回上级菜单"
    echo
    read -p "请输入数字:" menuNumberInput
    case "$menuNumberInput" in
        1 )
           speedtest-linux
	;;
	2 )
           superbench
	;;
	3 )
           mtsh
	;;
	4 )
           Lemonbench
	;;
	5 )
           UNIXbench
	;;
	6 )
           3speed
	;;
	7 )
           memorytest
	;;
	8 )
           rtsh
	;;
	9 )
           yabssh
	;;
	10 )
           disktestsh
	;;
	11 )
	   tubecheck
	;;
	12 )
	   RegionRestrictionCheck
	;;
	13 )
   disk-test
	;;
        0 )
            start_menu
        ;;
        * )
            clear
            red "请输入正确数字 !"
            test_tools
        ;;
    esac
}

function applications(){
    clear
    red " 应用程序菜单"
    green " 1. MTP&TLS 一键脚本"
    green " 2. Rclone官方一键安装脚本" 
    green " 3. Aria2 最强安装与管理脚本"
	green " 4. frpc 客户端管理"
	green " 5. frps 客户端管理"
    yellow " --------------------------------------------------"
    green " 0. 返回上级菜单"
    echo
    read -p "请输入数字:" menuNumberInput
    case "$menuNumberInput" in
        1 )
           mtp
	;;
	2 )
           rc
	;;
        3 )
           aria
	;;
	4 )
		   frpc-manage
	;;
	5 )
		   frps-manage
	;;
        0 )
            start_menu
        ;;
        * )
            clear
            red "请输入正确数字 !"
            applications
        ;;
    esac
}

#IPV.SH ipv4/6优先级调整一键脚本·下载
function ipvsh(){
wget -O "/root/ipv.sh" "https://raw.githubusercontent.com/BlueSkyXN/ChangeSource/master/ipv.sh" --no-check-certificate -T 30 -t 5 -d
chmod +x "/root/ipv.sh"
chmod 777 "/root/ipv.sh"
blue "下载完成"
blue "输入 bash /root/ipv.sh 来运行"
}

#IPT.SH iptable一键脚本·下载
function iptsh(){
wget -O "/root/ipt.sh" "https://raw.githubusercontent.com/BlueSkyXN/ChangeSource/master/ipt.sh" --no-check-certificate -T 30 -t 5 -d
chmod +x "/root/ipt.sh"
chmod 777 "/root/ipt.sh"
blue "下载完成"
blue "输入 bash /root/ipt.sh 来运行"
}

#Rclone&Fclone·下载
function clonesh(){
wget -O "/root/clone.sh" "https://raw.githubusercontent.com/BlueSkyXN/ChangeSource/master/clone.sh" --no-check-certificate -T 30 -t 5 -d
chmod +x "/root/clone.sh"
chmod 777 "/root/clone.sh"
blue "下载完成"
blue "输入 bash /root/clone.sh 来运行"
}

#ChangeSource Linux换源脚本·下载
function cssh(){
wget -O "/root/changesource.sh" "https://raw.githubusercontent.com/BlueSkyXN/ChangeSource/master/changesource.sh" --no-check-certificate -T 30 -t 5 -d
chmod +x "/root/changesource.sh"
chmod 777 "/root/changesource.sh"
blue "下载完成"
blue "输入 bash /root/changesource.sh 来运行"
}

#Besttrace 路由追踪·下载
function gettrace(){
wget -O "/root/besttrace.sh" "https://raw.githubusercontent.com/BlueSkyXN/ChangeSource/master/besttrace.sh" --no-check-certificate -T 30 -t 5 -d
chmod +x "/root/besttrace.sh"
chmod 777 "/root/besttrace.sh"
blue "下载完成"
blue "输入 bash /root/besttrace.sh 来运行"
}

#NEZHA.SH哪吒面板/探针·下载
function nezha(){
wget -O "/root/nezha.sh" "https://raw.githubusercontent.com/BlueSkyXN/SKY-BOX/main/scripts/nezha.sh" --no-check-certificate -T 30 -t 5 -d
chmod +x "/root/nezha.sh"
chmod 777 "/root/nezha.sh"
blue "下载完成"
blue "输入 bash /root/nezha.sh 来运行"
}

#获取本机IP
function getip(){
red "本机IP如下:"
echo
green " IPv4:"
echo $(curl ip.gs)
echo
green " IPv6:"
echo $(curl ip6.toos.info)
echo
}

#BBR内核安装脚本
function bbrnew(){
wget --no-check-certificate https://github.com/teddysun/across/raw/master/bbr.sh && chmod +x bbr.sh && ./bbr.sh
}

#开启BBR FQ算法
function bbrfq(){
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
sysctl -p
}

#System Configure
function system-best(){
cat > '/etc/sysctl.d/10.0.0.0.conf' <<- EOF
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_rmem = 1024 4096 16384
net.ipv4.udp_mem = 1024 4096 16384
net.ipv4.tcp_wmem = 1024 4096 16384
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_mtu_probing = 1

EOF
sysctl --load='/etc/sysctl.d/10.0.0.0.conf'
sysctl --system
}

#Git 新版 安装·仅支持CentOS
function yumgitsh(){
yum remove -y git
rm -rf /usr/bin/git
yum install -y curl-devel expat-devel gettext-devel openssl-devel zlib-devel
yum install -y gcc perl-ExtUtils-MakeMaker
wget https://www.kernel.org/pub/software/scm/git/git-2.36.1.tar.gz
tar -zxvf git-2.36.1.tar.gz
cd git-2.36.1 && make prefix=/usr/local/git all
make prefix=/usr/local/git install
echo "export PATH=$PATH:/usr/local/git/bin" >> /etc/profile
source /etc/profile
git --version
}

#宝塔面板磁盘挂载
function btdisk(){
wget -O bt_disk_mount.sh https://raw.githubusercontent.com/BlueSkyXN/SKY-BOX/main/scripts/bt_disk_mount.sh && bash bt_disk_mount.sh
}

#BBR一键管理脚本
function tcpsh(){
wget --no-check-certificate https://github.com/teddysun/across/raw/master/bbr.sh
chmod +x bbr.sh
./bbr.sh
}

#SWAP一键脚本
function swapsh(){
wget -N --no-check-certificate https://raw.githubusercontent.com/BlueSkyXN/SWAP/master/swapfile.sh && bash swapfile.sh
}

#F2B一键安装脚本
function f2bsh(){
curl https://raw.githubusercontent.com/BlueSkyXN/SKY-BOX/main/scripts/f2b.sh | bash
}

#Speedtest-Linux 下载
function speedtest-linux(){
wget -qO- bench.Sh||curl -sL bench.Sh|bash
}

#Superbench 综合测试
function superbench(){
wget -qO- git.io/superbench.sh|bash
}

#MT.SH 流媒体解锁测试
function mtsh(){
wget -qO- git.io/mt.sh|bash
}

#Lemonbench 综合测试
function Lemonbench(){
curl -fsL https://ilemonra.in/LemonBenchIntl | bash -s fast
}

#UNIXbench 综合测试
function UNIXbench(){
wget -qO- bench.Sh|bash
}

#三网Speedtest测速
function 3speed(){
wget -qO- git.io/superspeed.sh|bash
}

#Memorytest 内存压力测试
function memorytest(){
wget --no-check-certificate https://github.com/BlueSkyXN/MemoryTestingTool/raw/master/MemoryTestingTool.sh
chmod +x MemoryTestingTool.sh
./MemoryTestingTool.sh
}

#Route-trace 路由追踪测试
function rtsh(){
wget --no-check-certificate --no-cache -O /root/Routrace.sh https://raw.githubusercontent.com/BlueSkyXN/SKY-BOX/main/scripts/trace-ip.sh
chmod +x /root/Routrace.sh
/root/Routrace.sh
}

#YABS LINUX综合测试
function yabssh(){
wget --no-check-certificate --no-cache -O /root/yabs.sh https://raw.githubusercontent.com/599769749/test/main/yabs.sh && chmod +x /root/yabs.sh && /root/yabs.sh
}

#Disk Test 硬盘&系统综合测试
function disktestsh(){
curl -fsL https://disktestcn.cloudcone.com/ | bash
}

#TubeCheck Google/Youtube CDN分配节点测试
function tubecheck(){
wget --no-check-certificate https://rawthencutwp.tk/TubeCheck.sh && bash TubeCheck.sh
}

#RegionRestrictionCheck 流媒体解锁测试
function RegionRestrictionCheck(){
wget --no-check-certificate https://raw.githubusercontent.com/BlueSkyXN/SKY-BOX/main/scripts/RegionRestrictionCheck.sh
chmod 777 RegionRestrictionCheck.sh
./RegionRestrictionCheck.sh
}

#MTP&TLS 一键脚本
function mtp(){
curl -fsSL https://multipools.mtp-node.net/mtp/install.sh | bash -s mtp
}

#Rclone官方一键脚本
function rc(){
curl https://rclone.org/install.sh | sudo bash
}

#Aria2脚本
function aria(){
wget -N --no-check-certificate https://raw.githubusercontent.com/BlueSkyXN/TURN/main/Aria2.sh && chmod +x Aria2.sh && ./Aria2.sh
}

function disk-partition(){
    wget -O "/root/disk-partition.sh" "https://raw.githubusercontent.com/fengyuanluo/box/main/disk-partition.sh" --no-check-certificate -T 30 -t 5 -d
    chmod +x "/root/disk-partition.sh"
    chmod 777 "/root/disk-partition.sh"
    blue "下载完成"
	bash /root/disk-partition.sh
#   blue "输入 bash /root/disk-partition.sh 来运行"
}

function disk-test(){
    wget -O "/root/disk-test.sh" "https://raw.githubusercontent.com/fengyuanluo/box/main/disk-test.sh" --no-check-certificate -T 30 -t 5 -d
    chmod +x "/root/disk-test.sh"
    "/root/disk-test.sh"
    rm -f "/root/disk-test.sh"
}

function frpc-manage(){
    wget -O "/root/frpc.sh" "https://raw.githubusercontent.com/fengyuanluo/box/main/frpc.sh" --no-check-certificate -T 30 -t 5 -d
    chmod +x "/root/frpc.sh"
    "/root/frpc.sh"
    rm -f "/root/frpc.sh"
}

function frps-manage(){
    wget -O "/root/frps.sh" "https://raw.githubusercontent.com/fengyuanluo/box/main/frps.sh" --no-check-certificate -T 30 -t 5 -d
    chmod +x "/root/frps.sh"
    "/root/frps.sh"
    rm -f "/root/frps.sh"
}

start_menu