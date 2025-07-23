import re
from playwright.sync_api import Playwright, sync_playwright, Page,  expect
import time
import asyncio



# 使用 sync_playwright 启动 Playwright
def goDoubao(page):
    # 启动 Chromium 浏览器，headless=False 表示可见模式便于调试
    
    
    # 1. 信息录入
    input_selector = '#root > div.flow-web-root-outlet > div > div.containerWrapper-NWa4Sz > div.panelWrapper-O67Mdi.left-side-width--variable-aVHci6 > div.center-full-dpDzPj > div > div > div.footer-WyRAth > div > div > div > div:nth-child(3) > div.input-content-container-_k2eqc > div.container-VhbUmi.guidance-input-yS_o_1 > div.editor-container-kXzeJr > div.editor-wrapper-UClPXc > div > textarea'
    page.fill(input_selector, '请解释一下这个图片')  # 替换为实际需要填写的内容

    # 2. 上传附件
    # 通过 SVG path 定位上传按钮
    upload_button = page.locator('svg:has(path[d="M9.035 15.956a1.29 1.29 0 0 0 1.821-.004l6.911-6.911a3.15 3.15 0 0 0 0-4.457l-.034-.034a3.15 3.15 0 0 0-4.456 0l-7.235 7.234a5.031 5.031 0 0 0 7.115 7.115l6.577-6.577a1.035 1.035 0 0 1 1.463 1.464l-6.576 6.577A7.1 7.1 0 0 1 4.579 10.32l7.235-7.234a5.22 5.22 0 0 1 7.382 0l.034.034a5.22 5.22 0 0 1 0 7.383l-6.91 6.91a3.36 3.36 0 0 1-4.741.012l-.006-.005-.012-.011a3.346 3.346 0 0 1 0-4.732L12.76 7.48a1.035 1.035 0 0 1 1.464 1.463l-5.198 5.198a1.277 1.277 0 0 0 0 1.805z"])')
    
    #upload_button.click()  # 点击上传按钮

    # 设置文件上传（替换为实际文件路径）
    page.set_input_files('input[type="file"]', r'C:\Users\wdp\project\auto-test\images\aa.png')  # 替换为实际文件路径

    # 3. 点击发送按钮
    #<button disabled="" id="flow-end-msg-send" aria-disabled="true" aria-label="发送" data-testid="chat_input_send_button" class="semi-button semi-button-disabled semi-button-primary-disabled send-btn-xD8q3r semi-button-with-icon semi-button-with-icon-only" type="button" style="pointer-events: none;"><span class="semi-button-content"><span role="img" class="semi-icon semi-icon-default send-btn-icon-j_fetC"><svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="m3.543 8.883 7.042-7.047a2 2 0 0 1 2.828 0l7.043 7.046a1 1 0 0 1 0 1.415l-.701.701a1 1 0 0 1-1.414 0L13.3 5.956v15.792a1 1 0 0 1-1 1h-.99a1 1 0 0 1-1-1V6.342l-4.654 4.656a1 1 0 0 1-1.414 0l-.7-.7a1 1 0 0 1 0-1.415"></path></svg></span></span></button>

    time.sleep(1)

    # Playwright 定位方式（CSS 组合选择器）
    send_button = page.locator('button[data-testid="chat_input_send_button"][id="flow-end-msg-send"]')
    print(f"button {send_button} ")
    send_button.click()

    #send_button_xpath = '/html/body/div[1]/div[1]/div/div[3]/div[1]/div[1]/div/div/div[3]/div/div/div/div[3]/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[3]/div[2]/span/button'
    #page.locator(f'xpath={send_button_xpath}').click()


