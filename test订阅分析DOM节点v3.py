
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
import time
from pyppeteer import launch
from pyppeteer import connect

class DOMChangeMonitor:
    def __init__(self):
        self.dom_changes = []
        self.pending_requests = 0
        self.network_idle = asyncio.Event()
        self.timer = None
        self.shutdown = False
        
        # 添加节流控制
        self.last_print = 0
        self.print_interval = 1  # 秒

    async def start(self):

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
                self.page = page
                break

        if is_find:
            print(f"连接到了{page.url}页面")
        else:
            print("没有找到目标的页面")

        
        self.cdp = await self.page.target.createCDPSession()
        await self.setup_network_monitoring()
        await self.setup_dom_monitoring()
        print(" createCDPSession() ")

        print("Monitoring started. Press Ctrl+C to exit...")
        await self.monitor_loop()

    async def setup_network_monitoring(self):
        await self.cdp.send('Network.enable')
        self.cdp.on('Network.requestWillBeSent', self.on_request_start)
        self.cdp.on('Network.responseReceived', self.on_request_end)
        self.cdp.on('Network.loadingFinished', self.on_request_end)
        self.cdp.on('Network.loadingFailed', self.on_request_end)

    #
    async def setup_dom_monitoring(self):
        await self.page.evaluate('''() => {
            window.domChanges = [];
            const observer = new MutationObserver(mutations => {
                // 过滤并结构化需要的数据
                window.domChanges.push(...mutations.map(mutation => ({
                    type: mutation.type,
                    target: {
                        nodeName: mutation.target.nodeName,
                        attributes: Array.from(mutation.target.attributes).reduce((obj, attr) => {
                            obj[attr.name] = attr.value;
                            return obj;
                        }, {}),
                        nodeValue: mutation.target.nodeValue
                    },
                    attributeName: mutation.attributeName,
                    addedNodes: mutation.addedNodes.length,
                    removedNodes: mutation.removedNodes.length
                })));
            });
            observer.observe(document.documentElement, {
                subtree: true,
                childList: true,
                attributes: true,
                attributeOldValue: true,
                characterData: true,
                characterDataOldValue: true
            });
        }''')

    def on_request_start(self, _):
        self.pending_requests += 1
        self.network_idle.clear()
        if self.timer:
            self.timer.cancel()

    def on_request_end(self, _):
        self.pending_requests -= 1
        if self.pending_requests == 0:
            self.schedule_idle_check()

    def schedule_idle_check(self):
        if self.timer:
            self.timer.cancel()
        loop = asyncio.get_event_loop()
        self.timer = loop.call_later(0.5, lambda: self.network_idle.set())

    # 在collect_dom_changes中增加过滤
    async def collect_dom_changes(self):
        changes = await self.page.evaluate('''() => {
            const changes = window.domChanges.filter(c => c.type);  // 过滤无效记录
            window.domChanges = [];
            return changes;
        }''')

        
        return changes

    async def monitor_loop(self):
        while not self.shutdown:
            
            
            await self.network_idle.wait()
            changes = await self.collect_dom_changes()
            if changes and (time.time() - self.last_print) > self.print_interval:
                timestamp = time.time()
                print(f"\n ===={timestamp} Detected {len(changes)} DOM changes...")
                for change in changes:
                    print(f"#add by wdp {change}")
                    self.print_mutation(change)
                self.last_print = time.time()

    #优化一版
    def print_mutation(self, mutation):
        
        if mutation['type'] == 'childList':
            print(f"子节点变更 @ {mutation['target']['nodeName']}")
            print(f"移除的节点数: {mutation['removedNodes']}")
            print(f"添加的节点数: {mutation['addedNodes']}")
            
            # 获取实际节点内容（需修改收集逻辑）
            if mutation.get('removedNodes'):
                print("被移除的节点内容:", mutation['removedNodes'][0]['outerHTML'])
            if mutation.get('addedNodes'):
                print("新添加的节点内容:", mutation['addedNodes'][0]['outerHTML'])
                
        # 在原有逻辑基础上添加
        if mutation.get('addedNodes', 0) > 5 or mutation.get('removedNodes', 0) > 5:
            print("[MAJOR CHANGE] ", end='')
            
        # 添加字段存在性检查
        mutation_type = mutation.get('type')
        if not mutation_type:
            print(f"Irregular mutation detected: {mutation}")
            return

        if mutation_type == 'attributes':
            print(f"Attribute changed on {mutation.get('target', {}).get('nodeName', 'Unknown')}: "
                f"{mutation.get('attributeName', 'Unnamed attribute')} = "
                f"{mutation.get('target', {}).get('attributes', {}).get(mutation.get('attributeName'), '')}")
        elif mutation_type == 'characterData':
            print(f"Text changed in {mutation.get('target', {}).get('nodeName', 'Unknown')}: "
                f"{str(mutation.get('target', {}).get('nodeValue', '')).replace('\n', ' ')[:50]}...")
        elif mutation_type == 'childList':
            print(f"Children modified in {mutation.get('target', {}).get('nodeName', 'Unknown')}")
        else:
            print(f"Unhandled mutation type: {mutation_type}")

    async def cleanup(self):
        await self.cdp.detach()
        await self.browser.close()

async def main():
    monitor = DOMChangeMonitor()
    try:
        await monitor.start()
    except KeyboardInterrupt:
        monitor.shutdown = True
        await monitor.cleanup()

if __name__ == '__main__':
    asyncio.run(main())