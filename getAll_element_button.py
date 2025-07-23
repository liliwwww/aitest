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

def buttonClick( driver, by,xpath):

    print(f" %%%%BUTTON->buttonClick() xpath:{xpath}")
    # 列表button的按钮
    # xpath = "//table[@class='table table-bordered table-hover table-striped table-top']/tbody/tr[1]/td[9]/button"
    try:
        wait = WebDriverWait(driver, 2)
        element = wait.until(EC.element_to_be_clickable( (by, xpath) ))
        print(f"定位4元素：{element.tag_name}")
        element.click()

        #driver.execute_script("arguments[0].click();", element)

        #element.send_keys('张三四')
    except:
        print('Error1')

    try:
        print("找 sm_name的返回值")
        input_field = wait.until(EC.presence_of_element_located((By.ID, "sm_name")))
        value = input_field.get_attribute("value")
        print(f"点击后输入框值: {value}")
    except:
        print("找 sm_name的返回值失败")
    
    print("click ok")


##=============================
# # 主程序
def main():
    try:

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("成功连接到Chrome调试模式A")

        wait = WebDriverWait(driver, 10)

        try:

            ## 定位元素,在执行
            
            #xpath = "//*[@id='haha']"
            #idd = 'haha'
            #ele_Name = 'sm_name'

            # from page copy
            #/html/body/div[10]/div[2]/div[2]/div[2]/table/tbody/tr[3]/td[9]/button
            
            #列表button的按钮
            #xpath = "//table[@class='table table-bordered table-hover table-striped table-top']/tbody/tr[1]/td[9]/button"
            

            #页面上方查询按钮
            buttonPath = '//*[@id="pagerForm"]/div/p[4]/button'
            #buttonPath = "//*[@id='pagerForm'][@action='/yhbackstage/Salesman/findSales']/div/button"

            #buttonPath = "//*button[@class='btn btn-blue']"
            print("AAAA")
            element = wait.until(EC.element_to_be_clickable(
                (By.XPATH, buttonPath)
            ))
            print("BBBB")
            try:
                print(f"定位4元素：{element.tag_name}")
                #element.click()

                driver.execute_script("arguments[0].click();", element)

                #element.send_keys('张三四')
            except:
                print('Error1')

            try:
                print("找 sm_name的返回值")
                input_field = wait.until(EC.presence_of_element_located((By.ID, "sm_name")))
                value = input_field.get_attribute("value")
                print(f"点击后输入框值: {value}")
            except:
                print("找 sm_name的返回值失败")
            
            print("click ok")

        except Exception as dd:
            print(f"Error Error Error select date time error{dd}")

    except Exception as e:
        logger.error(f"脚本执行过程中发生未知错误: {e}")
    finally:
        # driver.quit()  # 根据需要决定是否关闭浏览器
        logger.info("程序退出")



if __name__ == "__main__":
    main()