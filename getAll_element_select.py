from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
import time

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



# 定义一个通用的点击函数，带重试和异常处理
def click_element(driver,step_name, by, locator, timeout=5, retries=2):
    print(f"click_element{step_name}{by}{locator}")
    time.sleep(1)
    
    attempt = 0
    while attempt <= retries:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            element.click()
            logger.info(f"{step_name} 成功")
            return True
        except Exception as e:
            attempt += 1
            logger.warning(f"{step_name} 失败 (第 {attempt}/{retries+1} 次尝试)，错误: {e}")
            if attempt > retries:
                logger.error(f"{step_name} 最终失败，跳过此步骤")
                return False
            time.sleep(1)  # 等待1秒后重试
    return False

# 定义一个通用的下拉框选择函数，带异常处理
def select_dropdown(driver,step_name, button_by, button_locator, option_by, option_locator, timeout=5, retries=2):
    print(f"select_dropdown{step_name}{button_by}{button_locator}{option_by}{option_locator}")
    time.sleep(1)
    # 点击下拉框按钮
    if not click_element(f"{step_name} - 点击下拉框", button_by, button_locator, timeout, retries):
        return False
    # 选择选项
    return click_element(f"{step_name} - 选择选项", option_by, option_locator, timeout, retries)

# 定义一个通用的Select选择函数，带异常处理
def select_value(driver,step_name, by, locator, value, timeout=5, retries=2):
    print(f"select_value{step_name}{by}{locator}{value}")
    time.sleep(1)
    attempt = 0
    while attempt <= retries:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            select = Select(element)
            select.select_by_value(value)
            logger.info(f"{step_name} 成功，选择值: {value}")
            return True
        except Exception as e:
            attempt += 1
            logger.warning(f"{step_name} 失败 (第 {attempt}/{retries+1} 次尝试)，错误: {e}")
            if attempt > retries:
                logger.error(f"{step_name} 最终失败，跳过此步骤")
                return False
            time.sleep(1)
    return False



