from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置 Chrome 选项
chrome_options = Options()
print("start1" )

chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 连接到调试端口
print("start2" )

# 初始化浏览器（不启动新实例，直接连接到已打开的 Chrome）
driver = webdriver.Chrome(options=chrome_options)
print("start3" )
# 最大化窗口
driver.maximize_window()

# 打印所有标签页的 URL 和标题
def print_tabs_info():
    print("start1->print_tabs_info" )
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


print_tabs_info()



# 假设WebDriver已经初始化并打开了页面
# driver = webdriver.Chrome()  # 如果未初始化，可以取消注释此行

# 交互式选择下拉框的函数（部分代码）
def select_dropdown_interactively(select_id, label):
    try:
        # 1. 点击下拉框按钮，展开选项
        dropdown_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='{select_id}']/following-sibling::div[contains(@class, 'bootstrap-select')]//button"))
        )
        dropdown_button.click()
        logger.info(f"已点击{label}下拉框按钮，展开选项")

        # 2. 从<select>元素中获取所有<option>的value值
        select_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f"//select[@id='{select_id}']"))
        )
        select = Select(select_element)
        options = select.options
        value_to_index = {option.get_attribute("value"): idx for idx, option in enumerate(options)}

        # 3. 获取bootstrap-select生成的<li>元素
        li_elements = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, f"//select[@id='{select_id}']/following-sibling::div[contains(@class, 'bootstrap-select')]//ul/li"))
        )

        # 4. 打印li_elements的HTML内容
        print(f"\n{label}下拉框的<li>元素HTML内容：")
        for idx, li in enumerate(li_elements):
            # 使用get_attribute("outerHTML")获取元素的完整HTML
            li_html = li.get_attribute("outerHTML")
            print(f"选项 {idx + 1} HTML:\n{li_html}\n")

        # 5. 打印所有选项的value和文本（继续之前的逻辑）
        print(f"\n{label}选项列表：")
        options_data = []
        for idx, li in enumerate(li_elements):
            data_index = li.get_attribute("data-original-index")
            text = li.find_element(By.XPATH, ".//span[@class='text']").text.strip()
            value = next((val for val, index in value_to_index.items() if str(index) == data_index), None)
            if value is not None:
                options_data.append({"value": value, "text": text, "data_index": data_index})
                print(f"value: {value}, 文本: {text}")

        # 6. 等待用户输入value
        while True:
            user_value = input(f"\n请输入要选择的{label}value值（输入'q'退出）：").strip()
            if user_value.lower() == 'q':
                logger.info("用户选择退出")
                return None

            # 验证输入是否有效
            matching_option = next((option for option in options_data if option["value"] == user_value), None)
            if matching_option:
                break
            else:
                print(f"无效的value值：{user_value}，请重新输入！")

        # 7. 根据用户输入的value找到对应的data-original-index，并选择
        data_index = matching_option["data_index"]
        selected_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='{select_id}']/following-sibling::div[contains(@class, 'bootstrap-select')]//ul/li[@data-original-index='{data_index}']"))
        )
        selected_option.click()
        logger.info(f"成功选择{label}: value={user_value}, 文本={matching_option['text']}")
        return user_value

    except Exception as e:
        logger.error(f"交互式选择{label}失败，错误: {e}")
        return None

# 交互式选择代理商地区的函数
def select_agent_area_interactively():
    try:
        # 1. 选择省份
        selected_province = select_dropdown_interactively("province", "省份")
        if selected_province is None:
            return False

        # 2. 等待城市下拉框加载完成
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.XPATH, "//select[@id='city']/following-sibling::div[contains(@class, 'bootstrap-select')]//ul/li")) > 1,
            message="城市下拉框未加载完成或无可用选项"
        )

        # 3. 选择城市
        selected_city = select_dropdown_interactively("city", "城市")
        if selected_city is None:
            return False

        logger.info("代理商地区选择完成！")
        return True

    except Exception as e:
        logger.error(f"交互式选择代理商地区失败，错误: {e}")
        return False

# 执行交互式选择
try:
    if select_agent_area_interactively():
        logger.info("代理商地区选择完成！")
    else:
        logger.warning("代理商地区选择未完成")

except Exception as e:
    logger.error(f"执行过程中发生错误: {e}")

# 保持浏览器打开以便调试
# time.sleep(10)
# driver.quit()