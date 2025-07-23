from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import clr  # 用于调用 .NET 库（Microsoft SendKeys）
import System  # 导入 .NET System 命名空间
from lxml import etree

# 加载 SendKeys（需要时使用）
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import SendKeys

# 配置 Chrome 选项
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 连接到调试端口

# 初始化浏览器（不启动新实例，直接连接到已打开的 Chrome）
driver = webdriver.Chrome(options=chrome_options)

# 最大化窗口
driver.maximize_window()

# 打印所有标签页的 URL 和标题
def print_tabs_info():
    window_handles = driver.window_handles
    print(f"当前打开的标签页数量：{len(window_handles)}")
    original_handle = driver.current_window_handle
    for index, handle in enumerate(window_handles):
        driver.switch_to.window(handle)
        time.sleep(1)
        url = driver.current_url
        title = driver.title
        print(f"标签页 {index + 1} - URL: {url}")
        print(f"标签页 {index + 1} - 标题: {title}")
    driver.switch_to.window(original_handle)

# 智能切换到 DeepSeek 页面
def switch_to_deepseek_tab():
    window_handles = driver.window_handles
    print(f"所有标签页句柄：{window_handles}")
    for handle in window_handles:
        driver.switch_to.window(handle)
        time.sleep(1)
        current_url = driver.current_url
        print(f"当前标签页 URL: {current_url}")
        if "deepseek" in current_url.lower():
            print(f"找到 DeepSeek 页面：{current_url}")
            driver.execute_script("window.focus();")
            driver.maximize_window()
            return True
    print("未找到 DeepSeek 页面，请确保已打开")
    return False

# 获取并打印所有元素的 XPath
def print_all_xpaths(max_depth=5):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        html_source = driver.page_source
        tree = etree.HTML(html_source)
        
        def generate_xpath(element, path="/", depth=0):
            if depth > max_depth:
                return
            tag = element.tag
            if tag == etree.Comment:
                return
            parent = element.getparent()
            if parent is None:
                current_path = path + tag
            else:
                siblings = [child for child in parent.getchildren() if child.tag == tag]
                if len(siblings) > 1:
                    index = siblings.index(element) + 1
                    current_path = f"{path}{tag}[{index}]"
                else:
                    current_path = f"{path}{tag}"
            element_info = f"XPath: {current_path}"
            if element.get("id"):
                element_info += f", id: {element.get('id')}"
            if element.get("class"):
                element_info += f", class: {element.get('class')}"
            print(element_info)
            for child in element.getchildren():
                generate_xpath(child, current_path + "/", depth + 1)
        
        root = tree.getroottree().getroot()
        generate_xpath(root)
    except Exception as e:
        print(f"Error printing XPaths: {e}")

# 打印所有标签页信息
print_tabs_info()

# 切换到 DeepSeek 页面
if not switch_to_deepseek_tab():
    exit()

# 打印页面 HTML，检查 chat-input 元素是否存在
html_content = driver.page_source
if "chat-input" in html_content:
    print("页面中存在 chat-input 元素")
else:
    print("页面中不存在 chat-input 元素")

# 打印页面中所有元素的 XPath
print("\n打印页面中所有元素的 XPath：")
print_all_xpaths(max_depth=5)

def check_input_box():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "chat-input"))
        )
        print("文本输入框存在，可以输入消息")
        return True
    except Exception as e:
        print(f"文本输入框不存在：{e}")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='给 DeepSeek 发送消息 ']"))
            )
            print("通过 placeholder 找到文本输入框")
            return True
        except Exception as e2:
            print(f"通过 placeholder 也无法找到文本输入框：{e2}")
            return False

def send_message(message):
    try:
        if not check_input_box():
            return False
        try:
            input_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "chat-input"))
            )
        except:
            input_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//textarea[@placeholder='给 DeepSeek 发送消息 ']"))
            )
        input_box.clear()
        input_box.send_keys(message)
        print("已输入消息，准备点击发送按钮")

        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(@class, '_7436101')]"))
        )
        send_button.click()
        print("已点击发送按钮")
    except Exception as e:
        print(f"Error sending message: {e}")
        try:
            send_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-disabled='false' and .//div[contains(@class, 'ds-icon')]]"))
            )
            send_button.click()
            print("通过备选选择器点击发送按钮")
        except Exception as e2:
            print(f"通过备选选择器也无法点击发送按钮：{e2}")
            return False
    return True

def extract_response(previous_message_count=0, previous_last_message="", timeout=30):
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
                return messages[-1].text

            # 如果消息数量未增加，但最后一个消息内容变化（可能是流式更新）
            if messages:
                current_last_message = messages[-1].text
                if current_last_message != previous_last_message:
                    print(f"最后一个消息内容已更新，新消息已生成")
                    return current_last_message

            print(f"当前消息数量 {current_message_count}，最后一个消息内容未变化，继续等待")
            time.sleep(1)  # 每秒检查一次

        # 超时未变化
        print(f"等待 {timeout} 秒后，新消息未生成")
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
                    timeout=30
                )
                if response:
                    print("模型回复：", response)
                else:
                    print("未能获取回复，请检查网络或页面元素。")
            else:
                print("消息发送失败，请检查页面元素。")
            time.sleep(2)
    finally:
        print("程序退出，但浏览器保持打开状态以维持上下文。")

if __name__ == "__main__":
    main()