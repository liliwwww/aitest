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
from getAll_element_button import buttonClick

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##==new code====

def process_table_B(dirver, table_xpath):


    # 检查是否有 iframe
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print(f"找到 {len(iframes)} 个 iframe，尝试切换")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                table = driver.find_element(By.XPATH, table_xpath)
                tbody = driver.find_element(By.XPATH, table_xpath + "//tbody")
                print("在 iframe 中找到 tbody")
                break
            except:
                driver.switch_to.default_content()  # 切换回主文档
    else:
        print("未找到 iframe")
        
    # 表格的 XPath
    # table_xpath = "//table[@class='table table-bordered']"

    # 定位表格
    #table = driver.find_element(By.XPATH, table_xpath)
    wait = WebDriverWait(driver, 3)
    table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    
    print('\n\n\nAAAA\n\n\n')
    print(f"find talbe outerHTML: {table.get_attribute('outerHTML')}")
    print('\n\n\nBBBB\n\n\n')

    # 提取表头
    thead = table.find_element(By.XPATH, ".//thead")
    header_row = thead.find_elements(By.XPATH, ".//tr[2]/th")  # 第二个 tr 是实际表头
    headers = [th.find_element(By.XPATH, ".//div[@class='fixedtableCol']").text.strip() for th in header_row]

    # 打印表头
    print("表头:")
    print(" | ".join(headers))
    print("-" * 100)

    # 提取 tbody 中的内容
    # tbody = table.find_element(By.XPATH, ".//tbody")

    # 高级用法定位 tbody

    
    tbody_xpath =  table_xpath + "/tbody"

    tbody = driver.execute_script("return document.querySelector('table.table.table-bordered tbody')")
    if tbody:
        print("通过 JavaScript 找到 tbody")
    else:
        print("JavaScript 也未找到 tbody")
        
    #//*[@id='bjui-navtab']/div[2]/div[2]/div[2]/div/div[1]/div/table/tbody 
    
    
    #print(f"wait tbody {tbody_xpath}")
    #tbody = WebDriverWait(driver, 10).until(
    #    EC.presence_of_element_located((By.XPATH,tbody_xpath))
    #)
    print(f"wait tr YES")

    rows = tbody.find_elements(By.XPATH, ".//tr")

    print(f"wait tr YES")

    # 遍历每一行并打印每个单元格内容
    print("表格内容:")
    for row_idx, row in enumerate(rows, 1):
        print(f"\n行 {row_idx}:")
        cells = row.find_elements(By.XPATH, ".//td")
        for col_idx, cell in enumerate(cells):
            # 获取单元格的文本内容
            cell_text = cell.text.strip()
            # 如果是第一列（radio），简化为 "Radio Button"
            if col_idx == 0:
                cell_text = "Radio Button"
            # 确保表头索引有效
            header = headers[col_idx] if col_idx < len(headers) else f"未知列{col_idx + 1}"
            print(f"列 {col_idx + 1} ({header}): {cell_text}")


##==process_talbeA===========================
def process_tableA(driver,xpath):
    # 等待表格加载
    wait = WebDriverWait(driver, 10)
    table = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    print(f"find talbe element{table}")
    print(f"find talbe outerHTML: {table.get_attribute('outerHTML')}")

    # 1. 打印 thead 中每一列的标题
    thead = table.find_element(By.TAG_NAME, "thead")
    headers = thead.find_elements(By.TAG_NAME, "tr")
    print("表头列：")
    #print("表头 outerHTML：")
    for i, header in enumerate(headers, 1):
        print(f"第 {i} 列 outerHTML: {header.get_attribute('outerHTML')}")
        print(f"第 {i} 列 文本: {header.text}")
        text = driver.execute_script("return arguments[0].innerText;", header)
        print(f"第 {i} 列 文本: {text}")


    for i, header in enumerate(headers, 0):
        print(f"第 {i} 列: {header.text}")

    # 2. 打印总列数
    total_columns = len(headers)
    print(f"\n表格总列数: {total_columns}")

    # 3. 按行打印内容，并按表头顺序打印每列的 outerHTML

    # 存储按钮的数组
    button_array = []


    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    print(f"\n表格共有 {len(rows)} 行数据：")

    for row_idx, row in enumerate(rows, 1):
        print(f"\n=== 第 {row_idx} 行 ===")
        cells = row.find_elements(By.TAG_NAME, "td")
        for col_idx, cell in enumerate(cells):
            header = headers[col_idx].text  # 获取对应表头
            print(f"{header}:")
            print(f"  outerHTML: {cell.get_attribute('outerHTML')}")
            print(f"  文本内容: {cell.text}")

            #
            if col_idx == len(cells) - 1:  # 最后一列
                print("rr5")
                button = cell.find_element(By.TAG_NAME, "button")
                print("rr7")

                if button and button.tag_name == 'button':
                    print("是 button ")
                    button_array.append(button)

    print(f"一共找到 {len(button_array)} 个 button ")



#####永久保留 主程序
try:

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("成功连接到Chrome调试模式A==>")

    

    try:

        # 代理商查询button;
        # <button type="submit" class="btn btn-blue" data-icon="search"><i class="fa fa-search"></i> 查询</button>
        ##  pagerForm > div > p:nth-child(4) > button
        ##  //*[@id="pagerForm"]/div/p[4]/button

        print("step1 , 按钮 ")
        buttonPath = '//*[@id="pagerForm"]/div/p[4]/button'
        #buttonPath = "//*button[@class='btn btn-blue']"
        buttonClick(driver, By.XPATH, buttonPath)

        print("按钮点完了")

        #buttonPath
        #tablePath = "/html/body/div[10]/div[2]/div[2]/div[2]/table"
        tablePath = "//*[@id='bjui-navtab']/div[2]/div[2]/div[2]/div/div[1]/div/table"

        #process_tableA(driver,tablePath)
        process_table_B(driver,tablePath)
        
        print("list table ok")

    except Exception as dd:
        print(f"Error Error Error select date time error{dd}")

except Exception as e:
    logger.error(f"脚本执行过程中发生未知错误: {e}")
finally:
    # driver.quit()  # 根据需要决定是否关闭浏览器
    logger.info("程序退出")