import subprocess

def send_adb_command(command):
    """
    通过 ADB 发送广播到 Android 设备
    :param command: 要发送的指令字符串
    """
    adb_command = [
        'adb', 'shell', 'am', 'broadcast',
        '-a', 'com.example.andriodtemplet.ADB_COMMAND',  # 广播动作
        '--es', 'command', command                      # 额外数据：键为 "command"，值为指令
    ]

    print(f"cmd is {adb_command} ")
    subprocess.run(adb_command, check=True)  # 执行 ADB 命令

# 发送指令 "switch back,jpg"
send_adb_command("switch back.jpg")