# 使用 sync_playwright 启动 Playwright
def goDoubaoWithThink(page):
    # 启动 Chromium 浏览器，headless=False 表示可见模式便于调试
    
    
    # 1. 信息录入
    input_selector = '#root > div.flow-web-root-outlet > div > div.containerWrapper-NWa4Sz > div.panelWrapper-O67Mdi.left-side-width--variable-aVHci6 > div.center-full-dpDzPj > div > div > div.footer-WyRAth > div > div > div > div:nth-child(3) > div.input-content-container-_k2eqc > div.container-VhbUmi.guidance-input-yS_o_1 > div.editor-container-kXzeJr > div.editor-wrapper-UClPXc > div > textarea'
    page.fill(input_selector, '请解释一下这个图片')  # 替换为实际需要填写的内容

    # 2. 上传附件
    # 通过 SVG path 定位上传按钮
    upload_button = page.locator('svg:has(path[d="M9.035 15.956a1.29 1.29 0 0 0 1.821-.004l6.911-6.911a3.15 3.15 0 0 0 0-4.457l-.034-.034a3.15 3.15 0 0 0-4.456 0l-7.235 7.234a5.031 5.031 0 0 0 7.115 7.115l6.577-6.577a1.035 1.035 0 0 1 1.463 1.464l-6.576 6.577A7.1 7.1 0 0 1 4.579 10.32l7.235-7.234a5.22 5.22 0 0 1 7.382 0l.034.034a5.22 5.22 0 0 1 0 7.383l-6.91 6.91a3.36 3.36 0 0 1-4.741.012l-.006-.005-.012-.011a3.346 3.346 0 0 1 0-4.732L12.76 7.48a1.035 1.035 0 0 1 1.464 1.463l-5.198 5.198a1.277 1.277 0 0 0 0 1.805z"])')
    
    
    #upload_button.click()  # 点击上传按钮

    # 设置文件上传（替换为实际文件路径）
    page.set_input_files('input[type="file"]', r'C:\Users\wdp\project\auto-test\images\aa.png')  # 替换为实际文件路径

    # 3. 点击发送按钮
    #<button disabled="" id="flow-end-msg-send" aria-disabled="true" aria-label="发送" data-testid="chat_input_send_button" class="semi-button semi-button-disabled semi-button-primary-disabled send-btn-xD8q3r semi-button-with-icon semi-button-with-icon-only" type="button" style="pointer-events: none;"><span class="semi-button-content"><span role="img" class="semi-icon semi-icon-default send-btn-icon-j_fetC"><svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="m3.543 8.883 7.042-7.047a2 2 0 0 1 2.828 0l7.043 7.046a1 1 0 0 1 0 1.415l-.701.701a1 1 0 0 1-1.414 0L13.3 5.956v15.792a1 1 0 0 1-1 1h-.99a1 1 0 0 1-1-1V6.342l-4.654 4.656a1 1 0 0 1-1.414 0l-.7-.7a1 1 0 0 1 0-1.415"></path></svg></span></span></button>

    time.sleep(1)

    # Playwright 定位方式（CSS 组合选择器）
    send_button = page.locator('button[data-testid="chat_input_send_button"][id="flow-end-msg-send"]')
    print(f"button {send_button} ")
    send_button.click()

    #send_button_xpath = '/html/body/div[1]/div[1]/div/div[3]/div[1]/div[1]/div/div/div[3]/div/div/div/div[3]/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[3]/div[2]/span/button'
    #page.locator(f'xpath={send_button_xpath}').click()





def goDoubaoThinkResponse(page):   
    # 4. 监听后台返回结果
    response_container_selector = '.think-collapse-block-iC7Hni'
    previous_content = ''
    current_content = ''
    max_wait_time = 60  # 最大等待时间（秒）
    check_interval = 1  # 检查间隔（秒）
    elapsed_time = 0

    sel = page.locator(response_container_selector).last
    print(f"current_content len is ({sel})")

    while True:
        # 获取返回信息容器的内容
        current_content = sel.inner_text()

        

        # 如果内容不再变化且不为空，说明回复完成
        if current_content == previous_content and current_content != '':
            print('回复已完成！')
            break

        # 更新上一次的内容
        previous_content = current_content

        # 等待一段时间再检查
        time.sleep(check_interval)
        elapsed_time += check_interval

        # 如果超过最大等待时间，退出循环
        if elapsed_time >= max_wait_time:
            print('超时，停止监听！')
            break

    # 输出最终返回结果
    print('返回Think结果：', current_content)


def goDoubaoResponse(page):   
    # 4. 监听后台返回结果
    response_container_selector = '.container-QE4ayg'
    previous_content = ''
    current_content = ''
    max_wait_time = 60  # 最大等待时间（秒）
    check_interval = 1  # 检查间隔（秒）
    elapsed_time = 0

    sel = page.locator(response_container_selector).last
    print(f"current_content len is ({sel})")

    while True:
        # 获取返回信息容器的内容
        current_content = sel.inner_text()

        

        # 如果内容不再变化且不为空，说明回复完成
        if current_content == previous_content and current_content != '':
            print('回复已完成！')
            break

        # 更新上一次的内容
        previous_content = current_content

        # 等待一段时间再检查
        time.sleep(check_interval)
        elapsed_time += check_interval

        # 如果超过最大等待时间，退出循环
        if elapsed_time >= max_wait_time:
            print('超时，停止监听！')
            break

    # 输出最终返回结果
    print('返回结果：', current_content)


def run(playwright: Playwright) -> None:

    # 连接到 Chrome 调试端口
    browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
    print("成功连接到 Chrome 调试端口")

    # 枚举所有上下文
    for context in browser.contexts:
        print(f"Context ID: {context}")
        # 枚举当前上下文下的所有页面
        for page1 in context.pages:
            print(f"  Page URL: {page1.url}")
            if page1.url.startswith( 'https://www.doubao.com/chat'):
                print("找到 doubao ")
                page = page1
    print("自检完成")
    print(f"\n\nPage title: {page.title()}\n\n")
    print(">>Go")


    goDoubao(page)
    time.sleep(4)
    goDoubaoThinkResponse(page)
    goDoubaoResponse(page)

    
    
if __name__ == "__main__":    
    with sync_playwright() as playwright:
        run(playwright)
