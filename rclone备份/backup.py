import os
import json
import shutil
import zipfile
import datetime
import subprocess
import tempfile
import requests
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:20171'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:20171'


def load_tasks():
    # Ensure the path of tasks.json in the same directory of the script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    tasks_file = os.path.join(dir_path, "tasks.json")


    # Check if the file exists and it is not empty
    if os.path.exists(tasks_file) and os.path.getsize(tasks_file) > 0:
        with open(tasks_file, "r") as f:
            tasks = json.load(f)
        return tasks
    else:
        print("Can't load tasks: File does not exist or it is empty.")
        return []
        
    # Ensure 'exclude_dirs' field exists in each of the task
    for task in tasks:
        if 'exclude_dirs' not in task:
            task['exclude_dirs'] = []
    
    return tasks

def copy_to_temp_dir(source_dir, exclude_dirs):
    # Copies the source directory to a temporary directory, skipping the exclude_dirs
    temp_dir = tempfile.mkdtemp()
    temp_backup_dir = os.path.join(temp_dir, os.path.basename(source_dir))

    # Check if the directory already exists. If it does, remove it first.
    if os.path.exists(temp_backup_dir):
        shutil.rmtree(temp_backup_dir)

    def should_copy_dir(path):
        # Check if the path is not part of the directories to exclude
        for exclude_dir in exclude_dirs:
            if os.path.abspath(exclude_dir) == os.path.abspath(path):
                return False
        return True

    shutil.copytree(source_dir, temp_backup_dir, ignore=lambda directory, contents: [c for c in contents if not should_copy_dir(os.path.join(directory, c))])
    return temp_backup_dir

def create_backup_zip(temp_backup_dir, identifier):
    # Compresses the temporary directory and returns the path to the zip file
    now = datetime.datetime.now()
    backup_name = f"{identifier}-{now.strftime('%Y-%m-%d-%H%M%S')}.zip"
    backup_path = os.path.join(os.path.dirname(temp_backup_dir), backup_name)
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_backup_dir))
    return backup_path

def ensure_cloud_dir_exists(cloud_dir, rclone_path):
    # Split the cloud directory into individual parts
    dir_parts = cloud_dir.split("/")
    current_dir = dir_parts[0]
    
    # Iterate over the directory parts and create each level if it doesn't exist
    for part in dir_parts[1:]:
        current_dir = os.path.join(current_dir, part)
        result = subprocess.run([rclone_path, "lsjson", current_dir], capture_output=True, text=True)
        
        if result.returncode != 0:
            # Directory does not exist, create it
            subprocess.run([rclone_path, "mkdir", current_dir])

def upload_to_cloud(task, backup_path):
    base_cloud_dir = task["cloud_dir"]
    rclone_path = task["rclone_path"]
    now = datetime.datetime.now()
    
    # Create the date-based directory structure
    date_dir = f"{now.year}/{now.month}/{now.day}"
    cloud_dir = os.path.join(base_cloud_dir, date_dir)
    
    # Ensure the cloud directory exists
    ensure_cloud_dir_exists(cloud_dir, rclone_path)
    
    # Upload the backup file to the cloud directory
    subprocess.run([rclone_path, "copy", backup_path, cloud_dir])

def call_notify_script(task, backup_path):
    webhook_url = task["webhook_url"]
    if not webhook_url:
        return

    file_name = os.path.basename(backup_path)
    file_size_bytes = os.path.getsize(backup_path)
    # Convert file size to MB
    file_size_MB = file_size_bytes / 1048576
    cloud_dir = task["cloud_dir"]
    
    message = f"文件名: {file_name}\n文件大小: {file_size_MB:.2f} MB\n备份目标目录: {cloud_dir}"
    
    data = {
        "msgtype": "text",
        "text": {
            "content": message,
        }
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    requests.post(webhook_url, headers=headers, json=data)

def main():
    tasks = load_tasks()
    for task in tasks:
        temp_backup_dir = copy_to_temp_dir(task["backup_dir"], task["exclude_dirs"])
        backup_zip_path = create_backup_zip(temp_backup_dir, task["identifier"])
        upload_to_cloud(task, backup_zip_path)
        call_notify_script(task, backup_zip_path)  # Pass parameters to call_notify_script
        shutil.rmtree(temp_backup_dir)  # Clean up the temporary directory

if __name__ == "__main__":
    main()