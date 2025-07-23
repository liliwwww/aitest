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


##=============================

# 主程序
try:

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("成功连接到Chrome调试模式A")

    wait = WebDriverWait(driver, 10)
    
    try:
        '''
        print("找 sm_nameA的返回值")
        try:
            
            input_field = wait.until(EC.presence_of_element_located((By.ID, "sm_name")))
            value = input_field.get_attribute("value")
            print(f"点击后输入框值: {value}")
        except:
            print("找 sm_name的返回值失败")
        
        print("找 sm_nameB的返回值")
        try:
            
            input_field = wait.until(EC.presence_of_element_located((By.NAME, "t2.sm_name")))
            value = input_field.get_attribute("value")
            print(f"点击后输入框值: {value}")
        except:
            print("找 sm_name的返回值失败")
        
        print("start ok")
        ''' 
        ##step1， 点查询按钮
        
        '''
        print("\n\n##step1， 点查询按钮")
        xpath = "//*[@id='haha1']"
        element = wait.until(EC.element_to_be_clickable((By.ID, 'haha1')))


        #element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        try:
            print(f"定位1元素：{element.tag_name}")
            #无论用ID还是用XPath，都不能用click
            #element.click()
            driver.execute_script("arguments[0].click();", element)

        except:
            print('Error1dd')
        
        
        ##step2， 输入张三
        
        time.sleep(1)
        print("\n\n##step2， 输入张三丰")
        xpath = "//*[@name='sm_name']"
        input_field = wait.until(EC.presence_of_element_located((By.NAME, 'sm_name')))
        input_field.send_keys("张三")
        '''

        ##step3， 点击查询
        time.sleep(3)
        print("\n\n##step3， 点击查询")
        xpath = "//*[@id='pagerForm'][@action='/yhbackstage/Salesman/findSales']/div/button"
        element1 = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        try:
            print(f"定位3元素：{element1.tag_name}")
            element1.click()
        except:
            print('Error3')


        ##step4， 按第一行按钮
        
        time.sleep(1)
        print("\n\n##step4， 按第一行按钮")
       
        #列表button的按钮
        xpath = "//table[@class='table table-bordered table-hover table-striped table-top']/tbody/tr[1]/td[9]/button"
        
        element2 = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        try:
            print(f"定位4元素：{element2.tag_name}")
            element2.click()

           # driver.execute_script("arguments[0].click();", element)

            #element.send_keys('张三四')
        except:
            print('Error4')
        

        

        print("找e sm_nameA的返回值")
        try:
            time.sleep(3)
            input_field = wait.until(EC.presence_of_element_located((By.ID, "sm_name")))
            value = input_field.get_attribute("value")
            print(f"点击后输入框值: {value}")
        except:
            print("找 sm_name的返回值失败")

        print("找 sm_nameB的返回值")
        try:
            
            input_field = wait.until(EC.presence_of_element_located((By.NAME, "t2.sm_name")))
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