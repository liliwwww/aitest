from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import logging
import time
from selenium.webdriver.chrome.options import Options
import json
import sys


# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



##执行操作
def execute_operations(driver, wait, operations):
    """执行 JSON 中的操作序列"""
    results = []
    for op in operations:
        
        

        
        control = op.get("control", {})
        action = op.get("action")
        xpath = control.get("xpath")
        script = control.get("script")
        control_name = control.get("name")
        control_type = control.get("type")
        value = op.get("value", "")
        description = op.get("description", "")

        result = {
            "control_name": control_name,
            "xpath": xpath,
            "action": action,
            "description": description,
            "status": "unknown",
            "message": ""
        }

        print(f"get Json, \n\t control_name{control_name}, \n\txpath{xpath}, \n\taction{description}")

        try:

            if script and len(script) > 0:
                ##"直接执行脚本"
                print(f"直接执行脚本{script}")
                driver.execute_script(script)
                result["status"] = "success"
                result["message"] = f"{control_name} 执行成功"
                print(f"直接执行脚本 成功")

            else:
                ## 定位元素,在执行
                ## 斗胆加了一个获得element的方法；
                if action == "click":
                    element = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, xpath)
                    ))
                else:
                    element = wait.until(EC.presence_of_element_located(
                        (By.XPATH, xpath)
                    ))

                print(f"定位5元素：{element.tag_name}")
                print(f"定位5操作：{action}")
                print(f"元素5HTML：{element.get_attribute("outerHTML")}")
                time.sleep(5)

                # 根据 action 执行操作
                if action == "click":
                    print("----click----")
                    try:
                        # 先尝试原生点击
                        element.click()
                        print("原生 click() 成功")
                    except WebDriverException as e:
                        print(f"原生 click() 失败: {str(e)}，尝试 JavaScript 点击")
                        # 如果失败，用 JavaScript 点击
                        driver.execute_script("arguments[0].click();", element)
                        print("JavaScript 点击成功")
                    
                    driver.execute_script("arguments[0].click();", element)
                    
                    #不稳定
                    #element.click()
                    result["status"] = "success"
                    result["message"] = f"{control_name} 点击成功"

                    ### 看看sm_name的回填值；
                    try:
                        print("找 sm_name的返回值")
                        input_field = wait.until(EC.presence_of_element_located((By.ID, "sm_name")))
                        value = input_field.get_attribute("value")
                        print(f"点击后输入框值: {value}")
                    except:
                        print("找 sm_name的返回值失败")
                elif action == "set_value" and control_type == "input":
                    print("----set_value----")
                    element.clear()
                    #driver.execute_script("arguments[0].value = arguments[1];", element, value)

                    #先获得焦点
                    #driver.execute_script("arguments[0].click();", element)
                    element.send_keys(value)
                    print("----set_value over")
                    actual_value = element.get_attribute("value")
                    print(f"----get_value {actual_value}")
                    if actual_value == value:
                        result["status"] = "success"
                        result["message"] = f"{control_name} 已成功设置为 '{value}'"
                    else:
                        result["status"] = "failure"
                        result["message"] = f"{control_name} 设置失败，当前值为 '{actual_value}'"

                else:
                    print("----error----")
                    result["status"] = "error"
                    result["message"] = f"不支持的操作类型: {action} 或控件类型: {control_type}"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"执行 {control_name} 时出错: {str(e)}"

        results.append(result)
        #print(json.dumps(result, ensure_ascii=False, indent=2))
        
        
        time.sleep(4)
        print('上一步执行结束，稍等3秒钟\n\n\n')
    return results



def main():
    
    # 初始化 Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("成功连接到Chrome调试模式A")
    wait = WebDriverWait(driver, 10)


    try:
        # 提示用户输入 Web 界面 URL
        #url = input("请输入要打开的 Web 界面 URL: ")
        #driver.get(url)
        #print(f"已打开 URL: {url}")

        while True:
            # 提示用户输入 JSON 控制脚本
            print("\n请输入 JSON 控制脚本（输入 'exit' 退出）：")
            json_input = ""
            while True:
                line = input()
                if line.strip() == "exit":
                    print("程序退出")
                    return
                json_input += line
                # 检查是否输入完整（简单判断是否包含结束符 ']'）
                if ']' in line:
                    break

            # 解析 JSON
            try:
                script = json.loads(json_input)
                operations = script.get("operations", [])
                if not operations:
                    print("错误：JSON 中没有 'operations' 字段或为空")
                    continue

                # 执行操作
                print("\n开始执行操作...")
                results = execute_operations(driver, wait, operations)
                print("\n所有操作执行完成，结果如下：")
                print(json.dumps(results, ensure_ascii=False, indent=2))

            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {str(e)}")
            except Exception as e:
                print(f"执行过程中发生错误: {str(e)}")

    finally:
        # 关闭浏览器
        print("Exit Exit Exit")

if __name__ == "__main__":
    main()    