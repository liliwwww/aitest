from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging
import time
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from dateutil.relativedelta import relativedelta  # 需要安装 python-dateutil 包


# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


##=========不能处理有效期====================

def get_validation_errorsA(driver):
    """
    获取页面中所有校验失败的输入控件及其对应的label文本
    参数:
        driver: 已初始化的WebDriver实例
    返回:
        dict: 键为label文本，值为对应的input控件name属性
    """
    # 存储结果的字典
    error_fields = {}
    
    # 查找所有包含label和input的p元素
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    
    for p in paragraphs:
        try:
            # 获取label文本
            label = p.find_element(By.TAG_NAME, "label")
            label_text = label.text.strip()  # 去除首尾空格
            
            # 检查是否有可见的错误span
            error_span = p.find_element(By.CSS_SELECTOR, "span.msg-wrap.n-error")
            is_visible = error_span.is_displayed()  # 检查span是否可见
            
            if is_visible:
                # 获取对应的input控件
                input_elem = p.find_element(By.TAG_NAME, "input")
                input_name = input_elem.get_attribute("name")
                
                # 将校验失败的字段添加到结果中
                error_fields[label_text] = input_name
        except:
            # 如果某个p元素结构不完整，跳过
            continue
    
    # 打印结果
    if error_fields:
        print("发现以下校验失败的字段：")
        for label, name in error_fields.items():
            print(f"字段: {label} (name={name})")
    else:
        print("未发现校验失败的字段")
    
    return error_fields


############################

def get_validation_errors(driver):
    """获取页面中所有校验失败的字段"""
    error_fields = {}
    
    # 处理<p>结构
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    for p in paragraphs:
        try:
            label = p.find_element(By.TAG_NAME, "label")
            label_text = label.text.strip()
            error_span = p.find_element(By.CSS_SELECTOR, "span.msg-wrap.n-error")
            if error_span.is_displayed():
                input_elem = p.find_element(By.TAG_NAME, "input")
                input_name = input_elem.get_attribute("name")
                error_fields[label_text] = input_name
        except:
            continue
     # 处理<td>结构（有效期）
    table_cells = driver.find_elements(By.TAG_NAME, "td")
    for td in table_cells:
        try:
            label = td.find_element(By.TAG_NAME, "label")
            label_text = label.text.strip()
            if label_text == "有效期:":
                begin_valid_input = td.find_element(By.NAME, "begin_valid")
                begin_error_span = td.find_element(By.CSS_SELECTOR, "span[for='begin_valid'] span.msg-wrap.n-error")
                if begin_error_span.is_displayed():
                    error_fields["开始有效期"] = "begin_valid"
                
                end_valid_input = td.find_element(By.NAME, "end_valid")
                end_error_span = td.find_element(By.CSS_SELECTOR, "span[for='end_valid'] span.msg-wrap.n-error")
                if end_error_span.is_displayed():
                    error_fields["结束有效期"] = "end_valid"
        except:
            continue
    
    if error_fields:
        print("发现以下校验失败的字段：")
        for label, name in error_fields.items():
            print(f"字段: {label} (name={name})")
    else:
        print("未发现校验失败的字段")
    
    return error_fields    

# 主程序
try:

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("成功连接到Chrome调试模式A")

    #wait = WebDriverWait(driver, 10)
    
    try:
        get_validation_errors(driver)

        
        print("get page_response date time ok")

    except Exception as dd:
        print("Error Error Error get page_response error")

except Exception as e:
    logger.error(f"脚本执行过程中发生未知错误: {e}")
finally:
    # driver.quit()  # 根据需要决定是否关闭浏览器
    logger.info("程序退出")