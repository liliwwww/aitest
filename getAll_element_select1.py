from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging
import time
from selenium.webdriver.chrome.options import Options

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 定义通用的点击函数（使用ActionChains）
def click_element(step_name, by, locator, timeout=5, retries=2, use_action=True):
    attempt = 0
    while attempt <= retries:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )

            print(f"click_element tag_name::{ element.text }")
            if use_action:
                actions = ActionChains(driver)
                actions.move_to_element(element).click().perform()
                logger.info(f"{step_name} 使用ActionChains点击成功")
            else:
                element.click()
                logger.info(f"{step_name} 成功")
            return True
        except Exception as e:
            attempt += 1
            logger.warning(f"{step_name} 失败 (第 {attempt}/{retries+1} 次尝试)，错误: {e}")
            if attempt > retries:
                logger.error(f"{step_name} 最终失败，跳过此步骤")
                driver.save_screenshot(f"debug_{step_name}_{int(time.time())}.png")
                return False
            time.sleep(1)
    return False

# 等待原生<select>选项加载
def wait_for_select_options(step_name, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_element(By.ID, "agent_nature").find_elements(By.TAG_NAME, "option")) > 1
        )
        options = driver.find_element(By.ID, "agent_nature").find_elements(By.TAG_NAME, "option")
        
        print(f" 获得option的选项{ len(options)}")
        
        for opt in options:
            print( f"<opt>{opt.tag_name}" )
            logger.info(f"{step_name} - 原生<select>选项: value='{opt.get_attribute('value')}', text='{opt.text.strip()}'")
        logger.info(f"{step_name} - 原生<select>选项已加载")
        return True
    except Exception as e:
        logger.error(f"{step_name} - 原生<select>选项未加载，错误: {e}")
        driver.save_screenshot(f"debug_{step_name}_select_options_not_loaded.png")
        return False

# 等待bootstrap-select选项加载
def wait_for_options(step_name, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li")) > 1
        )
        options = driver.find_elements(By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li")
        for opt in options:
            text = opt.find_element(By.XPATH, ".//span[@class='text']").text.strip()
            logger.info(f"{step_name} - 选项: '{text}'")
        logger.info(f"{step_name} - 选项数据已加载")
        return True
    except Exception as e:
        logger.error(f"{step_name} - 选项数据未加载，错误: {e}")
        driver.save_screenshot(f"debug_{step_name}_options_not_loaded.png")
        return False

# 直接操作原生<select>
def set_select_value(step_name, index, timeout=5):
    try:
        select = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "agent_nature"))
        )
        driver.execute_script(f"""
            var select = arguments[0];
            select.value = '{index}';
            var event = new Event('change', {{ bubbles: true }});
            select.dispatchEvent(event);
            $(select).selectpicker('refresh');
        """, select)
        logger.info(f"{step_name} - 直接操作原生<select>成功，设置value='{index}'")
        time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"{step_name} - 直接操作原生<select>失败，错误: {e}")
        return False




