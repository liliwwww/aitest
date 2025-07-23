from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Selenium，连接到已打开的Chrome调试模式
def init_driver():
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("成功连接到Chrome调试模式")
        return driver
    except Exception as e:
        logger.error(f"连接到Chrome调试模式失败: {e}")
        raise

# 根据定位类型和值定位元素
def locate_element(driver, locator_type, locator_value):
    locator_map = {
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "xpath": By.XPATH
    }
    if locator_type not in locator_map:
        raise ValueError(f"不支持的定位类型: {locator_type}，支持的类型: {list(locator_map.keys())}")

    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((locator_map[locator_type], locator_value))
        )
        return element
    except Exception as e:
        logger.error(f"定位元素失败: {locator_type}={locator_value}, 错误: {e}")
        return None

# 生成元素的XPath（简单实现）
def generate_xpath(element):
    try:
        tag = element.tag_name
        id_attr = element.get_attribute("id")
        name_attr = element.get_attribute("name")
        class_attr = element.get_attribute("class")

        if id_attr:
            return f"//{tag}[@id='{id_attr}']"
        elif name_attr:
            return f"//{tag}[@name='{name_attr}']"
        elif class_attr:
            return f"//{tag}[contains(@class, '{class_attr.split()[0]}')]"
        else:
            # 如果没有id、name、class，生成基于标签的XPath（可能不唯一）
            return f"//{tag}"
    except Exception as e:
        logger.error(f"生成XPath失败: {e}")
        return "未知XPath"

# 扫描页面上所有可交互控件
def list_interactive_controls(driver):
    try:
        # 定义控件类型和对应的XPath
        control_types = {
            "按钮": "//button | //input[@type='button' or @type='submit']",
            "文本框": "//input[@type='text' or @type='password' or @type='email']",
            "下拉框": "//select",
            "文本区域": "//textarea"
        }

        print("\n页面上可交互的控件列表：")
        print("格式: 控件类型 | id | name | class_name | xpath")
        print("-" * 50)

        for control_type, xpath in control_types.items():
            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                id_attr = element.get_attribute("id") or "无"
                name_attr = element.get_attribute("name") or "无"
                class_attr = element.get_attribute("class") or "无"
                element_xpath = generate_xpath(element)
                print(f"{control_type} | {id_attr} | {name_attr} | {class_attr} | {element_xpath}")

        print("-" * 50)

    except Exception as e:
        logger.error(f"扫描控件失败: {e}")
        print(f"错误: {e}")

# 点击按钮
def click_button(driver, locator_type, locator_value):
    element = locate_element(driver, locator_type, locator_value)
    if element:
        try:
            element.click()
            logger.info(f"成功点击按钮: {locator_type}={locator_value}")
        except Exception as e:
            logger.error(f"点击按钮失败: {locator_type}={locator_value}, 错误: {e}")

# 获取文本框或<textarea>的值
def get_text(driver, locator_type, locator_value):
    element = locate_element(driver, locator_type, locator_value)
    if element:
        try:
            text = element.get_attribute("value")
            logger.info(f"获取文本值: {locator_type}={locator_value}, 值: {text}")
            print(f"文本值: {text}")
        except Exception as e:
            logger.error(f"获取文本值失败: {locator_type}={locator_value}, 错误: {e}")

# 设置文本框或<textarea>的值
def set_text(driver, locator_type, locator_value, text):
    element = locate_element(driver, locator_type, locator_value)
    if element:
        try:
            element.clear()
            element.send_keys(text)
            logger.info(f"成功设置文本值: {locator_type}={locator_value}, 值: {text}")
        except Exception as e:
            logger.error(f"设置文本值失败: {locator_type}={locator_value}, 错误: {e}")

# 选择下拉框选项
def select_option(driver, locator_type, locator_value, value):
    element = locate_element(driver, locator_type, locator_value)
    if element:
        try:
            select = Select(element)
            select.select_by_value(value)
            logger.info(f"成功选择下拉框选项: {locator_type}={locator_value}, value={value}")
        except Exception as e:
            logger.error(f"选择下拉框选项失败: {locator_type}={locator_value}, 错误: {e}")

# 交互式命令行
def interactive_control(driver):
    print("\n欢迎使用Web控件控制程序！")
    print("支持的命令：")
    print("  list_controls - 列出页面上所有可交互控件")
    print("  click <locator_type> <locator_value> - 点击按钮，例如: click id myButton")
    print("  get_text <locator_type> <locator_value> - 获取文本框值，例如: get_text id myInput")
    print("  set_text <locator_type> <locator_value> <text> - 设置文本框值，例如: set_text id myInput Hello")
    print("  select <locator_type> <locator_value> <value> - 选择下拉框选项，例如: select id mySelect 1")
    print("  quit - 退出程序")

    while True:
        try:
            command = input("\n请输入命令：").strip()
            if not command:
                continue

            parts = command.split()
            action = parts[0].lower()

            if action == "quit":
                logger.info("用户选择退出")
                break

            elif action == "list_controls":
                list_interactive_controls(driver)

            elif action == "click" and len(parts) == 3:
                locator_type, locator_value = parts[1], parts[2]
                click_button(driver, locator_type, locator_value)

            elif action == "get_text" and len(parts) == 3:
                locator_type, locator_value = parts[1], parts[2]
                get_text(driver, locator_type, locator_value)

            elif action == "set_text" and len(parts) >= 4:
                locator_type, locator_value = parts[1], parts[2]
                text = " ".join(parts[3:])
                set_text(driver, locator_type, locator_value, text)

            elif action == "select" and len(parts) == 4:
                locator_type, locator_value, value = parts[1], parts[2], parts[3]
                select_option(driver, locator_type, locator_value, value)

            else:
                print("无效的命令！请参考支持的命令格式。")

        except Exception as e:
            logger.error(f"执行命令时发生错误: {e}")
            print(f"错误: {e}")

# 主程序
def main():
    try:
        driver = init_driver()
        interactive_control(driver)
    except Exception as e:
        logger.error(f"程序运行过程中发生错误: {e}")
    finally:
        # driver.quit()  # 调试模式下不关闭浏览器
        logger.info("程序退出")

if __name__ == "__main__":
    main()