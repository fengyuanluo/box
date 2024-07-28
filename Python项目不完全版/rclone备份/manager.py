import os
import json
import subprocess
import datetime
import shutil
import requests

def load_tasks():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    tasks_json_path = os.path.join(script_dir, 'tasks.json')

    if os.path.exists(tasks_json_path):
        with open(tasks_json_path, "r") as f:
            return json.load(f)
    else:
        return []

def save_tasks(tasks):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    tasks_json_path = os.path.join(script_dir, 'tasks.json')

    with open(tasks_json_path, "w") as f:
        json.dump(tasks, f, indent=2)

def create_backup_task():
    backup_dir = input("请输入备份目录: ")
    cloud_dir = input("请输入网盘目录: ")
    identifier = input("请输入备份标识: ")
    rclone_path = input("请输入rclone位置(默认为rclone不带路径): ") or "rclone"
    webhook_url = input("请输入webhook链接(可跳过): ")
    exclude_dirs = input("请输入要跳过的子目录，用逗号分隔(可跳过): ")
    retention_count = input("请输入要保留的备份数量(可跳过): ")
    execution_interval = input("请输入执行周期(小时，默认为24): ") or "24"
    
    task = {
        "type": "normal",
        "backup_dir": backup_dir,
        "cloud_dir": cloud_dir,
        "identifier": identifier,
        "rclone_path": rclone_path,
        "webhook_url": webhook_url,
        "exclude_dirs": exclude_dirs.split(',') if exclude_dirs else [],
        "retention_count": int(retention_count) if retention_count else None,
        "execution_interval": int(execution_interval)
    }
    return task

def create_system_backup_task():
    system_partition = input("请输入系统所在分区: ")
    other_mount_points = input("请输入其他硬盘的挂载点，用逗号分隔: ").split(',')
    docker_root = input("请输入Docker根目录: ")
    temp_dir = input("请输入系统备份专用临时目录(可跳过): ")
    cloud_dir = input("请输入网盘目录: ")
    identifier = input("请输入备份标识: ")
    rclone_path = input("请输入rclone位置(默认为rclone不带路径): ") or "rclone"
    webhook_url = input("请输入webhook链接(可跳过): ")
    retention_count = input("请输入要保留的备份数量(可跳过): ")
    execution_interval = input("请输入执行周期(小时，默认为24): ") or "24"

    task = {
        "type": "system",
        "backup_dir": system_partition,
        "cloud_dir": cloud_dir,
        "identifier": identifier,
        "rclone_path": rclone_path,
        "webhook_url": webhook_url,
        "exclude_dirs": other_mount_points,
        "docker_root": docker_root,
        "temp_dir": temp_dir,
        "retention_count": int(retention_count) if retention_count else None,
        "execution_interval": int(execution_interval)
    }
    return task

