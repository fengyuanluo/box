import os
import json
import glob
import requests

def load_tasks():
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as f:
            return json.load(f)
    else:
        return []

def send_notification(task, backup_path):
    webhook_url = task["webhook_url"]
    if not webhook_url:
        return
    
    file_name = os.path.basename(backup_path)
    file_size = os.path.getsize(backup_path)
    cloud_dir = task["cloud_dir"]
    
    message = f"文件名: {file_name}\n文件大小: {file_size} bytes\n备份目标目录: {cloud_dir}"
    
    data = {
        "content": message
    }
    
    requests.post(webhook_url, json=data)

def main():
    tasks = load_tasks()
    
    for task in tasks:
        backup_dir = task["backup_dir"]
        identifier = task["identifier"]
        backup_pattern = f"{identifier}-*.zip"
        backup_path = os.path.join(os.path.dirname(backup_dir), backup_pattern)
        
        latest_backup = max(glob.glob(backup_path), key=os.path.getctime)
        send_notification(task, latest_backup)

if __name__ == "__main__":
    main()