# 定义下拉框选择函数
def select_dropdown(step_name, button_by, button_locator, option_by, option_locator, index, timeout=5, retries=2):
    # 点击下拉框按钮
    if not click_element(f"{step_name} - 点击下拉框", button_by, button_locator, timeout, retries):
        return False
    
    print("select_dropdown AAA")

    # 等待原生<select>选项加载
    if not wait_for_select_options(step_name, timeout=10):
        logger.warning(f"{step_name} - 原生<select>选项未加载，尝试直接操作")
        if set_select_value(step_name, index, timeout):
            return True
        return False

    print("select_dropdown BBB")
    
    # 验证下拉框是否打开
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]"))
        )
        logger.info(f"{step_name} - 下拉框已打开")
    except Exception as e:
        logger.error(f"{step_name} - 下拉框未保持打开状态，错误: {e}")
        return False

    print("select_dropdown CCC")

    # 等待bootstrap-select选项加载
    if not wait_for_options(step_name, timeout=10):
        logger.warning(f"{step_name} - bootstrap-select选项未加载，尝试直接操作原生<select>")
        if set_select_value(step_name, index, timeout):
            return True
        return False

    print("select_dropdown DDD")
    # 获取选项并打印文本
    try:
        option = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((option_by, option_locator))
        )
        html = option.get_attribute("outerHTML")
        logger.info(f"{step_name} - 选项HTML: {html}")
        text = option.find_element(By.XPATH, ".//span[@class='text']").text.strip()
        logger.info(f"{step_name} - 选项文本: '{text}'")

        if "请选择" in text:
            logger.warning(f"{step_name} - 选项仍为‘请选择’，尝试直接操作原生<select>")
            if set_select_value(step_name, index, timeout):
                return True
            return False

    except Exception as e:
        logger.error(f"{step_name} - 获取选项文本失败，错误: {e}")
        driver.save_screenshot(f"debug_{step_name}_text_empty.png")
        return False

    print("select_dropdown EEE")

    # 点击选项
    if not click_element(f"{step_name} - 选择选项", option_by, option_locator, timeout, retries, use_action=True):
        return False

    # 验证选择结果
    try:
        selected_text = driver.find_element(By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[1]").text.strip()
        logger.info(f"{step_name} - 当前选中值: '{selected_text}'")
    except Exception as e:
        logger.warning(f"{step_name} - 无法验证选中值，错误: {e}")

    return True

# 主程序
try:

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("成功连接到Chrome调试模式")

    wait = WebDriverWait(driver, 10)

    '''
    try:
        # Step 1: 点击第一个下拉框的选择项
        element1 = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "tr:nth-of-type(2) > td:nth-of-type(1) span.filter-option")
        ))

        ActionChains(driver).move_to_element_with_offset(element1, 16.78125, 10.5).click().perform()
        print("1")

        time.sleep(3)
        # Step 2: 点击下拉菜单中的第一个选项
        element2 = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "xpath//html/body/div[12]/div/ul/li[2]/a")
        ))
        ActionChains(driver).move_to_element_with_offset(element2, 21.78125, 5.5).click().perform()
        print("2")
        time.sleep(3)
        
        # Step 3: 点击下拉框的 caret（展开箭头）
        element3 = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "tr:nth-of-type(2) > td:nth-of-type(1) span.caret")
        ))
        ActionChains(driver).move_to_element_with_offset(element3, 6.78125, 1.5).click().perform()
        print("3")
        time.sleep(3)

        # Step 4: 点击下拉菜单中的第二个选项
        element4 = wait.until(EC.element_to_be_clickable(
            (By.XPATH,  "//html/body/div[12]/div/ul/li[2]/a")
        ))
        ActionChains(driver).move_to_element_with_offset(element4, 51.78125, 13.5).click().perform()
        print("4")
        time.sleep(3)
    finally:
        print("到这里了")
	'''
    '''
    step_name = "选省份"
    print("选省份")
    xpath = "//button[@class='btn dropdown-toggle selectpicker btn-default'][@data-id='province']/span"
    if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
        print("点击ok")

    xpath = "//div[@class='btn-group bootstrap-select required show-tick open']/div/ul/li[12]/a"
    if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
        print("点击ok")
    '''
    '''
    step_name = "选城市"
    print("选城市")
    xpath = "//button[@class='btn dropdown-toggle selectpicker btn-default'][@data-id='city']/span"
    if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
        print("点击ok")

    xpath = "//div[@class='btn-group bootstrap-select required show-tick open']/div/ul/li[3]/a"
    if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
        print("点击ok")
    '''
    
    step_name = "代理商性质"
    print("代理商性质")
    
    #liyun
    #xpath = "//button[@class='btn dropdown-toggle selectpicker btn-default'][@title='经销商']/span"

    #代码生成 
    # button/span[1]/span[2] 实际上是一样的
    xpath = "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]"

    if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
        print("点击ok")

    #liyun 给的，可用
    #liyun 给的，可用
    xpath = "//div[@class='btn-group bootstrap-select show-tick open']/div/ul/li[1]"
    
    #recorder
    #xpath = "//html/body/div[12]/div/ul/li[1]/a"
    if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
        print("点击ok")
    

    '''
    # Step 0 & 1: 选择“代理商性质”中的第一个选项（经销商）
    select_dropdown(
        "选择代理商性质为经销商",
        By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]",
        By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[@data-original-index='0']/a",
        index="0"
    )

    # Step 2 & 3: 选择“代理商性质”中的第二个选项（渠道商）
    select_dropdown(
        "选择代理商性质为渠道商",
        By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button",
        By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[@data-original-index='1']/a",
        index="1"
    )
    '''

    logger.info("脚本执行完成！")

except Exception as e:
    logger.error(f"脚本执行过程中发生未知错误: {e}")
finally:
    # driver.quit()  # 根据需要决定是否关闭浏览器
    logger.info("程序退出")