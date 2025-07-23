import re
from playwright.sync_api import Playwright, sync_playwright, Page,  expect
import time
import asyncio
from getAll_pw_button import click_element_when_ready


### 验证一下窗口

def close_dialog_if_open(page: Page, dialog_locator):
    """关闭打开的对话框"""
    try:
        dialog = page.locator( dialog_locator )
        if dialog.is_visible():
            print(f"检测到《《《打开》》》 的对话框{dialog_locator}，尝试关闭")
            
            close_button = dialog.locator("a.close")
            if  close_button.count() > 0:
                close_button.click()
                print("对话框关闭按钮已点击")
            else:
                # 尝试点击背景关闭
                dialog.locator("div.bjui-dialogBackground").click()
                print("对话框背景已点击")
            # 等待对话框消失
            dialog.wait_for(state="hidden", timeout=5000)
            print("对话框已关闭")
        else:
            print(f"检测到《《《关闭》》》 的对话框{dialog_locator}，尝试关闭")
    except Exception as e:
        print(f"关闭对话框时发生错误: {e}")



#############验证用#######################

def click_query_button( page ):

    ##在点击第二个按钮前，现验证一下页面的层是否打开了；

    dialog_locator = "div.bjui-dialog-wrap"
    close_dialog_if_open(page, dialog_locator)

    try:

        # 验证选择器
        selector = '#pagerForm button[type="submit"][data-icon="search"]'
        count =  page.locator(selector).count()
        print(f"找到 {count} 个匹配按钮")

        if count == 0:
            print("错误: 未找到查询按钮")
            page.screenshot(path="no_button_screenshot.png")
            return
        
        if count > 1:
            print("点击第二个按钮>>>")
            locatorA = page.locator(selector).nth(2)
            print("点击第二个按钮.1>>>")
            locatorA.wait_for(state="visible", timeout=2000)
            print(f"点击第二个按钮.2>>>元素 {selector} 已可见")

            is_enabled = locatorA.is_enabled()
            if not is_enabled:
                print(f"点击第二个按钮>>>错误: 元素 {selector}  已禁用")
            
            print("点击第二个按钮>>> >>>before click =======")
            success = locatorA.click(timeout=3)
        else:
            # 点击查询按钮
            success =  click_element_when_ready(
                page=page,
                selector=selector,
                first=True,  # 假设只有一个匹配按钮
                timeout=10000
            )

        if success:
            print("操作完成：成功点击查询按钮")
        else:
            print("操作失败：无法点击查询按钮")

    except Exception as e:
        print(f"主程序错误: {e}")
        page.screenshot(path="main_error_screenshot.png")
        print("截图已保存: main_error_screenshot.png")
    finally:
        print("任务完成，浏览器保持打开状态")




###
def element_Info( element ):
    is_visible = element.is_visible()
    is_enabled = element.is_enabled()
    print(f"元素{ element }可见: {is_visible}, 元素启用: {is_enabled}")

