#!/usr/bin/env python3
import time
import datetime
import subprocess
import os
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def wait_until(target_time):
    """等待到指定时间"""
    now = datetime.datetime.now()
    target = now.replace(hour=target_time.hour, minute=target_time.minute, second=target_time.second, microsecond=0)
    
    # 如果目标时间已经过去，等到明天同一时间
    if now > target:
        target = target + datetime.timedelta(days=1)
    
    wait_seconds = (target - now).total_seconds()
    logger.info(f"等待到 {target.strftime('%H:%M:%S')}，还有 {wait_seconds:.1f} 秒")
    
    # 如果等待时间少于5分钟，进入精确等待模式
    if wait_seconds < 300:
        while datetime.datetime.now() < target:
            time.sleep(0.01)  # 小间隔检查，确保准确性
    else:
        # 否则使用普通sleep，每30秒输出一次日志
        while wait_seconds > 0:
            sleep_time = min(30, wait_seconds)
            time.sleep(sleep_time)
            wait_seconds -= sleep_time
            logger.info(f"还剩 {wait_seconds:.1f} 秒")

def main():
    """主函数，在指定时间运行预订脚本"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 正常运行时间：11:59:00 AM (稍早于11:59:20，给脚本启动的时间)
    now = datetime.datetime.now()
    target_time = now.replace(hour=11, minute=59, second=0)
    
    logger.info(f"准备在 {target_time.strftime('%H:%M:%S')} 启动预订脚本")
    
    # 等待直到目标时间
    wait_until(target_time)
    
    # 运行预订脚本
    logger.info("开始运行预订脚本")
    
    booking_script = os.path.join(script_dir, "book.py")
    result = subprocess.run(["python3", booking_script], capture_output=True, text=True)
    
    # 记录运行结果
    logger.info(f"预订脚本返回代码: {result.returncode}")
    logger.info(f"标准输出:\n{result.stdout}")
    
    if result.stderr:
        logger.error(f"错误输出:\n{result.stderr}")

if __name__ == "__main__":
    main() 