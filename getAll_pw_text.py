import re
from playwright.sync_api import Playwright, sync_playwright, Page,  expect
import time
import asyncio


### 验证一下窗口



#######对外暴露方法
def text_when_ready(page: Page, selector: str, first: bool = True, timeout: int = 10000) -> bool:
   
    try:

        print(">>>>click_element_when_ready 1")
        # 创建定位器
        locator = page.locator(selector)

        print(">>>>click_element_when_ready 2")
        if first:
            locator = locator.first
        else:
            # 1 就是第二个
            locator = page.locator(selector).nth(1)
            print("点击第二个按钮.1>>>")
            

        print(">>>>click_element_when_ready 3{}")
        # 等待元素可见
        locator.wait_for(state="visible", timeout=timeout)
        print(f"元素 {selector} 已可见")


        return True

    except TimeoutError:
        print(f"错误: 元素 {selector} 在 {timeout}ms 内未变得可见或可点击")
        page.screenshot(path="error_screenshot_timeout.png")
        print("截图已保存: error_screenshot_timeout.png")
        return False
    except Exception as e:
        print(f"点击元素 {selector} 时发生错误: {e}")
        page.screenshot(path="error_screenshot_general.png")
        print("截图已保存: error_screenshot_general.png")
        return False


     
from playwright.sync_api import Page
from datetime import datetime


def screenshot_and_mark_element(page: Page, selector: str):
    element = page.query_selector(selector)
    if element and element.is_visible():
        bounding_box = element.bounding_box()
        x = bounding_box['x'] if bounding_box else 0
        y = bounding_box['y'] if bounding_box else 0
        width = bounding_box['width'] if bounding_box else 0
        height = bounding_box['height'] if bounding_box else 0

        current_time = datetime.now().strftime("%m%d%H%M%S")
        image_name = f"screenshots/{selector.replace(' ', '_')}_{current_time}.png"
        image_name = sanitize_windows_filename(image_name)
        print(f"output file name {image_name}")
        page.screenshot(path=image_name)

        # 以下是在截图上绘制红色线框的逻辑（这里只是简单示例，实际实现可能更复杂）
        from PIL import Image, ImageDraw
        img = Image.open(image_name)
        draw = ImageDraw.Draw(img)
        draw.rectangle([x, y, x + width, y + height], outline="red", width=2)
        img.save(image_name)

        return x, y, width, height
    return 0, 0, 0, 0

#############验证用#######################

def sanitize_windows_filename(s):
    """
    将字符串中不符合 Windows 文件名命名规范的字符替换为"_"
    :param s: 输入字符串
    :return: 处理后的字符串
    """
    # Windows 文件名不允许的字符列表
    invalid_chars = r'\/:*?"<>|'
    for char in invalid_chars:
        s = s.replace(char, '_')
    return s

def run(playwright: Playwright) -> None:

    # 连接到 Chrome 调试端口
    browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
    print("成功连接到 Chrome 调试端口")

    # 获取现有上下文和页面
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.pages[0] if context.pages else context.new_page()

    print(">>11Go")
    selector = 'input[name="agent_num"][class="form-control"][type="text"]'
    text_when_ready(page, selector)
    screenshot_and_mark_element(page, selector)

    time.sleep(1)

    selector = 'input[name="agent_name"][class="form-control"][type="text"]'
    text_when_ready(page, selector)
    screenshot_and_mark_element(page, selector)
    
if __name__ == "__main__":    
    with sync_playwright() as playwright:
        run(playwright)
