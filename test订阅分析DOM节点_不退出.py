
'''
需求：
我希望试用chrome的CDP协议，监听当前页面DOM结构的变化，如果页面DOM发生变化后，把发生变化的内容打印出来。

因为浏览器DOM可能随时发生变化，我希望等到浏览器网络IDEL的时候再进行比较。

帮我生成python代码

'''
#查看是那个venv
#python -c "import sys; print(sys.path)"

import asyncio
import requests
from pyppeteer import connect


async def main():
    # 获取 Chrome 调试模式的 WebSocket 端点
    response = requests.get('http://localhost:9222/json/version')
    response.raise_for_status()  # 检查请求是否成功
    data = response.json()
    browser_ws_url = data['webSocketDebuggerUrl']
    print(f"浏览器级别的 WebSocket 端点: {browser_ws_url}")

    # 连接到浏览器
    browser = await connect(browserWSEndpoint=browser_ws_url)

    # 导航到目标 URL
    target_url = 'http://39.105.217.139:8181/yhbackstage/Index/index'
    is_find = False
    # 获取所有页面
    pages = await browser.pages()
    for page in pages:
        # 打印页面的 URL
        print(f"页面 URL: {page.url}")
        if page.url == target_url:
            print("找到了目标 page, 跳出")
            is_find = True
            break

    if is_find:
        print(f"连接到了{page.url}页面")
    else:
        print("没有找到目标的页面")

    # 启用 Network 领域以支持 waitForNetworkIdle
    await page._client.send('Network.enable')

    # 用于存储 DOM 变化的列表
    changes = []
    # 标志位，控制是否正在等待网络空闲
    is_waiting = False

    # 定义处理 DOM 变化的异步函数
    async def dom_changed(description):
        nonlocal changes, is_waiting
        changes.append(description)
        if not is_waiting:
            is_waiting = True
            await page.waitForNetworkIdle()  # 等待网络空闲
            print('DOM 变化如下:')
            for change in changes:
                print(f'- {change}')
            changes.clear()
            is_waiting = False

    # 将 Python 函数暴露给 JavaScript
    await page.exposeFunction('domChanged', dom_changed)

    # 注入 JavaScript 代码，使用 MutationObserver 监听 DOM 变化
    await page.evaluate('''() => {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                let description = '';
                if (mutation.type === 'childList') {
                    description = `子节点变化在 ${mutation.target.tagName}${mutation.target.id ? '#' + mutation.target.id : ''}`;
                } else if (mutation.type === 'attributes') {
                    description = `属性 ${mutation.attributeName} 变化在 ${mutation.target.tagName}${mutation.target.id ? '#' + mutation.target.id : ''}`;
                }
                window.domChanged(description);
            });
        });
        observer.observe(document, { childList: true, subtree: true, attributes: true });
    }''')

    # 提示正在监听
    print(f'已连接到页面 {target_url}，正在监听 DOM 变化...')

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("接收到 Ctrl + C，正在退出...")
    finally:
        # 断开连接（不会关闭浏览器窗口）
        await browser.disconnect()


# 运行异步任务
asyncio.run(main())
    