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

# 智能切换到 DeepSeek 页面
def switch_to_deepseek_tab():
    print("start1->switch_to_deepseek_tab" )
    window_handles = driver.window_handles
    print(f"所有标签页句柄：{window_handles}")
    for handle in window_handles:
        driver.switch_to.window(handle)
        time.sleep(1)
        current_url = driver.current_url
        print(f"当前标签页 URL: {current_url}")
        if "damai.cn" in current_url.lower():  # 修改为 damai.cn
            print(f"找到大麦网页面：{current_url}")
            driver.execute_script("window.focus();")
            driver.maximize_window()
            return True
    print("未找到大麦网页面，请确保已打开")
    return False

# 滚动页面加载更多内容
def scroll_to_load_more():
    print("start1->scroll_to_load_more" )
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待加载
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# 提取页面中的项目名称和 URL
def extract_project_urls():
    project_urls = {}  # 使用字典去重，key 为项目名称，value 为 URL

    try:
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 滚动页面加载更多内容
        print("滚动页面以加载更多内容...")
        scroll_to_load_more()

        # 获取页面基础 URL（用于将相对路径转换为绝对路径）
        base_url = driver.current_url

        # 1. 提取分类导航中的项目和 URL
        print("\n提取分类导航中的项目...")
        try:
            nav_elements = driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'nav')]//a | //div[contains(@class, 'category')]//a"
            )
            for element in nav_elements:
                name = element.text.strip()
                href = element.get_attribute("href")
                if name and href:
                    href = urljoin(base_url, href)  # 转换为绝对路径
                    project_urls[name] = href
                    print(f"--->分类导航项目：{name}, URL: {href}")
        except Exception as e:
            print(f"提取分类导航失败：{e}")

        # 2. 提取活动列表中的项目和 URL
        print("\n提取活动列表中的项目...")
        try:
            activity_elements = driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'item')]//a | //div[contains(@class, 'event')]//a"
            )
            for element in activity_elements:
                name = element.text.strip()
                href = element.get_attribute("href")
                if name and href:
                    href = urljoin(base_url, href)  # 转换为绝对路径
                    project_urls[name] = href
                    print(f"--->活动列表项目：{name}, URL: {href}")
        except Exception as e:
            print(f"提取活动列表失败：{e}")

        # 3. 提取推荐活动中的项目和 URL
        print("\n提取推荐活动中的项目...")
        try:
            banner_elements = driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'banner')]//a | //div[contains(@class, 'promo')]//a"
            )
            for element in banner_elements:
                name = element.text.strip()
                href = element.get_attribute("href")
                if name and href:
                    href = urljoin(base_url, href)  # 转换为绝对路径
                    project_urls[name] = href
                    print(f"--->推荐活动项目：{name}, URL: {href}")
        except Exception as e:
            print(f"提取推荐活动失败：{e}")

        # 4. 输出结果
        print("\n=== 项目名称和 URL 列表 ===")
        for name, url in project_urls.items():
            print(f"{name}，url：{url}")

        # 5. 保存到文件（可选）
        with open("project_urls.txt", "w", encoding="utf-8") as f:
            for name, url in project_urls.items():
                f.write(f"{name}，url：{url}\n")

    except Exception as e:
        print(f"Error extracting project URLs: {e}")

# 打印所有标签页信息
print_tabs_info()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 假设WebDriver已经初始化并打开了页面
# driver = webdriver.Chrome()  # 如果未初始化，可以取消注释此行

# 测试数据
test_data = {
    "agent_name": "测试代理商有限公司",  # 代理商名称
    "agent_nature": "0",  # 代理商性质: 经销商
    "province": "2200",  # 代理商地区: 北京市
    "city": "2210",    # 假设为朝阳区，具体值需根据实际动态加载结果调整
    "commissary": "张三",  # 法人名称
    "link_man": "李四",  # 联系人姓名
    "link_email": "test@example.com",  # 联系人邮箱
    "organ_code": "91110108MA12345678",  # 统一社会信用代码
    "agent_level": "1",  # 代理商等级: 一级代理商
    "agent_area": "北京市朝阳区测试路123号",  # 详细地址
    "identity_num": "110101199001011234",  # 法人身份证号码
    "link_phone": "13812345678",  # 手机号码
    "deposit_money": "50",  # 保证金金额(万元)
    "nature": "1",  # 账户类型: 对公
    "screen_name": "测试代理商有限公司",  # 开户账户名称
    "screen_num": "6222021234567890123",  # 开户银行账户
    "begin_valid": "2025-04-07",  # 有效期开始日期
    "end_valid": "2026-04-07",  # 有效期结束日期
    "admin_name": "agent_test_001"  # 代理商登录账号
}

