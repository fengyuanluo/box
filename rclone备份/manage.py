import os
import json

def load_tasks():
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as f:
            return json.load(f)
    else:
        return []

def save_tasks(tasks):
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)

def create_task():
    backup_dir = input("请输入备份目录: ")
    cloud_dir = input("请输入网盘目录: ")
    identifier = input("请输入备份标识: ")
    rclone_path = input("请输入rclone位置(默认为rclone不带路径): ") or "rclone"
    webhook_url = input("请输入webhook链接(可跳过): ")
    
    task = {
        "backup_dir": backup_dir,
        "cloud_dir": cloud_dir,
        "identifier": identifier,
        "rclone_path": rclone_path,
        "webhook_url": webhook_url
    }
    return task

def modify_task(task):
    print(f"当前备份目录: {task['backup_dir']}")
    backup_dir = input("请输入新的备份目录(跳过则不修改): ")
    if backup_dir:
        task["backup_dir"] = backup_dir
    
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
    
    return task

def main():
    tasks = load_tasks()
    
    while True:
        print("备份任务管理")
        print("1. 显示已创建的备份任务")
        print("2. 创建新的备份任务")
        print("3. 修改备份任务")
        print("4. 删除备份任务")
        print("5. 退出")
        
        choice = input("请输入选项: ")
        
        if choice == "1":
            print("已创建的备份任务:")
            for i, task in enumerate(tasks, start=1):
                print(f"{i}. 备份目录: {task['backup_dir']}, 网盘目录: {task['cloud_dir']}, 备份标识: {task['identifier']}")
        
        elif choice == "2":
            task = create_task()
            tasks.append(task)
            save_tasks(tasks)
            print("备份任务创建成功")
        
        elif choice == "3":
            print("请选择要修改的备份任务:")
            for i, task in enumerate(tasks, start=1):
                print(f"{i}. 备份目录: {task['backup_dir']}, 网盘目录: {task['cloud_dir']}, 备份标识: {task['identifier']}")
            
            try:
                index = int(input("请输入备份任务编号: ")) - 1
                task = tasks[index]
                modified_task = modify_task(task)
                tasks[index] = modified_task
                save_tasks(tasks)
                print("备份任务修改成功")
            except (ValueError, IndexError):
                print("无效的备份任务编号")
        
        elif choice == "4":
            print("请选择要删除的备份任务:")
            for i, task in enumerate(tasks, start=1):
                print(f"{i}. 备份目录: {task['backup_dir']}, 网盘目录: {task['cloud_dir']}, 备份标识: {task['identifier']}")
            
            try:
                index = int(input("请输入备份任务编号: ")) - 1
                del tasks[index]
                save_tasks(tasks)
                print("备份任务删除成功")
            except (ValueError, IndexError):
                print("无效的备份任务编号")
        
        elif choice == "5":
            break
        
        else:
            print("无效的选项")

if __name__ == "__main__":
    main()
