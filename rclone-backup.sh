#!/bin/bash

install_packages() {
    if ! command -v python3 &> /dev/null; then
        echo "Python3 is not installed. Installing..."
        sudo apt-get update
        sudo apt-get install -y python3
    fi

    if ! command -v rclone &> /dev/null; then
        echo "Rclone is not installed. Installing..."
        curl https://rclone.org/install.sh | sudo bash
    fi

    if ! command -v pip3 &> /dev/null; then
        echo "pip3 is not installed. Installing..."
        sudo apt-get install -y python3-pip
    fi

    if ! python3 -c "import requests" &> /dev/null; then
        echo "requests library is not installed. Installing..."
        sudo pip3 install requests
    fi
}

install_rclone_backup_scripts() {
    read -p "Enter the path to save the backup scripts: " script_path

    if [ ! -d "$script_path" ]; then
        echo "Creating directory $script_path..."
        mkdir -p "$script_path"
    fi

    echo "Downloading backup.py..."
    curl https://raw.githubusercontent.com/fengyuanluo/box/main/rclone%E5%A4%87%E4%BB%BD/backup.py -o "$script_path/backup.py"
    chmod +x $script_path/backup.py
    echo "Downloading manage.py..."
    curl https://raw.githubusercontent.com/fengyuanluo/box/main/rclone%E5%A4%87%E4%BB%BD/manage.py -o "$script_path/manage.py"
    chmod +x $script_path/manage.py
}

set_cron_job() {
    read -p "Enter the interval (in hours) to run backup.py: " interval

    cron_entry="0 */$interval * * * $script_path/backup.py"
    (crontab -l | grep -v -F "$script_path/backup.py"; echo "$cron_entry") | crontab -
    echo "Cron job set to run backup.py every $interval hour(s)."
}

run_manage_py() {
    python3 "$script_path/manage.py"
}

uninstall_rclone_backup() {
    read -p "Enter the path where the backup scripts are located: " script_path

    rm -rf "$script_path"
    echo "Backup scripts deleted."

    read -p "Do you want to uninstall Python3, Rclone, and pip3? (y/n) " uninstall_packages
    if [ "$uninstall_packages" == "y" ]; then
        sudo apt-get remove -y python3 rclone python3-pip
        echo "Python3, Rclone, and pip3 uninstalled."
    fi
}

main() {
    while true; do
        echo "Menu:"
        echo "1. Install"
        echo "2. Uninstall"
        echo "3. Exit"
        read -p "Enter your choice (1-3): " choice

        case "$choice" in
            1)
                install_packages
                install_rclone_backup_scripts
                set_cron_job
                run_manage_py
                ;;
            2)
                uninstall_rclone_backup
                ;;
            3)
                exit 0
                ;;
            *)
                echo "Invalid choice. Please try again."
                ;;
        esac
    done
}

main
