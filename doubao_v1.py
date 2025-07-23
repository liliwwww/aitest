import re
from playwright.sync_api import Playwright, sync_playwright, Page,  expect
import time
import asyncio
import os
from bs4 import BeautifulSoup
import shutil
import os
from pathlib import Path

def write_string_to_file(content: str, mode: str = 'a', encoding: str = 'utf-8') -> bool:

    print(f"write to file {content}")
    """
    将字符串内容写入指定文件
    
    参数:
        content (str): 要写入的字符串内容
        file_path (str): 文件路径
        mode (str, 可选): 打开文件的模式 (默认为 'w'，即写入模式)
        encoding (str, 可选): 文件编码 (默认为 'utf-8')
    
    返回:
        bool: 如果写入成功返回True，否则返回False
    """
    try:
        # 确保目录存在
        file_path = "output.txt"
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # 写入文件
        with open(file_path, mode, encoding=encoding) as file:
            file.write(f"{content}\n")
        return True
    except Exception as e:
        print(f"写入文件时出错: {e}")
        return False


def resetDialog( page ):

    button = page.locator('#root > div.flow-web-root-outlet > div > div.containerWrapper-NWa4Sz > div.container-J58dAw > div > aside > aside > div > div.\!px-12 > div > div > div')
    button.click()

    time.sleep(2)


    input_selector = '#root > div.flow-web-root-outlet > div > div.containerWrapper-NWa4Sz > div.panelWrapper-O67Mdi.left-side-width--variable-aVHci6 > div.center-full-dpDzPj > div > div > div.inter-MUNFr1.\!overflow-visible > div > div > div.w-full > div:nth-child(2) > div.input-content-container-_k2eqc > div.container-VhbUmi > div.editor-container-kXzeJr > div.editor-wrapper-UClPXc > div > textarea'
    page.fill(input_selector, '1+1=?')  # 替换为实际需要填写的内容

    time.sleep(1)

    send_button = page.locator('#flow-end-msg-send')
    send_button.click()

    



def move_file_to_directory(source_file: str) -> bool:
    """
    将单个文件移动到目标目录
    
    参数:
        source_file (str): 源文件路径（包含文件名）
        target_directory (str): 目标目录路径（不包含文件名，目录需存在或自动创建）
    
    返回:
        bool: 移动成功返回True，失败返回False
    """
    try:
        # 检查源文件是否存在且是文件
        if not os.path.isfile(source_file):
            print(f"错误：源文件 '{source_file}' 不存在或不是文件")
            return False
        
        # 确保目标目录存在（自动创建多级目录）
        target_directory = r"E:\2025-032\bak"
        Path(target_directory).mkdir(parents=True, exist_ok=True)
        
        # 获取目标文件完整路径（保留原文件名）
        filename = os.path.basename(source_file)
        target_path = os.path.join(target_directory, filename)
        
        # 执行移动操作
        shutil.move(source_file, target_path)
        print(f"文件已成功移动到：{target_path}")
        return True
    
    except Exception as e:
        print(f"移动文件时发生错误：{str(e)}")
        return False

        


# 使用 sync_playwright 启动 Playwright
def goDoubao(page, fileName):
    # 启动 Chromium 浏览器，headless=False 表示可见模式便于调试
    
    
    # 1. 信息录入
    input_selector = '#root > div.flow-web-root-outlet > div > div.containerWrapper-NWa4Sz > div.panelWrapper-O67Mdi.left-side-width--variable-aVHci6 > div.center-full-dpDzPj > div > div > div.footer-WyRAth > div > div > div > div:nth-child(3) > div.input-content-container-_k2eqc > div.container-VhbUmi.guidance-input-yS_o_1 > div.editor-container-kXzeJr > div.editor-wrapper-UClPXc > div > textarea'
    page.fill(input_selector, '以上图片是古文排版自上而下，自右而左， 请提取文字')  # 替换为实际需要填写的内容

    # 2. 上传附件
    # 通过 SVG path 定位上传按钮
    upload_button = page.locator('svg:has(path[d="M9.035 15.956a1.29 1.29 0 0 0 1.821-.004l6.911-6.911a3.15 3.15 0 0 0 0-4.457l-.034-.034a3.15 3.15 0 0 0-4.456 0l-7.235 7.234a5.031 5.031 0 0 0 7.115 7.115l6.577-6.577a1.035 1.035 0 0 1 1.463 1.464l-6.576 6.577A7.1 7.1 0 0 1 4.579 10.32l7.235-7.234a5.22 5.22 0 0 1 7.382 0l.034.034a5.22 5.22 0 0 1 0 7.383l-6.91 6.91a3.36 3.36 0 0 1-4.741.012l-.006-.005-.012-.011a3.346 3.346 0 0 1 0-4.732L12.76 7.48a1.035 1.035 0 0 1 1.464 1.463l-5.198 5.198a1.277 1.277 0 0 0 0 1.805z"])')
    
    #upload_button.click()  # 点击上传按钮

    # 设置文件上传（替换为实际文件路径）
    print(f"上传文件名{fileName}")
    page.set_input_files('input[type="file"]', fileName)  # 替换为实际文件路径

    # 3. 点击发送按钮
    #<button disabled="" id="flow-end-msg-send" aria-disabled="true" aria-label="发送" data-testid="chat_input_send_button" class="semi-button semi-button-disabled semi-button-primary-disabled send-btn-xD8q3r semi-button-with-icon semi-button-with-icon-only" type="button" style="pointer-events: none;"><span class="semi-button-content"><span role="img" class="semi-icon semi-icon-default send-btn-icon-j_fetC"><svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="m3.543 8.883 7.042-7.047a2 2 0 0 1 2.828 0l7.043 7.046a1 1 0 0 1 0 1.415l-.701.701a1 1 0 0 1-1.414 0L13.3 5.956v15.792a1 1 0 0 1-1 1h-.99a1 1 0 0 1-1-1V6.342l-4.654 4.656a1 1 0 0 1-1.414 0l-.7-.7a1 1 0 0 1 0-1.415"></path></svg></span></span></button>

    time.sleep(3)

    # Playwright 定位方式（CSS 组合选择器）
    send_button = page.locator('button[data-testid="chat_input_send_button"][id="flow-end-msg-send"]')
    send_button.click()

    #send_button_xpath = '/html/body/div[1]/div[1]/div/div[3]/div[1]/div[1]/div/div/div[3]/div/div/div/div[3]/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[3]/div[2]/span/button'
    #page.locator(f'xpath={send_button_xpath}').click()

    goDoubaoThinkResponse(page)

