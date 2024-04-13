import os
import json

def load_tasks():
    # Get the directory of current script
    script_dir = os.path.dirname(__file__)
    # Define the path of tasks.json
    tasks_json_path = os.path.join(script_dir, 'tasks.json')

    if os.path.exists(tasks_json_path):
        with open(tasks_json_path, "r") as f:
            return json.load(f)
    else:
        return []

def save_tasks(tasks):
    # Get the directory of current script
    script_dir = os.path.dirname(__file__)
    # Define the path of tasks.json
    tasks_json_path = os.path.join(script_dir, 'tasks.json')

    with open(tasks_json_path, "w") as f:
        json.dump(tasks, f, indent=2)

def create_task():
    backup_dir = input("请输入备份目录: ")
    cloud_dir = input("请输入网盘目录: ")
    identifier = input("请输入备份标识: ")
    rclone_path = input("请输入rclone位置(默认为rclone不带路径): ") or "rclone"
    webhook_url = input("请输入webhook链接(可跳过): ")
    exclude_dirs = input("请输入要跳过的子目录，用逗号分隔(可跳过): ")
    
    # 确保即使用户没有输入任何内容，任务中也会有 'exclude_dirs' 字段，其为一个空列表
    task = {
        "backup_dir": backup_dir,
        "cloud_dir": cloud_dir,
        "identifier": identifier,
        "rclone_path": rclone_path,
        "webhook_url": webhook_url,
        "exclude_dirs": exclude_dirs.split(',') if exclude_dirs else []
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
    
    # 确保 'exclude_dirs' 字段总是可用，即便它是一个空列表
    exclude_dirs = task.get("exclude_dirs", [])
    print(f"当前跳过的子目录: {','.join(exclude_dirs)}")
    exclude_input = input("请输入新的要跳过的子目录，用逗号分隔(跳过则不修改): ")
    if exclude_input:
        task["exclude_dirs"] = exclude_input.split(',')
    
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
                # 使用 get 方法安全访问 'exclude_dirs' 字段，如果该字段不存在，则给出空列表
                exclude_dirs = ','.join(task.get('exclude_dirs', []))
                print(f"{i}. 备份目录: {task['backup_dir']}, "
                      f"网盘目录: {task['cloud_dir']}, "
                      f"备份标识: {task['identifier']}, "
                      f"跳过的子目录: {exclude_dirs}")
        
        elif choice == "2":
            task = create_task()
            tasks.append(task)
            save_tasks(tasks)
            print("备份任务创建成功")
        
        elif choice == "3":
            print("请选择要修改的备份任务:")
            for i, task in enumerate(tasks, start=1):
                exclude_dirs = ','.join(task.get('exclude_dirs', []))
                print(f"{i}. 备份目录: {task['backup_dir']}, "
                      f"网盘目录: {task['cloud_dir']}, "
                      f"备份标识: {task['identifier']}, "
                      f"跳过的子目录: {exclude_dirs}")
            
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
                exclude_dirs = ','.join(task.get('exclude_dirs', []))
                print(f"{i}. 备份目录: {task['backup_dir']}, "
                      f"网盘目录: {task['cloud_dir']}, "
                      f"备份标识: {task['identifier']}, "
                      f"跳过的子目录: {exclude_dirs}")
            
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