def set_Recorder(driver):


    try:
        

        # Step 2 & 3: 选择“代理商性质”中的第一个选项（经销商）
        select_dropdown(driver,
            "选择代理商性质",
            By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[2]/p[1]/div/button/span[2]",
            By.XPATH, "//div[@class='btn-group bootstrap-select show-tick open']/div/ul/li[2]"
        )
        
        # Step 4 & 5: 选择“代理商地区”中的第二个选项
        select_dropdown(driver,
            "选择代理商地区",
            By.XPATH, "//*[@id='myForm1']/fieldset[2]/table/tbody/tr[1]/td[1]/div/button/span[1]",
            By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[2]/a/span[1]"
        )
        
        # Step 6: 点击“总行名称”查找按钮
        click_element(driver,"点击‘总行名称’查找按钮", By.ID, "sz")

        # Step 7: 点击对话框中的搜索按钮
        click_element(driver,"点击‘总行名称’对话框中的搜索按钮", By.XPATH, "//*[@id='pagerForm']/div/button")

        # Step 8: 选择对话框中的第一行数据
        click_element(driver,"选择‘总行名称’对话框中的第一行数据", By.XPATH, "//html/body/div[12]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[2]/button")

        # Step 9: 点击“销售经理”查找按钮
        click_element(driver,"点击‘销售经理’查找按钮", By.ID, "haha1")
        
        # Step 10 & 11: 选择“销售经理”对话框中的第一个下拉框的第二个选项
        select_dropdown(driver,
            "选择‘销售经理’第一个下拉框",
            By.XPATH, "//*[@id='pagerForm']/div/div[1]/button/span[2]",
            By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[2]/a/span[1]"
        )

        # Step 12 & 13: 选择“销售经理”对话框中的第二个下拉框的第二个选项
        select_dropdown(driver,
            "选择‘销售经理’第二个下拉框",
            By.XPATH, "//*[@id='pagerForm']/div/div[2]/button/span[1]",
            By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[2]/a/span[1]"
        )

        # Step 14 & 15: 选择“销售经理”对话框中的第三个下拉框的第一个选项
        select_dropdown(driver,
            "选择‘销售经理’第三个下拉框（第一次）",
            By.XPATH, "//*[@id='pagerForm']/div/div[3]/button/span[1]",
            By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[1]/a/span[1]"
        )

        # Step 16 & 17: 再次选择“销售经理”对话框中的第三个下拉框的第二个选项
        select_dropdown(driver,
            "选择‘销售经理’第三个下拉框（第二次）",
            By.XPATH, "//*[@id='pagerForm']/div/div[3]/button/span[1]",
            By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[2]/a/span[1]"
        )

        # Step 18: 点击“销售经理”对话框中的搜索按钮
        click_element(driver,"点击‘销售经理’对话框中的搜索按钮", By.XPATH, "//*[@id='pagerForm']/div/button")

        # Step 19: 选择“销售经理”对话框中的第一行数据
        click_element(driver,"选择‘销售经理’对话框中的第一行数据", By.XPATH, "//html/body/div[12]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[9]/button")

        # Step 20: 点击“运营经理”查找按钮
        click_element(driver,"点击‘运营经理’查找按钮", By.ID, "haha")

        # Step 21: 点击“运营经理”对话框中的搜索按钮
        click_element(driver,"点击‘运营经理’对话框中的搜索按钮", By.XPATH, "//*[@id='pagerForm']/div/button")

        # Step 22: 选择“运营经理”对话框中的第一行数据
        click_element(driver,"选择‘运营经理’对话框中的第一行数据", By.XPATH, "//html/body/div[12]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[9]/button")
        
        
        
        # Step 23: 点击“开始日期”选择器
        click_element(driver,"点击‘开始日期’选择器", By.XPATH, "//*[@id='myForm1']/fieldset[3]/table/tbody/tr[2]/td/span[1]/a/i")

        # Step 24 & 25: 更改年份为2023
        click_element(driver,"点击年份下拉框", By.XPATH, "//*[@id='bjui-calendar']/div/div[1]/table/tbody/tr/td[2]/select")
        select_value(driver,"更改年份为2023", By.XPATH, "//*[@id='bjui-calendar']/div/div[1]/table/tbody/tr/td[2]/select", "2023")

        # Step 26: 选择11月
        click_element(driver,"选择11月", By.XPATH, "//*[@id='bjui-calendar']/div/div[2]/dl[2]/dd[11]")

        # Step 27: 点击“结束日期”选择器
        click_element(driver,"点击‘结束日期’选择器", By.XPATH, "//*[@id='myForm1']/fieldset[3]/table/tbody/tr[2]/td/span[3]/a/i")

        # Step 28: 选择12月
        click_element(driver,"选择12月", By.XPATH, "//*[@id='bjui-calendar']/div/div[2]/dl[2]/dd[24]")

        # Step 29: 点击“下一步”按钮
        click_element(driver,"点击‘下一步’按钮", By.ID, "btn")
        
        logger.info("脚本执行完成！")

    except Exception as e:
        logger.error(f"脚本执行过程中发生未知错误: {e}")
    finally:
        # driver.quit()  # 根据需要决定是否关闭浏览器
        logger.info("程序退出")

def set_select( driver ):
    try:
        print("step1")
        # Step 2: 点击下拉框按钮
        dropdown_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]"))
        )
        dropdown_button.click()
        logger.info("点击下拉框按钮，展开选项")

        print("step2")
        # Step 3: 选择第一个选项（经销商）
        first_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//html/body/div[9]/div/ul/li[1]/a"))
        )
        first_option.click()
        logger.info("选择第一个选项（经销商）")

        # Step 4: 再次点击下拉框按钮
        print("step3")
        dropdown_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]"))
        )
        dropdown_button.click()
        logger.info("再次点击下拉框按钮，展开选项")

        print(f"step4{ dropdown_button.tag_name }")

        # Step 5: 选择第二个选项（渠道商）
        second_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//html/body/div[9]/div/ul/li[2]/a"))
        )
        second_option.click()
        logger.info("选择第二个选项（渠道商）")

    except Exception as e:
        logger.error(f"脚本执行失败: {e}")



