from playwright.sync_api import sync_playwright, Playwright

# 点击查询按钮，
# 输出列表信息；

operation_buttons = []  # 存储操作列按钮的 HTML 和元素


def query_A(page):

    
    try:
        # 步骤 1：点击查询按钮
        # option 1 ：by selector
        #query_button_selector = '//*[@id="pagerForm"]/div/p[4]/button'
        #page.wait_for_selector(query_button_selector, timeout=10000)  # 等待按钮出现
        #page.click(query_button_selector)
        

        # 使用 CSS 选择器定位按钮
        button_locator = page.locator("#pagerForm > div > p:nth-child(4) > button")
        print(" locator 1")    
        # 等待并点击
        button_locator.wait_for(state="visible", timeout=10000)
        
        print(" locator 2")
        button_locator.click()
        
        print("查询按钮已点击")

        # 等待表格加载
        table_selector = "table.table.table-bordered"
        page.wait_for_selector(f"{table_selector} tbody", timeout=10000)  # 等待 tbody 出现

        # 步骤 2：提取表头
        headers = page.query_selector_all(f"{table_selector} thead tr:nth-child(2) th div.fixedtableCol")
        header_texts = [header.inner_text().strip() for header in headers]
        print("\n表头:")
        print(" | ".join(header_texts))
        print("-" * 100)

        # 提取 tbody 内容
        

        rows = page.query_selector_all(f"{table_selector} tbody tr")
        print("表格内容:")
        for row_idx, row in enumerate(rows, 1):
            print(f"\n行 {row_idx}:")
            cells = row.query_selector_all("td")
            for col_idx, cell in enumerate(cells):
                # 处理操作列（最后一列）
                if col_idx == len(headers) - 1:  # 最后一列是“操作”
                    button = cell.query_selector("a.btn.btn-blue.permission")  # 定位按钮
                    button_html = button.evaluate("el => el.outerHTML") if button else "无按钮"
                    cell_text = "Button"  # 显示为 Button，HTML 单独输出
                    operation_buttons.append({"html": button_html, "element": button})
                    print(f"列 {col_idx + 1} ({header_texts[col_idx]}): {cell_text}")
                    print(f"  按钮 HTML: {button_html}")
                else:
                    cell_text = "Radio Button" if col_idx == 0 else cell.inner_text().strip()
                    print(f"列 {col_idx + 1} ({header_texts[col_idx]}): {cell_text}")

        # 打印按钮数组
        print("\n操作按钮数组:")
        for idx, btn in enumerate(operation_buttons):
            print(f"索引 {idx}: {btn['html']}")
        
        
    except Exception as e:
        print(f"发生错误: {e}")
        # 保存截图便于调试
        page.screenshot(path="error_screenshot.png")
        print("已保存错误截图: error_screenshot.png")

    finally:
        # 保持浏览器打开（调试模式下不关闭）
        print("任务完成，浏览器保持打开状态")


def select_A_row(page, user_input):

    print(f"\>>>select_A_row  {user_input}")
    try:
        
        button_idx = int(user_input)
        if 0 <= button_idx < len(operation_buttons):
            button = operation_buttons[button_idx]["element"]
            #print(f"{}")
            if button:
                button.click()
                print(f"已点击索引 {button_idx} 的按钮")
                # 等待页面可能的变化（例如弹窗或跳转）
                page.wait_for_timeout(2000)  # 2秒，视情况调整
            else:
                print("按钮不可用")
        else:
            print(f"无效索引，请输入 0 到 {len(operation_buttons) - 1} 之间的数字")
    except ValueError:
        print("请输入有效数字或 'q'")
    except Exception as e:
        print(f"点击按钮时出错: {e}")

# 运行 Playwright
with sync_playwright() as playwright:

    try:
            
        print("step1")
        # 连接到已打开的 Chrome 调试端口
        try:
            browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("成功连接到 Chrome 调试端口")
        except Exception as e:
            print(f"无法连接到调试端口: {e}")
            print("请确保 Chrome 已以调试模式启动 (--remote-debugging-port=9222)")
            exit

        print("step2")
        # 获取默认上下文和页面（使用已打开的页面）
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        
        print("step3")
        page = context.pages[0] if context.pages else context.new_page()

        print("step4")
        query_A(page)

        print("step5")
        select_A_row(page, 3)

        print("\n\n\n EXIT NORMAL ")    
    except Exception as e:
        print(f"\n\n\n EXIT ERROR : {e}")    