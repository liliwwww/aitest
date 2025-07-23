import subprocess

# 发送切换背景命令
def switch_background(image_name):

    cmd = f"adb shell am broadcast -a ADBCommand --es cmd 'switchBackGroup {image_name}'"
    print(f"send cmd \n {cmd}")
    subprocess.run(cmd, shell=True)



# 使用示例
if __name__ == "__main__":
    # 示例：切换为back.jpg背景
    switch_background("back")