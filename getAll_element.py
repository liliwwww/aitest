from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup

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

# 智能切换到 大麦 页面
def switch_to_damai_tab():
    window_handles = driver.window_handles
    print(f"所有标签页句柄：{window_handles}")
    for handle in window_handles:
        driver.switch_to.window(handle)
        time.sleep(1)
        current_url = driver.current_url
        print(f"当前标签页 URL: {current_url}")
        if "https://www.damai.cn/" in current_url.lower():
            print(f"找到 DeepSeek 页面：{current_url}")
            driver.execute_script("window.focus();")
            driver.maximize_window()
            return True
    print("未找到 大麦 页面，请确保已打开")
    return False

# 提取页面中的链接、图片 URL 和所有元素的 id
def extract_page_info():
    try:
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 获取页面 HTML 源码
        html_source = driver.page_source

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_source, "html.parser")

        # 1. 提取所有链接（<a> 标签的 href 属性）
        print("\n=== 页面中的所有链接 ===")
        links = soup.find_all("a", href=True)
        for i, link in enumerate(links, 1):
            href = link["href"]
            print(f"链接 {i}: {href}")

        # 2. 提取所有图片的 URL（<img> 标签的 src 属性）
        print("\n=== 页面中的所有图片 URL ===")
        images = soup.find_all("img", src=True)
        for i, img in enumerate(images, 1):
            src = img["src"]
            print(f"图片 {i}: {src}")

        # 3. 提取所有元素的 id
        print("\n=== 页面中所有元素的 id ===")
        elements_with_id = soup.find_all(lambda tag: tag.has_attr("id"))
        for i, element in enumerate(elements_with_id, 1):
            element_id = element["id"]
            tag_name = element.name
            print(f"元素 {i}: 标签={tag_name}, id={element_id}")

    except Exception as e:
        print(f"Error extracting page info: {e}")

# 打印所有标签页信息
print_tabs_info()

# 切换到 damai 页面
if not switch_to_damai_tab():
    exit()

# 提取页面信息
extract_page_info()

# 保持浏览器打开
print("\n程序完成，浏览器保持打开状态以维持上下文。")