def modify_task(task):
    if task['type'] == 'normal':
        print(f"当前备份目录: {task['backup_dir']}")
        backup_dir = input("请输入新的备份目录(跳过则不修改): ")
        if backup_dir:
            task["backup_dir"] = backup_dir
    elif task['type'] == 'system':
        print(f"当前系统分区: {task['backup_dir']}")
        system_partition = input("请输入新的系统分区(跳过则不修改): ")
        if system_partition:
            task["backup_dir"] = system_partition
        
        print(f"当前Docker根目录: {task['docker_root']}")
        docker_root = input("请输入新的Docker根目录(跳过则不修改): ")
        if docker_root:
            task["docker_root"] = docker_root
        
        print(f"当前系统备份专用临时目录: {task.get('temp_dir', '未设置')}")
        temp_dir = input("请输入新的系统备份专用临时目录(跳过则不修改): ")
        if temp_dir:
            task["temp_dir"] = temp_dir
    
    print(f"当前网盘目录: {task['cloud_dir']}")
    cloud_dir = input("请输入新的网盘目录(跳过则不修改): ")
    if cloud_dir:
        task["cloud_dir"] = cloud_dir
    
    print(f"当前备份标识: {task['identifier']}")
    identifier = input("请输入新的备份标识(跳过则不修改): ")
    if identifier:
        task["identifier"] = identifier
    
    print(f"当前rclone位置: {task['rclone_path']}")
    rclone_path = input("请输入新的rclone位置(跳过则不修改): ")
    if rclone_path:
        task["rclone_path"] = rclone_path
    
    print(f"当前webhook链接: {task['webhook_url']}")
    webhook_url = input("请输入新的webhook链接(跳过则不修改): ")
    if webhook_url:
        task["webhook_url"] = webhook_url
    
    exclude_dirs = task.get("exclude_dirs", [])
    print(f"当前跳过的{'子目录' if task['type'] == 'normal' else '挂载点'}: {','.join(exclude_dirs)}")
    exclude_input = input(f"请输入新的要跳过的{'子目录' if task['type'] == 'normal' else '挂载点'}，用逗号分隔(跳过则不修改): ")
    if exclude_input:
        task["exclude_dirs"] = exclude_input.split(',')
    
    print(f"当前保留的备份数量: {task.get('retention_count', '未设置')}")
    retention_count = input("请输入新的保留备份数量(跳过则不修改): ")
    if retention_count:
        task["retention_count"] = int(retention_count)
    
    print(f"当前执行周期: {task.get('execution_interval', 24)}小时")
    execution_interval = input("请输入新的执行周期(小时，跳过则不修改): ")
    if execution_interval:
        task["execution_interval"] = int(execution_interval)
    
    return task

def send_webhook(webhook_url, message):
    if webhook_url:
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            print("通知发送成功")
        except Exception as e:
            print(f"发送通知失败: {e}")