# 字段与XPath的映射（不包含代理商地区，因为单独处理）
field_mappings = [
    {"name": "代理商名称", "xpath": "//input[@id='agent_name']", "value": test_data["agent_name"], "type": "input", "status": None},
    {"name": "代理商性质", "xpath": "//select[@id='agent_nature']", "value": test_data["agent_nature"], "type": "select", "status": None},
    {"name": "法人名称", "xpath": "//input[@id='commissary']", "value": test_data["commissary"], "type": "input", "status": None},
    {"name": "联系人姓名", "xpath": "//input[@id='link_man']", "value": test_data["link_man"], "type": "input", "status": None},
    {"name": "联系人邮箱", "xpath": "//input[@id='link_email']", "value": test_data["link_email"], "type": "input", "status": None},
    {"name": "统一社会信用代码", "xpath": "//input[@id='organ_code']", "value": test_data["organ_code"], "type": "input", "status": None},
    {"name": "代理商等级", "xpath": "//select[@id='agent_level']", "value": test_data["agent_level"], "type": "select", "status": None},
    {"name": "详细地址", "xpath": "//input[@id='agent_area']", "value": test_data["agent_area"], "type": "input", "status": None},
    {"name": "法人身份证号码", "xpath": "//input[@id='identity_num']", "value": test_data["identity_num"], "type": "input", "status": None},
    {"name": "手机号码", "xpath": "//input[@id='link_phone']", "value": test_data["link_phone"], "type": "input", "status": None},
    {"name": "保证金金额(万元)", "xpath": "//input[@id='deposit_money']", "value": test_data["deposit_money"], "type": "input", "status": None},
    {"name": "账户类型", "xpath": "//select[@id='nature']", "value": test_data["nature"], "type": "select", "status": None},
    {"name": "开户账户名称", "xpath": "//input[@id='screen_name' and contains(@class, 'a1')]", "value": test_data["screen_name"], "type": "input", "status": None},
    {"name": "开户银行账户", "xpath": "//input[@id='screen_num' and contains(@class, 'a1')]", "value": test_data["screen_num"], "type": "input", "status": None},
    {"name": "有效期开始日期", "xpath": "//input[@name='begin_valid']", "value": test_data["begin_valid"], "type": "input", "status": None},
    {"name": "有效期结束日期", "xpath": "//input[@name='end_valid']", "value": test_data["end_valid"], "type": "input", "status": None},
    {"name": "代理商登录账号", "xpath": "//input[@id='admin_name1']", "value": test_data["admin_name"], "type": "input", "status": None}
]

# 选择代理商地区的函数（处理bootstrap-select）
def select_agent_area(province_val, city_val):
    print("okok")
    try:
        # 1. 选择省份
        # 找到省份的bootstrap-select按钮
        province_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//select[@id='province']/following-sibling::div[contains(@class, 'bootstrap-select')]//button"))
        )
        province_button.click()

        # 选择省份选项
        province_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='btn-group.bootstrap-select.required.show-tick.open']/div/ul/li[index='4']/a"))
        )
        province_option.click()
        logger.info(f"成功选择省份: {province_val} (北京市)")

        # 2. 等待城市下拉框加载完成
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.XPATH, "//select[@id='city']/following-sibling::div[contains(@class, 'bootstrap-select')]//ul/li")) > 1,
            message="城市下拉框未加载完成或无可用选项"
        )

        # 3. 选择城市
        city_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/ul/li[2]/a"))
        )
        city_button.click()

        # 打印所有城市选项以便调试
        city_options = driver.find_elements(By.XPATH, "//select[@id='city']/following-sibling::div[contains(@class, 'bootstrap-select')]//ul/li")
        city_values = [option.get_attribute("data-original-index") for option in city_options]
        logger.info(f"城市选项: {city_values}")

        # 选择城市（假设城市值的data-original-index与value对应）
        city_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='city']/following-sibling::div[contains(@class, 'bootstrap-select')]//ul/li/a[contains(@data-normalized-text, '朝阳')]"))
        )
        city_option.click()
        logger.info(f"成功选择城市: 朝阳区")

    except Exception as e:
        logger.error(f"选择代理商地区失败，错误: {e}")

# 填写单个字段的函数
def fill_field(field):
    name = field["name"]
    xpath = field["xpath"]
    value = field["value"]
    field_type = field["type"]

    try:
        # 等待元素可见
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        if field_type == "input":
            element.clear()  # 清空现有内容
            element.send_keys(value)
            logger.info(f"成功填写字段 '{name}': {value}")
            field["status"] = "success"
        elif field_type == "select":
            select = Select(element)
            select.select_by_value(value)
            logger.info(f"成功选择字段 '{name}': {value}")
            field["status"] = "success"

    except Exception as e:
        logger.error(f"填写字段 '{name}' 失败，XPath: {xpath}，错误: {e}")
        field["status"] = "failed"

# 填写表单函数
def fill_form():
    # 1. 填写其他字段
    for field in field_mappings:
        fill_field(field)

    # 2. 单独处理代理商地区
    select_agent_area(test_data["province"], test_data["city"])

    # 检查失败的字段
    failed_fields = [field["name"] for field in field_mappings if field["status"] == "failed"]
    if failed_fields:
        logger.warning(f"以下字段填写失败: {failed_fields}")
    else:
        logger.info("所有字段填写完成！")

# 执行填写表单
try:
    fill_form()

    # 可选：点击“下一步”按钮提交表单
    # submit_button = WebDriverWait(driver, 5).until(
    #     EC.element_to_be_clickable((By.XPATH, "//button[@id='btn']"))
    # )
    # submit_button.click()
    # logger.info("已点击'下一步'按钮")

except Exception as e:
    logger.error(f"执行过程中发生错误: {e}")

# 保持浏览器打开以便调试
# time.sleep(10)
# driver.quit()