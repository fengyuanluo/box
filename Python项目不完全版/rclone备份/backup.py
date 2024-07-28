import os
import json
import shutil
import zipfile
import datetime
import subprocess
import tempfile
import requests
import logging
import time

# 设置日志
script_dir = os.path.dirname(os.path.realpath(__file__))
log_file = os.path.join(script_dir, 'backup.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_tasks():
    tasks_file = os.path.join(script_dir, "tasks.json")
    logging.info(f"Attempting to load tasks from {tasks_file}")

    if os.path.exists(tasks_file) and os.path.getsize(tasks_file) > 0:
        with open(tasks_file, "r") as f:
            tasks = json.load(f)
        logging.info(f"Successfully loaded {len(tasks)} tasks")
        return tasks
    else:
        logging.error("Can't load tasks: File does not exist or it is empty.")
        return []

def rsync_to_temp_dir(source_dir, exclude_dirs, temp_dir):
    temp_backup_dir = os.path.join(temp_dir, os.path.basename(source_dir))
    logging.info(f"Rsync from {source_dir} to {temp_backup_dir}")

    if os.path.exists(temp_backup_dir):
        shutil.rmtree(temp_backup_dir)

    exclude_args = [f"--exclude={dir}" for dir in exclude_dirs]
    rsync_command = ["rsync", "-a", "--delete"] + exclude_args + [source_dir, temp_dir]
    logging.debug(f"Rsync command: {' '.join(rsync_command)}")
    
    result = subprocess.run(rsync_command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Rsync failed: {result.stderr}")
    else:
        logging.info("Rsync completed successfully")

    return temp_backup_dir

def create_backup_zip(temp_backup_dir, identifier):
    now = datetime.datetime.now()
    backup_name = f"{identifier}-{now.strftime('%Y-%m-%d-%H%M%S')}.zip"
    backup_path = os.path.join(os.path.dirname(temp_backup_dir), backup_name)
    logging.info(f"Creating backup zip: {backup_path}")

    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, temp_backup_dir))
        logging.info("Backup zip created successfully")
    except Exception as e:
        logging.error(f"Failed to create backup zip: {e}")
        raise

    return backup_path