def restore_backup():
    tasks = load_tasks()
    print("请选择要还原的备份任务:")
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. {task['identifier']} ({task['type']}备份)")
    
    try:
        index = int(input("请输入备份任务编号: ")) - 1
        task = tasks[index]
    except (ValueError, IndexError):
        print("无效的备份任务编号")
        return

    rclone_path = task['rclone_path']
    cloud_dir = f"{task['cloud_dir']}/{task['identifier']}/"
    
    page = 0
    backups = []
    while True:
        # 列出最新的10个备份
        cmd = f"{rclone_path} lsf --format tp {cloud_dir} | sort -r | tail -n +{page*10+1} | head -n 10"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        new_backups = result.stdout.strip().split('\n')
        
        if not new_backups[0]:
            if page == 0:
                print("没有找到备份文件")
                return
            else:
                print("没有更多的备份文件了")
                continue

        backups = new_backups

        print("可用的备份文件:")
        for i, backup in enumerate(backups, start=1):
            print(f"{i}. {backup}")
        print("11. 列出更多备份")
        print("0. 返回上一级菜单")

        choice = input("请选择要还原的备份文件编号: ")
        if choice == '11':
            page += 1
            continue
        elif choice == '0':
            return
        else:
            try:
                index = int(choice) - 1
                selected_backup = backups[index]
                break
            except (ValueError, IndexError):
                print("无效的选择，请重试")

    print(f"你选择了还原: {selected_backup}")
    confirm = input("警告：这将完全覆盖目标目录的所有内容。是否确定继续？(y/n): ")
    if confirm.lower() != 'y':
        print("还原操作已取消")
        return

    # 下载并解压备份文件
    backup_path = os.path.join(cloud_dir, selected_backup.split(';')[1])
    local_backup = os.path.join('/tmp', selected_backup.split(';')[1])
    cmd = f"{rclone_path} copy {backup_path} /tmp/"
    subprocess.run(cmd, shell=True)

    # 解压并覆盖现有数据
    if task['type'] == 'normal':
        # 删除目标目录的所有内容
        for item in os.listdir(task['backup_dir']):
            item_path = os.path.join(task['backup_dir'], item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        
        # 解压新的备份内容
        cmd = f"unzip -o {local_backup} -d {task['backup_dir']}"
    else:  # system backup
        # 对于系统备份，我们需要更加小心
        cmd = f"sudo unzip -o {local_backup} -d /"
    
    subprocess.run(cmd, shell=True)
    
    # 清理临时文件
    os.remove(local_backup)
    
    print("还原操作完成")
    
    # 发送还原完成通知
    message = f"✅ 备份还原任务 '{task['identifier']}' 已完成\n- 类型: {'系统备份' if task['type'] == 'system' else '普通备份'}\n- 时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- 还原文件: {selected_backup.split(';')[1]}"
    send_webhook(task['webhook_url'], message)

def main():
    tasks = load_tasks()
    
    while True:
        print("\n备份任务管理")
        print("1. 显示已创建的备份任务")
        print("2. 创建新的备份任务")
        print("3. 创建新的系统备份任务")
        print("4. 修改备份任务")
        print("5. 删除备份任务")
        print("6. 还原备份")
        print("7. 退出")
        
        choice = input("请输入选项: ")
        
        if choice == "1":
            print("已创建的备份任务:")
            for i, task in enumerate(tasks, start=1):
                exclude_dirs = ','.join(task.get('exclude_dirs', []))
                print(f"{i}. 类型: {task['type']}, "
                      f"备份目录: {task['backup_dir']}, "
                      f"网盘目录: {task['cloud_dir']}, "
                      f"备份标识: {task['identifier']}, "
                      f"执行周期: {task.get('execution_interval', 24)}小时, "
                      f"跳过的{'子目录' if task['type'] == 'normal' else '挂载点'}: {exclude_dirs}")
        
        elif choice == "2":
            task = create_backup_task()
            tasks.append(task)
            save_tasks(tasks)
            print("备份任务创建成功")
        
        elif choice == "3":
            task = create_system_backup_task()
            tasks.append(task)
            save_tasks(tasks)
            print("系统备份任务创建成功")
        
        elif choice == "4":
            print("请选择要修改的备份任务:")
            for i, task in enumerate(tasks, start=1):
                exclude_dirs = ','.join(task.get('exclude_dirs', []))
                print(f"{i}. 类型: {task['type']}, "
                      f"备份目录: {task['backup_dir']}, "
                      f"网盘目录: {task['cloud_dir']}, "
                      f"备份标识: {task['identifier']}, "
                      f"执行周期: {task.get('execution_interval', 24)}小时, "
                      f"跳过的{'子目录' if task['type'] == 'normal' else '挂载点'}: {exclude_dirs}")
            
            try:
                index = int(input("请输入备份任务编号: ")) - 1
                task = tasks[index]
                modified_task = modify_task(task)
                tasks[index] = modified_task
                save_tasks(tasks)
                print("备份任务修改成功")
            except (ValueError, IndexError):
                print("无效的备份任务编号")
        
        elif choice == "5":
            print("请选择要删除的备份任务:")
            for i, task in enumerate(tasks, start=1):
                exclude_dirs = ','.join(task.get('exclude_dirs', []))
                print(f"{i}. 类型: {task['type']}, "
                      f"备份目录: {task['backup_dir']}, "
                      f"网盘目录: {task['cloud_dir']}, "
                      f"备份标识: {task['identifier']}, "
                      f"执行周期: {task.get('execution_interval', 24)}小时, "
                      f"跳过的{'子目录' if task['type'] == 'normal' else '挂载点'}: {exclude_dirs}")
            
            try:
                index = int(input("请输入备份任务编号: ")) - 1
                del tasks[index]
                save_tasks(tasks)
                print("备份任务删除成功")
            except (ValueError, IndexError):
                print("无效的备份任务编号")
        
        elif choice == "6":
            restore_backup()
        
        elif choice == "7":
            print("退出程序")
            break
        
        else:
            print("无效的选项，请重新输入")

if __name__ == "__main__":
    main()