def interact_with_dropdown(driver):
    try:
        # 假设下拉框的<select>元素id为"agent_type"，根据实际情况调整
        select_id = "agent_type"

        # 1. 点击下拉框按钮，展开选项
        dropdown_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='{select_id}']/following-sibling::div[contains(@class, 'bootstrap-select')]//button"))
        )
        dropdown_button.click()
        logger.info("已点击下拉框按钮，展开选项")

        # 2. 获取所有选项（<li>元素）
        li_elements = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, f"//select[@id='{select_id}']/following-sibling::div[contains(@class, 'bootstrap-select')]//ul/li"))
        )

        # 3. 打印所有选项的data-original-index和文本值
        print("\n下拉框选项列表：")
        options_data = []
        for li in li_elements:
            data_index = li.get_attribute("data-original-index")
            text = li.find_element(By.XPATH, ".//span[@class='text']").text.strip()
            options_data.append({"data_index": data_index, "text": text})
            print(f"data-original-index: {data_index}, 文本: {text}")

        # 4. 等待用户输入data-original-index
        while True:
            user_input = input("\n请输入要选择的data-original-index值（输入'q'退出）：").strip()
            if user_input.lower() == 'q':
                logger.info("用户选择退出")
                return False

            # 验证输入是否有效
            if any(option["data_index"] == user_input for option in options_data):
                break
            else:
                print(f"无效的data-original-index值：{user_input}，请重新输入！")

        # 5. 根据用户输入选择对应的选项
        selected_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='{select_id}']/following-sibling::div[contains(@class, 'bootstrap-select')]//ul/li[@data-original-index='{user_input}']"))
        )
        selected_text = next(option["text"] for option in options_data if option["data_index"] == user_input)
        selected_option.click()
        logger.info(f"成功选择选项: data-original-index={user_input}, 文本={selected_text}")
        return True

    except Exception as e:
        logger.error(f"操作下拉框失败，错误: {e}")
        return False



















#########===================================



# 定义通用的点击函数，带重试和异常处理
def click_elementA(driver, step_name, by, locator, timeout=5, retries=2):
    attempt = 0
    while attempt <= retries:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            element.click()
            logger.info(f"{step_name} 成功")
            return True
        except Exception as e:
            attempt += 1
            logger.warning(f"{step_name} 失败 (第 {attempt}/{retries+1} 次尝试)，错误: {e}")
            if attempt > retries:
                logger.error(f"{step_name} 最终失败，跳过此步骤")
                return False
            time.sleep(1)  # 等待1秒后重试
    return False

# 定义通用的下拉框选择函数
def select_dropdownA(driver,step_name, button_by, button_locator, option_by, option_locator, timeout=5, retries=2):
    # 点击下拉框按钮
    if not click_elementA(driver,f"{step_name} - 点击下拉框", button_by, button_locator, timeout, retries):
        return False
    # 选择选项
    return click_elementA(driver,f"{step_name} - 选择选项", option_by, option_locator, timeout, retries)

def update1(driver):

    print("update 1111")
    # 主程序
    try:
        # 点击下拉框按钮
        click_elementA(driver,"点击‘代理商性质’下拉框", By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]")

        # 添加延迟，等待选项加载
        time.sleep(1)  # 临时添加，用于调试

        # 检查选项是否出现在DOM中
        try:
            option = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[@data-original-index='0']/a"))
            )
            html = option.get_attribute("outerHTML")
            logger.info(f"选项HTML: {html}")
            text = option.text.strip()
            logger.info(f"选项文本: '{text}'")
            if not text:
                # 尝试从子元素获取文本
                span_text = option.find_element(By.XPATH, ".//span[@class='text']").text.strip()
                logger.info(f"从<span class='text'>获取的文本: '{span_text}'")
        except Exception as e:
            logger.error(f"获取选项文本失败，错误: {e}")
            driver.save_screenshot("debug_option_text_empty.png")



        # Step 2 & 3: 选择“代理商性质”中的第一个选项（经销商）
        select_dropdownA(driver,
            "选择代理商性质为经销商",
            By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button",
            By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[1]/a/span[1]"
        )

        print(";;;;;;;;;;;;;;;;;;;;;;;")

        # Step 4 & 5: 选择“代理商性质”中的第二个选项（渠道商）
        select_dropdownA(driver,
            "选择代理商性质为渠道商",
            By.XPATH, "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button",
            By.XPATH, "//div[contains(@class, 'dropdown-menu') and contains(@class, 'open')]//ul/li[2]/a/span[1]"
        )

        logger.info("脚本执行完成！")

    except Exception as e:
        logger.error(f"脚本执行过程中发生未知错误: {e}")
    finally:
        # driver.quit()  # 根据需要决定是否关闭浏览器
        logger.info("程序退出")


# 主程序
def main():
    try:
        driver = init_driver()

        set_Recorder(driver)
        #update1(driver)
        '''
        # 执行交互式选择
        try:
            if interact_with_dropdown(driver):
                logger.info("下拉框选择完成！")
            else:
                logger.warning("下拉框选择未完成")

        except Exception as e:
            logger.error(f"执行过程中发生错误: {e}")
        '''
    except Exception as e:
        logger.error(f"程序运行过程中发生错误: {e}")
    finally:
        # driver.quit()  # 调试模式下不关闭浏览器
        logger.info("程序退出")

if __name__ == "__main__":
    main()