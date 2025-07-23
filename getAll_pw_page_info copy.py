from playwright.sync_api import sync_playwright

import os
from datetime import datetime

def capture_page_info():
    """打印当前页面 HTML 并截图"""
    with sync_playwright() as playwright:
        try:
            # 连接到 Chrome 调试端口
            browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("成功连接到 Chrome 调试端口")

            # 枚举所有上下文
            for context in browser.contexts:
                print(f"Context ID: {context}")
                # 枚举当前上下文下的所有页面
                for page1 in context.pages:
                    print(f"  Page URL: {page1.url}")
                    if page1.url == 'http://39.105.217.139:8181/yhbackstage/Index/index':
                        page = page1
            print("自检完成")
            print(f"\n\nPage title: {page.title()}\n\n")
            print(">>Go")


            # 获取页面完整 HTML
            html_content = page.content()
            print("\n=== 页面 HTML ===")
            print(html_content[:1000] + "..." if len(html_content) > 1000 else html_content)
            print("==================")

            output_dir="screenshots"
    
            # 创建输出目录（如果不存在）
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                    
            # 生成带有时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存 HTML 到文件
            output_path = os.path.join(output_dir, f"page_{timestamp}.html")
            print(f" >>>OUTPUT HTML>>>{output_path}")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"HTML 已保存为 {output_path}")

            # 截图
            
            output_path = os.path.join(output_dir, f"screenshot_{timestamp}.png")
            print(f" >>>OUTPUT SCREENSHOT>>>{output_path}")
            page.screenshot(path=output_path, full_page=True)
            print(f"截图已保存为 {output_path}")

        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            print("任务完成，浏览器保持打开状态")

if __name__ == "__main__":
    capture_page_info()