def run(playwright: Playwright) -> None:

    # 连接到 Chrome 调试端口
    browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
    print("成功连接到 Chrome 调试端口")

    # 获取现有上下文和页面
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.pages[0] if context.pages else context.new_page()

    print(">>11")
    
    #page.get_by_role("link", name=" 代理商管理").click()
    #page.get_by_role("link", name=" 代理商申请").click()
    #page.get_by_role("link", name=" 添加代理商").click()
    page.locator("#agent_name").click()
    page.locator("#agent_name").fill("1111")
    page.locator("#organ_code").click()

    
    ###总行名称
    #page.get_by_role("cell", name="总行名称:  查找").get_by_role("button").click()
    #page.locator("form").filter(has_text="总行名称： 查询").get_by_role("button").click()
    #page.get_by_role("row", name="中国光大银行  选择").get_by_role("button").click()
    
    print(">>44")
    time.sleep(1)

    

    selector = "#branchSel"
    success = click_element_when_ready(
        page=page,
        selector=selector,
        first=True,
        timeout=10000
    )
    print(f">>> 支行名称查询 {selector} 结果 {success}")

    
    print(">>44.2")
    page.get_by_role("row", name="59667 中国光大银行股份有限公司北京怀柔支行").get_by_role("button").click()
    print(">>44.3")
    
    page.get_by_role("group", name="其他信息").locator("#haha1").click()
    
    print(">>44.4")
    page.locator("input[name=\"sm_name\"]").click()
    print(">>44.5")
    page.locator("input[name=\"sm_name\"]").fill("张三")

    print(">>55")
    #page.get_by_role("button", name=" 查询").nth(1).click()
    selectorB = '#pagerForm button[type="submit"][data-icon="search"]'
    click_element_when_ready( page=page,
                selector=selectorB, first=False )   
    
    print(">>5633")
    page.get_by_role("cell", name="18245636954").click()
    page.get_by_role("button", name=" 选择").click()


    ### 运营经理
    time.sleep(2)
    page.get_by_role("group", name="其他信息").locator("#haha").click()
    page.locator("input[name=\"sm_name\"]").click()
    page.locator("input[name=\"sm_name\"]").fill("张三")
    page.locator("input[name=\"sm_name\"]").press("Enter")

    time.sleep(1)
    selectorB = '#pagerForm button[type="submit"][data-icon="search"]'
    click_element_when_ready( page=page,
                selector=selectorB, first=False )   
    
    page.get_by_role("button", name=" 选择").click()
    

    ###有效期
    page.get_by_role("group", name="其他信息").get_by_role("link").first.click()
    page.locator("select[name=\"year\"]").select_option("2024")
    page.get_by_text("1", exact=True).first.click()
    
    print(">>99")
    page.get_by_role("group", name="其他信息").get_by_role("link").nth(1).click()
    page.get_by_role("definition").filter(has_text="14").click()

    print(">>99.1")
    page.get_by_role("cell", name="开户银行账户:").locator("#screen_num").click()
    page.get_by_role("cell", name="开户银行账户:").locator("#screen_num").fill("112342222")
    
    print(">>99.2")
    page.get_by_role("group", name="代理商信息").click()
    page.get_by_role("button", name="下一步").click()
    
    print(">>99.3")
    page.get_by_role("group", name="基本信息").get_by_role("button").nth(2).click()
    page.locator("a").filter(has_text="北京").click()
    
    print(">>99.4")
    page.get_by_role("group", name="基本信息").get_by_role("button").nth(3).click()
    page.locator("a").filter(has_text="北京市").click()
    
    print(">>99.5")
    page.locator("#agent_area").click()
    page.locator("#agent_area").fill("天津大学")
    
    print(">>99.6")
    page.locator("#admin_name1").click()
    page.locator("#admin_name1").fill("32323232323")
    page.get_by_role("button", name="下一步").click()
    
    print(">>99.7")
    page.locator("input[name=\"\\31 \"]").click()
    page.locator("input[name=\"\\31 \"]").set_input_files("微信截图_20250407162225.png")
    print(">>99.8")
    page.locator("input[name=\"\\32 \"]").click()
    page.locator("input[name=\"\\32 \"]").set_input_files("微信截图_20250407162225.png")
    
    print(">>99.9")
    page.locator("input[name=\"\\35 \"]").click()
    page.locator("input[name=\"\\35 \"]").set_input_files("微信截图_20250407162225.png")
    page.locator("input[name=\"\\31 6\"]").click()
    
    print(">>99.10")
    page.locator("input[name=\"\\31 6\"]").set_input_files("微信截图_20250407162225.png")
    page.locator("input[name=\"\\37 \"]").click()
    page.locator("input[name=\"\\37 \"]").set_input_files("微信截图_20250407162225.png")
    page.locator("input[name=\"\\36 \"]").click()
    
    print(">>99.11")
    page.locator("input[name=\"\\36 \"]").set_input_files("微信截图_20250407162225.png")
    page.locator("input[name=\"\\31 7\"]").click()
    page.locator("input[name=\"\\31 7\"]").set_input_files("微信截图_20250407162225.png")
    
    print(">>99.12")
    page.get_by_role("button", name="提交").click()
    page.get_by_role("button", name=" 确定").click()

    # ---------------------
    #context.close()
    #browser.close()


with sync_playwright() as playwright:
    run(playwright)
