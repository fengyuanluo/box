import os
import json
import zipfile
import datetime
import subprocess

def load_tasks():
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as f:
            return json.load(f)
    else:
        return []

def backup_folder(task):
    backup_dir = task["backup_dir"]
    identifier = task["identifier"]
    now = datetime.datetime.now()
    backup_name = f"{identifier}-{now.year}-{now.month}-{now.day}-{now.hour}.zip"
    backup_path = os.path.join(os.path.dirname(backup_dir), backup_name)
    
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, backup_dir))
    
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

def main():
    tasks = load_tasks()
    
    for task in tasks:
        backup_path = backup_folder(task)
        upload_to_cloud(task, backup_path)

if __name__ == "__main__":
    main()