def convertToText( page ):

    directory = r"E:\2025-032"
    # 列出所有的文件
    """列出指定目录下的所有PNG文件"""
    if not os.path.exists(directory):
        print(f"错误: 目录 '{directory}' 不存在")
        return []
    
    if not os.path.isdir(directory):
        print(f"错误: '{directory}' 不是一个目录")
        return []
    
    # 使用列表推导式生成所有PNG文件的列表(不区分大小写)
    allfile = [
        filename
        for filename in os.listdir(directory)
        if filename.lower().endswith('.png')
        and os.path.isfile(os.path.join(directory, filename))
    ]

    # 
    if allfile:


        
        i = 0
        while i < len(allfile):
            filename = allfile[i]
            # 在这里处理文件名
            print(filename)
            
            

            time.sleep(4)
            
            imgFile = f"{directory}\{filename}"
            print(imgFile)
            write_string_to_file( f"\n开始处理 {imgFile} \n" )

            try:

                goDoubao(page, imgFile)    
                time.sleep(4)
                goDoubaoThinkResponse(page)
                time.sleep(4)
                goDoubaoResponse(page)
                #滚到最下面
                scroll(page)

                #如果弄成功了，就移走
                move_file_to_directory(imgFile)

                # 控制循环是否加一，如果没有成功，还是继续重试当前文件。
                i += 1

                

            except Exception as dd:
                print( f" {imgFile} 处理失败，reset Dialog 继续" )
                resetDialog(page)

            

    else:
        print("未找到PNG文件")


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
        print("wait think ...")
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



def get_inner_text(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    target_div = soup.find('div', {
        'data-testid':'message_text_content'
    })
    if target_div:
        return target_div.get_text()
    else:
        return ""
    

def goDoubaoResponse(page):   
    
    # 4. 监听后台返回结果
    response_container_selector = '.container-QE4ayg'
    previous_content = ''
    current_content = ''
    max_wait_time = 60  # 最大等待时间（秒）
    check_interval = 1  # 检查间隔（秒）
    elapsed_time = 0

    sel = page.locator(response_container_selector).last
    
    while True:
        print("wait reponse ...")
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
    log_content = get_inner_text( sel.inner_html() )
    write_string_to_file( log_content )
    

def scroll(page):
    # 使用第一种选择器
    button = page.locator('.container-u3ALXo.to-bottom-button-NfAcu0')
    print(f"find scroll{button}")
    try:

        if button.is_enabled():
            print("按钮存在且可点击")
            if button.is_visible():
                print("按钮可见，可以点击")
                button.click()
                print("按钮未被禁用，可以点击 ok")
        else:
            print("按钮被禁用，无法点击")
    except Exception as dd:
        print( " 滚动失败" )
        
   
    
    

    # 或使用更稳定的选择器
    #button = page.locator('div:has(> span[role="img"]) > svg > path[d*="M21.707"]')
    #button.wait_for(state='visible')

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


    convertToText(page)

    #resetDialog(page)
    

    
    
if __name__ == "__main__":    
    with sync_playwright() as playwright:
        run(playwright)

    