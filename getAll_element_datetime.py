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

    #wait = WebDriverWait(driver, 10)

    try:

        # 获取当前日期和一年后的日期
        start_date = datetime.now().strftime('%Y-%m-%d')  # 当前日期，格式如 2025-04-10
        end_date = (datetime.now() + relativedelta(years=1)).strftime('%Y-%m-%d')  # 一年后的日期

        start_date = '2024-11-11'
        end_date = '2025-12-12'
        
        # JavaScript 代码
        js_start_date = (
            "document.getElementsByName('begin_valid')[1].removeAttribute('readOnly');"
            f"document.getElementsByName('begin_valid')[1].value = '{start_date}';"
        )

        js_end_date = (
            "document.getElementsByName('end_valid')[1].removeAttribute('readOnly');"
            f"document.getElementsByName('end_valid')[1].value = '{end_date}';"
        )

        # 执行 JavaScript（假设 driver 已经初始化）
        # 第一步：设置开始时间
        print(f" js_start_date:{js_start_date}")
        driver.execute_script(js_start_date)

        print(f" js_end_date:{js_end_date}")
        # 第二步：设置结束时间
        driver.execute_script(js_end_date)

        print("select date time ok")

    except Exception as dd:
        print("Error Error Error select date time error")

except Exception as e:
    logger.error(f"脚本执行过程中发生未知错误: {e}")
finally:
    # driver.quit()  # 根据需要决定是否关闭浏览器
    logger.info("程序退出")