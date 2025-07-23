from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import clr  # 用于调用 .NET 库（Microsoft SendKeys）
import System  # 导入 .NET System 命名空间

# 加载 SendKeys（需要安装 pythonnet 包：pip install pythonnet）
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import SendKeys

# 配置 Chrome 选项
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 连接到调试端口
print("connected ok")

# 初始化浏览器（不启动新实例，直接连接到已打开的 Chrome）
driver = webdriver.Chrome(options=chrome_options)



# 打印所有标签页的 URL 和标题
active_handle ="AAAA";

def print_tabs_info( ):
    print("connected print_tabs_info()")
    """打印每个标签页的 URL 和标题"""
    window_handles = driver.window_handles
    print(f"当前打开的标签页数量：{len(window_handles)}")
    
    # 保存当前标签页句柄，以便恢复
    original_handle = driver.current_window_handle
    active_handle = original_handle

    print(f"save 当前tab handle：{original_handle}")

        # 遍历每个标签页
    for index, handle in enumerate(window_handles):
        print(f"遍历 tab handle：{handle}")
        driver.switch_to.window(handle)
        # 等待页面加载（避免获取不到 URL 或标题）
        time.sleep(1)
        url = driver.current_url
        title = driver.title
        print(f"标签页 {index + 1} - URL: ->{url}<-")
        print(f"标签页 {index + 1} - 标题: {title}")

        if url == 'https://www.deepseek.com/':
            print(f"找到了 tab{index}")
            active_handle = handle
            print(f"找到了 tab ID is {active_handle}")

    
    # 恢复到原始标签页
    print(f" 当前tab handle：{original_handle}")
    driver.switch_to.window(original_handle)

    return active_handle


# 切换到 DeepSeek 页面所在的标签页
'''
window_handles = driver.window_handles
print(f"当前打开的标签页数量：{len(window_handles)}")
if len(window_handles) >= 2:
    driver.switch_to.window(window_handles[1])
    print(f"已切换到标签页：{driver.current_url}")
else:
    print("未找到足够的标签页，请确保 DeepSeek 页面已打开")
    exit()
'''

# 打印所有标签页的信息
active_handle = print_tabs_info()

# 激活deepseek tab
print(f"准备激活tab{active_handle}")
driver.switch_to.window(active_handle)



def check_input_box():
    """检查文本输入框是否存在"""
    try:
        
        element = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "chat-input"))
        )
        print("a找到元素：", element)  # element 是一个 WebElement 对象
        print("a元素标签名：", element.tag_name)  # 例如 "textarea"


        element = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[contains(@id, 'chat-input')]"))
        )
        print("b找到元素：", element)  # element 是一个 WebElement 对象
        print("b元素标签名：", element.tag_name)  # 例如 "textarea"
        
        

        print("文本输入框存在，可以输入消息")
        return True
    except Exception as e:
        print(f"文本输入框不存在：{e}")
        return False
    
def send_message(message):
    """发送消息"""
    try:

        # 先检查文本输入框是否存在
        if not check_input_box():
            return False
        
        # 定位文本输入框
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@id='chat-input']"))
        )
        input_box.clear()
        input_box.send_keys(message)

        # 使用 SendKeys 模拟按下 Enter 键（增强键盘输入稳定性）
        #print( )

        #SendKeys.SendWait("{ENTER}")
         # 定位发送按钮并点击
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(@class, '_7436101')]"))
        )
        print(f"找到按钮了：{send_button}")
        send_button.click()

        
        print("Enter sending message: ")

        # 或者使用 Selenium 点击发送按钮
        # send_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '开启新对话')]"))
        # )
        # send_button.click()
    except Exception as e:
        print("send ... error")
        print(f"Error sending message: {e}")
        return False
    return True

