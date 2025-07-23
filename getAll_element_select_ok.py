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
    print(f"\n\n\nclick_element step_name::{ step_name } locator { locator } \n")
    attempt = 0
    while attempt <= retries:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            print(f">>>click_element xpath::{ locator }")
            print(f">>>click_element tag_name::{ element.text }")
            print(f">>>click_element html::{ element.get_attribute("outerHTML") }")
            
            

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

##=============================
def find_next_UlElement(by, locator ):
   
    print(f"find_next_UlElement>>>{ locator}")
    
    try:
        # 假设你已经导航到包含该 HTML 的页面
        # driver.get("你的目标URL")  # 请替换为实际 URL

        # 定位到指定的 ul 元素
        wait = WebDriverWait(driver, 1)
        print(f"找到了")
        
        ul_element = wait.until(EC.presence_of_element_located(
            (by, locator)
        ))
        print(f"找到了")
        ul_html = ul_element.get_attribute('outerHTML')
        print(f"UL 标签的 HTML 内容如下：{ul_html}")
        

        # 查找 ul 下所有的 li 元素
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

        # 遍历每个 li 元素，提取所需信息
        print("UL 下所有 LI 标签的信息：")
        for index, li in enumerate(li_elements, 1):
            # 获取 data-original-index 属性
            original_index = li.get_attribute('data-original-index')
            
            # 获取 <span class="text"> 的文本内容
            span_text = li.find_element(By.CSS_SELECTOR, 'span.text').text
            
            # 打印结果
            print(f"LI {index}:")
            print(f"  data-original-index: {original_index}")
            print(f"  span.text: {span_text}")

    except:
        # 关闭浏览器
        print("find_next_UlElement Error Error")

def find_next_ElementA( by, locator ):
   
    print(f"find_next_ElementA>>>{ locator}")
    
    try:
        
        try:
            print(">>>>>>")
            print(">>>>>>out All Div")
            print(">>>>>>")
            
            all_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'btn-group bootstrap-select show-tick')]")
            i=0
            for div in all_divs:
                print(f"\n  ---{i}---")
                i = i+1
                
                print(div.get_attribute('outerHTML'))
        except:
            print(">>>>>>out All Div OK")
        

        try:
            print(">>>>>>")
            print(">>>>>>直接找")
            print(">>>>>>")
            element = driver.find_element(
                By.XPATH, locator
            )
            print("98343")
            
            try:
                print(f"element1.tag{len(element)}")
            except:
                print("打印长度 异常")

            print(f"直接找>>>element2.tag{element.tag_name}")
            print(f"直接找>>>element3.tag{element.text}")   

            html = element.get_attribute('outerHTML')
            print(f"直接找>>>element3标签的 HTML 内容如下：{html}")
        except :
            print("直接找>>> 失败")

        
        print(">>>>>>")
        print(">>>>>>是否可见")
        print(">>>>>>")
        #xpath = "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]"
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (by, locator)
                ))
        print("2343")
        #print(f"element1.tag{len(element)}")
        print(f"element2.tag{element.tag_name}")
        print(f"element3.tag{element.text}")   

        html = element.get_attribute('outerHTML')
        print(f"element3标签的 HTML 内容如下：{html}")
        

    except Exception as e:
        # 关闭浏览器
        print("find_next_Element Error Error Error \n\n\n")

def func代理商性质():

    step_name = "AA代理商性质"
    print("代理商性质")
    
    #liyun
    #xpath = "//button[@class='btn dropdown-toggle selectpicker btn-default'][@title='经销商']/span"

    #代码生成 
    # button/span[1]/span[2] 实际上是一样的
    xpath = "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]"

    if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
        print("点击ok")

    #查看有个ul下，到底有多少个li    
    find_next_UlElement( By.XPATH, "//div[@class='btn-group bootstrap-select show-tick open']/div/ul")

    #liyun 给的，可用
    #liyun 给的，可用
    xpath = "//div[@class='btn-group bootstrap-select show-tick open']/div/ul/li[1]/a/span[2]"
    
    #recorder
    #xpath = "//html/body/div[12]/div/ul/li[1]/a"
    if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
        print("点击ok")


    #### attach test
    # 
    print(">>>")
    print(">>>")
    print(">>>")
    xpath = "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]"
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, xpath)
            ))
    print("2343")
    #print(f"element1.tag{len(element)}")
    print(f"element2.tag{element.tag_name}")
    print(f"element3.tag{element.text}")    

# 主程序
try:

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("成功连接到Chrome调试模式A")

    #wait = WebDriverWait(driver, 10)

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
    
    
    
    step_name = "代理商等级"
    print("step_name start")
    #xpath = "//button[@class='btn dropdown-toggle selectpicker btn-default']"
    
    # 可以
    # xpath = "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button"
    
    # 代理商性质
    xpath = "//button[@type='button'][@class='btn dropdown-toggle selectpicker btn-default'][@data-id='agent_level']/span[2]"
    
    #xpath = "//div[@class='btn-group bootstrap-select show-tick open']/div/ul/li[1]/a/span[2]"
    #xpath = "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]"
    #xpath = "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button"

    #先找到下拉框
    #find_next_ElementA( By.XPATH, xpath)
    #查看有个ul下，到底有多少个li    
    
    #点一下
    #if not click_element(f"{step_name} - 点击下拉框", By.XPATH, xpath, 10, 1):
    #    print("点击ok")

    #找到ul 下面有几个ul
    xpath = "//div[@class='btn-group bootstrap-select show-tick open']/div/ul"
    #find_next_UlElement(By.XPATH, xpath )
    find_next_ElementA(By.XPATH, xpath )
    
    #func代理商性质()

    #func代理商性质()

    logger.info("脚本执行完成！")

except Exception as e:
    logger.error(f"脚本执行过程中发生未知错误: {e}")
finally:
    # driver.quit()  # 根据需要决定是否关闭浏览器
    logger.info("程序退出")