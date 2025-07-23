
# 通过传递对话框id，获得对话框的所有信息；
from playwright.sync_api import sync_playwright, Playwright, Page
from playwright.async_api import  Page, TimeoutError
import json
import time
import asyncio
import os

####upload 方法1：#####

def set_file_and_update_text(page: Page, text_selector: str, file_selector: str, file_path: str, timeout: int = 10000) -> bool:
    """
    异步上传文件并验证文本框更新。

    Args:
        page (Page): Playwright 的页面对象。
        text_selector (str): 只读文本框的 CSS 选择器（如 '#five'）。
        file_selector (str): 文件上传 input 的 CSS 选择器。
        file_path (str): 文件的绝对路径。
        timeout (int): 等待超时时间（毫秒）。默认 10000ms。

    Returns:
        bool: 成功返回 True，失败返回 False.
    """
    try:

        print(">>>upload file 1")
        # 验证文件存在
        if not os.path.isfile(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return False

        '''
        print(">>>upload file 2")
        # 定位文件上传 input
        file_input = page.locator(file_selector)
        count = file_input.count()

        print(f">>>upload file 3 {count}")
        if count == 0:
            print(f"错误: 未找到文件上传控件 '{file_selector}'")
            page.screenshot(path="no_file_input_screenshot.png")
            return False

        # 等待文件 input 可用
        print(">>>upload file 4")
        file_input.wait_for(state="attached", timeout=timeout)  # 可能隐藏
        print(f"文件上传控件 '{file_selector}' 已找到")
        '''

        # 定位文本框
        print(">>>upload file 5")
        text_input = page.locator(text_selector)
        text_input.wait_for(state="visible", timeout=timeout)
        print(f"文本框 '{text_selector}' 已可见")

        # 上传文件
        print(">>>upload file 6")
        #file_input.set_input_files(file_path)
        print(f"成功上传文件 '{file_path}'")

        # 验证文本框更新
        print(">>>upload file 7")
        filename = os.path.basename(file_path)
        page.wait_for_function(
            f'document.querySelector("{text_selector}").value === "{filename}"',
            timeout=5000
        )
        print(f"文本框 '{text_selector}' 已更新为 '{filename}'")
        page.screenshot(path="after_upload_screenshot.png")
        print("截图已保存: after_upload_screenshot.png")
        return True

    except TimeoutError:
        print(f"错误: 在 {timeout}ms 内未完成上传或文本框未更新")
        page.screenshot(path="timeout_screenshot.png")
        return False
    except Exception as e:
        print(f"上传文件或更新文本框错误: {e}")
        page.screenshot(path="error_screenshot_general.png")
        return False



##### 方法2 ， 使用script，修改属性######
def set_readonly_text(page: Page, selector: str, value: str, timeout: int = 10000) -> bool:
    """
    异步为只读文本框设置值，通过 JavaScript 移除 readonly。

    Args:
        page (Page): Playwright 的页面对象。
        selector (str): 文本框的 CSS 选择器。
        value (str): 要设置的文件名。
        timeout (int): 等待超时时间（毫秒）。默认 10000ms。

    Returns:
        bool: 成功返回 True，失败返回 False.
    """
    try:
        # 定位文本框
        text_input = page.locator(selector)
        text_input.wait_for(state="visible", timeout=timeout)
        print(f"文本框 '{selector}' 已可见")

        # 检查元素是否存在
        count = text_input.count()
        if count == 0:
            print(f"错误: 未找到文本框 '{selector}'")
            page.screenshot(path="no_input_screenshot.png")
            return False

        # 检查是否为文本框
        input_type = text_input.evaluate("el => el.type")
        if input_type != "text":
            print(f"错误: 元素 '{selector}' 不是文本框 (type={input_type})")
            page.screenshot(path="invalid_input_screenshot.png")
            return False

        # 使用 JavaScript 设置值
        text_input.evaluate(
            """
            (element, value) => {
                element.removeAttribute('readonly');
                element.value = value;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
            """,
            value
        )
        print(f"成功设置文本框 '{selector}' 的值为 '{value}'")

        # 验证值
        actual_value = text_input.input_value()
        if actual_value != value:
            print(f"错误: 文本框值未更新为 '{value}', 实际为 '{actual_value}'")
            page.screenshot(path="value_mismatch_screenshot.png")
            return False

        page.screenshot(path="after_set_screenshot.png")
        print("截图已保存: after_set_screenshot.png")
        return True

    except TimeoutError:
        print(f"错误: 文本框 '{selector}' 在 {timeout}ms 内未变得可见")
        page.screenshot(path="timeout_screenshot.png")
        return False
    except Exception as e:
        print(f"设置文本框值错误: {e}")
        page.screenshot(path="error_screenshot_general.png")
        return False

####upload when ready########
def upload_file_when_ready(page: Page, selector: str, file_path: str, timeout: int = 10000) -> bool:
    """
    异步上传文件到指定 input 元素，等待元素可用后再执行。

    Args:
        page (Page): Playwright 的页面对象。
        selector (str): input 元素的 CSS 选择器。
        file_path (str): 文件的绝对路径。
        timeout (int): 等待超时时间（毫秒）。默认 10000ms。

    Returns:
        bool: 上传成功返回 True，失败返回 False.
    """
    try:
        # 验证文件存在
        if not os.path.isfile(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return False

        # 定位 input 元素
        input_locator = page.locator(selector)

        # 等待元素可见
        input_locator.wait_for(state="visible", timeout=timeout)
        print(f"元素 '{selector}' 已可见")

        # 检查元素是否存在
        count = input_locator.count()
        if count == 0:
            print(f"错误: 未找到元素 '{selector}'")
            page.screenshot(path="no_input_screenshot.png")
            return False

        # 检查元素是否启用
        is_enabled =  input_locator.is_enabled()
        if not is_enabled:
            print(f"错误: 元素 '{selector}' 已禁用")
            page.screenshot(path="input_disabled_screenshot.png")
            return False

        # 检查是否为文件上传控件
        input_type = input_locator.evaluate("el => el.type")
        if input_type != "file":
            print(f"错误: 元素 '{selector}' 不是文件上传控件 (type={input_type})")
            page.screenshot(path="invalid_input_screenshot.png")
            return False

        # 上传文件
        input_locator.set_input_files(file_path)
        print(f"成功上传文件 '{file_path}' 到 '{selector}'")
        page.screenshot(path="after_upload_screenshot.png")
        print("截图已保存: after_upload_screenshot.png")
        return True

    except TimeoutError:
        print(f"错误: 元素 '{selector}' 在 {timeout}ms 内未变得可见或可上传")
        page.screenshot(path="timeout_screenshot.png")
        return False
    except Exception as e:
        print(f"上传文件 '{file_path}' 时发生错误: {e}")
        page.screenshot(path="error_screenshot_general.png")
        return False


####获取页面dialog 错误信息####
def get_alert_message(page: Page, timeout: int = 5000) -> str:
    """
    检查错误提示对话框是否可见，并提取错误信息。

    Args:
        page (Page): Playwright 的页面对象。
        timeout (int): 等待对话框出现的超时时间（毫秒）。默认 5000ms。

    Returns:
        str: 如果对话框可见，返回错误信息；否则返回空字符串。
    """
    try:
        # 定位错误提示对话框
        alert_dialog = page.locator("#bjui-alertMsgBox")
        
        # 检查对话框是否可见
        is_visible = alert_dialog.is_visible(timeout=timeout)
        if not is_visible:
            print("错误提示对话框 '#bjui-alertMsgBox' 不可见")
            return ""

        print("错误提示对话框 '#bjui-alertMsgBox' 已可见")

        # 定位错误信息
        msg_locator = alert_dialog.locator("div.msg")
        msg_count = msg_locator.count()
        if msg_count == 0:
            print("错误: 未找到错误信息 '<div class=\"msg\">'")
            page.screenshot(path="no_msg_screenshot.png")
            return ""

        # 提取错误信息文本
        message = msg_locator.text_content()
        if message:
            print(f"提取错误信息: '{message}'")
            return message.strip()
        else:
            print("错误: 错误信息为空")
            page.screenshot(path="empty_msg_screenshot.png")
            return ""

    except TimeoutError:
        print(f"错误: 在 {timeout}ms 内未找到可见的 '#bjui-alertMsgBox'")
        page.screenshot(path="timeout_screenshot.png")
        return ""
    except Exception as e:
        print(f"提取错误信息时发生错误: {e}")
        page.screenshot(path="error_screenshot_general.png")
        return ""
    


####

def get_dialog_info(page: Page, dialog_selector: str = "div#dialog") -> dict:
    """
    获取弹出层的所有信息并返回。
    
    Args:
        page: Playwright 的 Page 对象
        dialog_selector: 弹出层的 CSS 选择器，默认为 div#dialog
    Returns:
        包含弹出层信息的字典
    """

    dialog_selector = "div.bjui-dialog:has-text('查看代理商')"
    
    try:
        # 等待弹出层出现
        dialog = page.locator(dialog_selector)
        dialog.wait_for(state="visible", timeout=10000)
        print("弹出层已找到")

        # 获取详细信息
        dialog_info = {
            "html": dialog.evaluate("el => el.outerHTML") or "无 HTML",
            "text": dialog.inner_text().strip() or "无文本",
            "attributes": dialog.evaluate("el => Object.fromEntries(Object.entries(el.attributes).map(([k, v]) => [k, v.value]))") or {},
            "children": []
        }

        # 获取子元素
        children = dialog.locator(">*").all()
        for child in children:
            child_info = {
                "tag": child.evaluate("el => el.tagName.toLowerCase()"),
                "text": child.inner_text().strip() or "无文本",
                "classes": child.get_attribute("class") or "无类"
            }
            dialog_info["children"].append(child_info)

        # 打印详细信息
        print("\n=== 弹出层信息 ===")
        print(f"HTML:\n{dialog_info['html']}\n")
        print(f"文本内容:\n{dialog_info['text']}\n")
        print(f"属性:\n{json.dumps(dialog_info['attributes'], indent=2, ensure_ascii=False)}\n")
        print("子元素:")
        for i, child in enumerate(dialog_info["children"], 1):
            print(f"  子元素 {i}:")
            print(f"    标签: {child['tag']}")
            print(f"    文本: {child['text']}")
            print(f"    类: {child['classes']}")
        print("==================")

        return dialog_info

    except Exception as e:
        print(f"获取弹出层信息失败: {e}")
        page.screenshot(path="dialog_error_screenshot.png")
        print("已保存错误截图: dialog_error_screenshot.png")
        return {}

def main():
    """独立运行，测试弹出层信息获取"""
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("成功连接到 Chrome 调试端口")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()

            print("page 对象初始化完成:")

            # 假设页面已有弹出层（手动触发或修改逻辑）
            #dialog_info = get_dialog_info(page)
            #print("\n最终结果:")
            #print(json.dumps(dialog_info, indent=2, ensure_ascii=False))
            #message = get_alert_message(page=page)
            #print(f" Error Msg:{message}")

            # 上传文件
            # 文件绝对路径（请替换为实际路径）
            file_path = r"C:\fakepath\微信截图_20250407162225.png"
            # Linux/macOS 示例：
            # file_path = "/home/yourname/Pictures/微信截图_20250407162225.png"

            # 文件绝对路径（请替换为实际路径）
            #file_path = r"C:\Users\YourName\Pictures\微信截图_20250407162225.png"
            # Linux/macOS 示例：
            # file_path = "/home/yourname/Pictures/微信截图_20250407162225.png"

            # 假设文件上传 input（需确认实际选择器）
            #file_selector = 'input[type="file"]'  # 请替换为实际选择器
            xpath = '"//*[@id=\"uploadImgForm\"]/fieldset/p[4]/a/input")）'
            selector = '#Sixteen'
            css = '#uploadImgForm fieldset p:nth-child(4) a input'



            ##排查1
            selector = '#Sixteen'
            #text_input = page.locator(selector)
            #count = text_input.count()
            #print(f"step1：找到 {count} 个 '#Sixteen' 元素")

            ##排查2
            
            #one，#two，#five,#Sixteen,#Seven,#Six,#Seventeen,#Fourteen,#Fifteen

            # 上传文件并更新文本框
            print("GO11>>>")
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

            if success:
                print("操作完成：成功上传图片")
            else:
                print("操作失败：无法上传图片")

            page.get_by_role("button", name="提交").click()

        except Exception as e:
            print(f"运行失败: {e}")
        finally:
            print("任务完成，浏览器保持打开状态")

if __name__ == "__main__":
    main()