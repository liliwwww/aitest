
from playwright.sync_api import Playwright, sync_playwright, Page,  expect
from datetime import datetime
from getAll_pw_button import click_element_when_ready,click_element_by_role
from getAll_pw_dialog_info import get_alert_message,set_readonly_text
import time

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

    print(">>22")
    page.locator("#organ_code").fill("33333")
    #代理商性质
    #第一个控件
    #<div class="btn-group bootstrap-select show-tick open" style="width: 81px;"><button type="button" class="btn dropdown-toggle selectpicker btn-default" data-toggle="dropdown" data-id="agent_nature" title="请选择"><span class="filter-option pull-left">请选择</span>&nbsp;<span class="caret"></span></button></div>
    #第二个控件
    #<div class="btn-group bootstrap-select show-tick" style="width: 57px;"><button type="button" class="btn dropdown-toggle selectpicker btn-default" data-toggle="dropdown" data-id="agent_nature" title="经销商"><span class="filter-option pull-left">经销商</span>&nbsp;<span class="caret"></span></button><div class="dropdown-menu open" style="min-width: 0px;"><ul class="dropdown-menu inner selectpicker" role="menu"><li data-original-index="0" class="selected"><a tabindex="0" class="" data-normalized-text="<span class=&quot;text&quot;>经销商</span>"><span class="text">经销商</span><span class="glyphicon glyphicon-ok check-mark"></span></a></li><li data-original-index="1"><a tabindex="0" class="" data-normalized-text="<span class=&quot;text&quot;>渠道商</span>"><span class="text">渠道商</span><span class="glyphicon glyphicon-ok check-mark"></span></a></li></ul></div></div>
    #使用这个
    selector = 'button[data-id="agent_nature"][title="经销商"]'
    #选成了第一个元素

    success = click_element_when_ready(
        page=page,
        selector=selector,
        first=True,
        timeout=10000
    )
    #page.get_by_role("listitem").filter(has_text="渠道商").locator("a").click()
    print("代理商性质")

    page.get_by_role("button", name="一级代理商").click()
    page.locator("a").filter(has_text="一级代理商").click()
    print("代理商等级")

    # 展业区域 print(">>99.3")
    page.get_by_role("group", name="基本信息").get_by_role("button").nth(2).click()
    page.locator("a").filter(has_text="北京").click()
    
    print(">>99.4")
    page.get_by_role("group", name="基本信息").get_by_role("button").nth(3).click()
    page.locator("a").filter(has_text="北京市").click()
    
    # 详细地址 print(">>99.5")
    page.locator("#agent_area").click()
    page.locator("#agent_area").fill("天津大学")
    
    
    page.locator("#commissary").click()
    page.locator("#commissary").fill("33221")
    page.locator("#identity_num").click()
    #page.locator("#identity_num").fill("11111")
    #page.locator("#link_man").click()
    page.locator("#identity_num").dblclick()
    page.locator("#identity_num").fill("110108197809251319")
    page.locator("#link_man").click()
    page.locator("#link_man").fill("张五六")
    page.locator("#link_phone").click()
    page.locator("#link_phone").fill("13911111111")
    page.locator("#link_email").click()
    page.locator("#link_email").fill("abc@12.com")
    page.locator("#deposit_money").click()

    print(">>33")
    page.locator("#deposit_money").fill("100")
    page.get_by_role("cell", name="开户账户名称: *").locator("#screen_name").click()
    page.get_by_role("cell", name="开户账户名称: *").locator("#screen_name").fill("天大的事儿")
    page.get_by_role("cell", name="开户银行账户: *").locator("#screen_num").click()
    page.get_by_role("cell", name="开户银行账户: *").locator("#screen_num").fill("11233333334")
    
    ###总行名称
    page.get_by_role("cell", name="总行名称:  查找").get_by_role("button").click()
    page.locator("form").filter(has_text="总行名称： 查询").get_by_role("button").click()
    page.get_by_role("row", name="中国光大银行  选择").get_by_role("button").click()
    
    print(">>44")
    time.sleep(1)

    #支行名称查询
    selector = "#branchSel"
    success = click_element_when_ready(
        page=page,
        selector=selector,
        first=True,
        timeout=10000
    )
    #page.locator("#branchSel").click()
    print(">>44.1")
    #page.locator("input[name=\"branch_bank\"]").click()
    
    print(">>44.2")
    page.get_by_role("row", name="59667 中国光大银行股份有限公司北京怀柔支行").get_by_role("button").click()
    print(">>44.3")
    time.sleep(3)

    #销售经理
    page.get_by_role("group", name="其他信息").locator("#haha1").click()
    print(">>>> open 销售经理 dailog")
    '''
    timeout = 10000
    locator = page.get_by_role("group", name="其他信息").locator("#haha1")
    print(">>>>auto debug>>> 3{}")
    # 等待元素可见
    locator.wait_for(state="visible", timeout=timeout)
    print(f"元素 {selector} 已可见")

    print(">>>>auto debug 4")

    # 检查元素是否启用
    is_enabled = locator.is_enabled()
    if not is_enabled:
        print(f"错误: 元素 {selector} 已禁用")
        page.screenshot(path="error_screenshot_disabled.png")
        return False

    # 执行点击
    print(">>>>auto debug 5")
    locator.click(timeout=timeout)
    print(f">>>>auto debug成功点击元素 {selector}")
    '''

    print(">>44.4")
    time.sleep(2)
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
    time.sleep(3)
    page.get_by_role("group", name="其他信息").locator("#haha").click()
    time.sleep(2)
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
    #page.get_by_role("cell", name="开户银行账户:").locator("#screen_num").click()
    #page.get_by_role("cell", name="开户银行账户:").locator("#screen_num").fill("112342222")
    
    print(">>99.2")
    page.get_by_role("group", name="代理商信息").click()
    page.get_by_role("button", name="下一步").click()
    
    
    print(">>99.6")
    page.locator("#admin_name1").click()
    accountNO = datetime.now().strftime("%Y%m%d%H%M%S")
    page.locator("#admin_name1").fill( accountNO )
    page.get_by_role("button", name="下一步").click()

    message = get_alert_message(page)
    print(f"获取《下一步按钮》ErrorPage 信息{message}")
    
    print(">>99.7")
    # tab2 上传文件
    #  上传文件并更新文本框
    print("GO11>>>")
    #file_path = r"C:\\Users\\wdp\\project\\aitest\\pic\\微信截图_20250407162225.png"
    
    file_path = r"C:\fakepath\微信截图_20250407162225.png"        

    selector = '#one'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )
    print("GO11>>>")
    selector = '#two'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )
    print("GO11>>>")
    selector = '#five'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )
    print("GO11>>>")
    selector = '#Sixteen'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )
    print("GO11>>>")
    selector = '#Seven'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )
    print("GO11>>>")
    selector = '#Six'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )
    print("GO11>>>")
    selector = '#Seventeen'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )
    print("GO11>>>")
    selector = '#Fourteen'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )
    print("GO11>>>")
    selector = '#Fifteen'
    success = set_readonly_text(
        page=page,
        selector=selector,
        value=file_path,
        timeout=10000
    )

    if success:
        print("操作完成：成功更新文本框文件名")
    else:
        print("操作失败：无法更新文本框文件名")

    
    print(">>99.12")
    time.sleep(3)
    click_element_by_role(page,"button", name="提交")

    message = get_alert_message(page)
    #click_element_by_role(page,"button", name="确定")

    # ---------------------
    #context.close()
    #browser.close()


with sync_playwright() as playwright:
    run(playwright)