def refresh_new_message(driver):

    first_messages = driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]"
            )
    first_messages_text = first_messages[-1].text
    while True:
        print('while.....')
        time.sleep(5)  # 每5秒检查一次
        print('while.....')
        last_messages = driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]"
            )
        last_messages_text = last_messages[-1].text
        print(f"发现新内容，继续{len(last_messages_text)},{len(first_messages_text)}")

        if len(last_messages_text) > len(first_messages_text):
            first_messages_text = last_messages_text
        else:
            return last_messages_text
    

    


def extract_response(previous_message_count=0, previous_last_message="", timeout=40):
    """提取模型返回的最新回复，等待新消息出现或内容变化"""
    try:
        # 等待至少一个符合条件的 <div> 出现（如果之前没有消息）
        if previous_message_count == 0:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]")
                )
            )

        # 轮询检查消息数量或内容是否变化
        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]"
            )
            current_message_count = len(messages)

            # 如果消息数量增加，说明新消息已生成
            if current_message_count > previous_message_count:
                print(f"消息数量从 {previous_message_count} 增加到 {current_message_count}，新消息已生成")
                #new 版本 如果新消息生成了，进入一个新的循坏。不停地检测新消息是否完成
                return refresh_new_message(driver)
                #old 版本，直接输出 return messages[-1].text

            # 如果消息数量未增加，但最后一个消息内容变化（可能是流式更新）
            if messages:
                current_last_message = messages[-1].text
                if current_last_message != previous_last_message:
                    print(f"最后一个消息内容已更新，新消息已生成")
                    return current_last_message

            print(f"当前消息数量 {current_message_count}，最后一个消息内容未变化，继续等待")
            time.sleep(5)  # 每秒检查一次

        # 超时未变化
        print(f"等待 {timeout} 秒后，新消息未生成")
        return None
    except Exception as e:
        print(f"Error extracting response: {e}")
        return None


def extract_response_1():
    """提取模型返回的最新回复"""
    try:
        # 等待至少一个符合条件的 <div> 出现
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]")
            )
        )

        # 获取所有符合条件的 <div> 元素
        messages = driver.find_elements(
            By.XPATH, 
            "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]"
        )

        # 提取最后一个元素（最新回复）的文本内容
        if messages:
            response = messages[-1].text
            return response
        else:
            return None
    except Exception as e:
        print(f"Error extracting response: {e}")
        return None

def main():
    try:
        while True:
            # 在发送消息前，记录当前消息数量和最后一个消息内容
            messages = driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]"
            )
            previous_message_count = len(messages)
            previous_last_message = messages[-1].text if messages else ""
            print(f"发送前消息数量：{previous_message_count}")

            user_input = input("请输入你的消息（输入'exit'退出）：")
            if user_input.lower() == 'exit':
                break
            if send_message(user_input):
                # 提取回复，等待新消息出现
                response = extract_response(
                    previous_message_count=previous_message_count,
                    previous_last_message=previous_last_message,
                    timeout=40
                )
                if response:
                    print("模型回复：", response)
                else:
                    print("未能获取回复，请检查网络或页面元素。")
            else:
                print("消息发送失败，请检查页面元素。")
            time.sleep(10)
    finally:
        print("程序退出，但浏览器保持打开状态以维持上下文。")

def main_1():
    print("Start1: ")
    try:
        # 示例对话（在同一页面上进行多次对话）
        while True:
            user_input = input("请输入你的消息（输入'exit'退出）：")
            if user_input.lower() == 'exit':
                break

            # 发送消息
            if send_message(user_input):
                # 提取回复
                response = extract_response()
                if response:
                    print("模型回复：", response)
                else:
                    print("未能获取回复，请检查网络或页面元素。")
            else:
                print("消息发送失败，请检查页面元素。")

            # 随机延迟，模拟真实用户行为
            time.sleep(2)
    finally:
        # 不关闭浏览器，保持上下文
        print("程序退出，但浏览器保持打开状态以维持上下文。")

if __name__ == "__main__":
    main()