def ensure_cloud_dir_exists(cloud_dir, rclone_path):
    logging.info(f"Ensuring cloud directory exists: {cloud_dir}")
    cmd = [rclone_path, "mkdir", cloud_dir]
    logging.debug(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to create directory {cloud_dir}: {result.stderr}")
    else:
        logging.debug(f"Directory {cloud_dir} created or already exists")

def upload_to_cloud(backup_path, cloud_dir, identifier, rclone_path):
    upload_dir = f"{cloud_dir}/{identifier}/"
    logging.info(f"Uploading {backup_path} to {upload_dir}")
    ensure_cloud_dir_exists(upload_dir, rclone_path)
    cmd = [rclone_path, "copy", backup_path, upload_dir]
    logging.debug(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Upload failed: {result.stderr}")
    else:
        logging.info("Upload completed successfully")

def delete_old_backups(cloud_dir, identifier, rclone_path, retention_count):
    if retention_count is None:
        logging.info("No retention count specified, skipping old backup deletion")
        return

    backup_dir = f"{cloud_dir}/{identifier}/"
    logging.info(f"Deleting old backups in {backup_dir}, retaining {retention_count} latest backups")
    cmd = [rclone_path, "lsf", "--format", "tp", backup_dir]
    logging.debug(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"Failed to list backups: {result.stderr}")
        return

    backups = []
    for line in result.stdout.strip().split('\n'):
        parts = line.split(';')
        if len(parts) == 2:
            timestamp, filename = parts
            backups.append((timestamp, filename))

    backups.sort(reverse=True)  # Sort by timestamp, newest first
    logging.debug(f"Found {len(backups)} backups")

    if len(backups) > retention_count:
        for _, filename in backups[retention_count:]:
            backup_path = f"{backup_dir}{filename}"
            delete_cmd = [rclone_path, "delete", backup_path]
            logging.debug(f"Running command: {' '.join(delete_cmd)}")
            delete_result = subprocess.run(delete_cmd, capture_output=True, text=True)
            if delete_result.returncode != 0:
                logging.error(f"Failed to delete {backup_path}: {delete_result.stderr}")
            else:
                logging.info(f"Deleted old backup: {backup_path}")

def send_webhook(webhook_url, message):
    if webhook_url:
        try:
            logging.info(f"Sending webhook: {message}")
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            logging.info("Webhook sent successfully")
        except Exception as e:
            logging.error(f"Failed to send webhook: {e}")

def backup_system(task):
    logging.info(f"Starting system backup for task: {task['identifier']}")
    system_partition = task['backup_dir']
    other_mount_points = task.get('exclude_dirs', [])
    docker_root = task.get('docker_root', '')
    temp_dir = task.get('temp_dir', '/tmp')
    cloud_dir = task['cloud_dir']
    identifier = task['identifier']
    rclone_path = task['rclone_path']
    webhook_url = task.get('webhook_url', '')
    retention_count = task.get('retention_count')

    with tempfile.TemporaryDirectory(dir=temp_dir) as temp_backup_dir:
        logging.info(f"Created temporary directory: {temp_backup_dir}")
        
        rsync_command = ["sudo", "rsync", "-aAXv", "--delete"]
        rsync_command.extend([f"--exclude={mp}" for mp in other_mount_points])
        rsync_command.extend(["--exclude=/dev/*", "--exclude=/proc/*", "--exclude=/sys/*", 
                              "--exclude=/tmp/*", "--exclude=/run/*", "--exclude=/mnt/*", 
                              "--exclude=/media/*", "--exclude=/lost+found"])
        rsync_command.extend(["/", temp_backup_dir])
        
        logging.debug(f"Running system rsync command: {' '.join(rsync_command)}")
        result = subprocess.run(rsync_command, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"System rsync failed: {result.stderr}")
            raise Exception("System rsync failed")

        if docker_root:
            docker_backup_dir = os.path.join(temp_backup_dir, "docker_backup")
            os.makedirs(docker_backup_dir, exist_ok=True)
            docker_rsync_command = ["sudo", "rsync", "-av", "--delete", docker_root, docker_backup_dir]
            logging.debug(f"Running Docker rsync command: {' '.join(docker_rsync_command)}")
            docker_result = subprocess.run(docker_rsync_command, capture_output=True, text=True)
            if docker_result.returncode != 0:
                logging.error(f"Docker rsync failed: {docker_result.stderr}")
                raise Exception("Docker rsync failed")

        backup_path = create_backup_zip(temp_backup_dir, identifier)
        upload_to_cloud(backup_path, cloud_dir, identifier, rclone_path)
        os.remove(backup_path)
        logging.info(f"Removed local backup file: {backup_path}")

        delete_old_backups(cloud_dir, identifier, rclone_path, retention_count)
        send_webhook(webhook_url, f"✅ 系统备份任务 '{identifier}' 已完成\n- 类型: 系统备份\n- 时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def backup_normal(task):
    logging.info(f"Starting normal backup for task: {task['identifier']}")
    backup_dir = task['backup_dir']
    cloud_dir = task['cloud_dir']
    identifier = task['identifier']
    rclone_path = task['rclone_path']
    webhook_url = task.get('webhook_url', '')
    exclude_dirs = task.get('exclude_dirs', [])
    retention_count = task.get('retention_count')

    with tempfile.TemporaryDirectory() as temp_dir:
        logging.info(f"Created temporary directory: {temp_dir}")
        temp_backup_dir = rsync_to_temp_dir(backup_dir, exclude_dirs, temp_dir)
        backup_path = create_backup_zip(temp_backup_dir, identifier)
        upload_to_cloud(backup_path, cloud_dir, identifier, rclone_path)
        os.remove(backup_path)
        logging.info(f"Removed local backup file: {backup_path}")

        delete_old_backups(cloud_dir, identifier, rclone_path, retention_count)
        send_webhook(webhook_url, f"✅ 普通备份任务 '{identifier}' 已完成\n- 类型: 普通备份\n- 时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def execute_upload_task(task):
    source_dir = task['source_dir']
    cloud_dir = task['cloud_dir']
    identifier = task['identifier']
    rclone_path = task['rclone_path']
    webhook_url = task['webhook_url']

    logging.info(f"Starting upload task: {identifier}")
    upload_dir = f"{cloud_dir}/{identifier}/"
    ensure_cloud_dir_exists(upload_dir, rclone_path)

    cmd = [rclone_path, "copy", source_dir, upload_dir]
    logging.debug(f"Running upload command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"Upload failed: {result.stderr}")
        raise Exception("Upload failed")
    else:
        logging.info("Upload completed successfully")

    send_webhook(webhook_url, f"✅ 上传任务 '{identifier}' 已完成\n- 类型: 文件上传\n- 时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- 源目录: {source_dir}")

def main():
    logging.info("Starting backup process")
    tasks = load_tasks()
    
    while True:
        current_time = datetime.datetime.now()
        
        for task in tasks:
            try:
                last_execution = task.get('last_execution', None)
                execution_interval = task.get('execution_interval', 24)  # 默认24小时
                
                if last_execution is None or (current_time - datetime.datetime.fromisoformat(last_execution)).total_seconds() >= execution_interval * 3600:
                    logging.info(f"Processing task: {task['identifier']}")
                    if task['type'] == 'system':
                        backup_system(task)
                    elif task['type'] == 'normal':
                        backup_normal(task)
                    elif task['type'] == 'upload':
                        execute_upload_task(task)
                    else:
                        logging.error(f"Unknown task type: {task['type']}")
                    
                    task['last_execution'] = current_time.isoformat()
                    
                    # 保存更新后的任务列表
                    with open(os.path.join(script_dir, "tasks.json"), "w") as f:
                        json.dump(tasks, f, indent=2)
            except Exception as e:
                error_message = f"Error during task execution of {task['identifier']}: {e}"
                logging.exception(error_message)
                send_webhook(task.get('webhook_url', ''), f"❌ 任务 '{task['identifier']}' 失败\n- 类型: {task['type']}\n- 时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n- 错误: {str(e)}")

        # 等待一小时后再次检查
        time.sleep(3600)

if __name__ == "__main__":
    main()
