# locustfile.py
from locust import HttpUser, task, between
import subprocess  # 导入 subprocess 模块

class MyUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://example.com"  # 替换为你的目标主机

    @task
    def run_script_task(self):
        try:
            # 运行 text.py 脚本
            process = subprocess.run(['python3', '/Users/anbei/Desktop/bedrock-cn/example/python/text.py'], capture_output=True, text=True)
            if process.returncode == 0:
                print(f"Script output: {process.stdout}")
            else:
                print(f"Script error: {process.stderr}")
        except Exception as e:
            print(f"Error running script: {e}")
