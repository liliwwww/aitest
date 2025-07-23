
'''
需求：
我希望试用chrome的CDP协议，监听当前页面DOM结构的变化，如果页面DOM发生变化后，把发生变化的内容打印出来。

因为浏览器DOM可能随时发生变化，我希望等到浏览器网络IDEL的时候再进行比较。

帮我生成python代码

'''
#查看是那个venv
#python -c "import sys; print(sys.path)"

'''
google-chrome --remote-debugging-port=9223 --user-data-dir="~/chrome-debug-profile"
'''
import asyncio
import requests
from pyppeteer import connect

async def main():
    try:
        # 获取 Chrome 调试模式的 WebSocket 端点
        response = requests.get('http://localhost:9222/json/version')
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        browser_ws_url = data['webSocketDebuggerUrl']
        print(f"浏览器级别的 WebSocket 端点: {browser_ws_url}")

        # 连接到浏览器
        browser = await connect(browserWSEndpoint=browser_ws_url)

        # 获取所有打开的页面
        pages = await browser.pages()

        # 打印每个页面的 URL
        for page in pages:
            print(f"页面 URL: {page.url}")

        # 断开连接
        await browser.disconnect()

    except requests.exceptions.RequestException as e:
        print(f"无法获取 WebSocket 端点: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

# 运行异步任务
asyncio.get_event_loop().run_until_complete(main())