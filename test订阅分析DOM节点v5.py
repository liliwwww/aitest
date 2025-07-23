
'''
需求：
我希望试用chrome的CDP协议，监听当前页面DOM结构的变化，如果页面DOM发生变化后，把发生变化的内容打印出来。

因为浏览器DOM可能随时发生变化，我希望等到浏览器网络IDEL的时候再进行比较。

帮我生成python代码


'attributes'（属性变更）
'childList'（子节点列表变更）
'characterData'（文本内容变更）


'''
import asyncio
import requests
import time
import logging
from pyppeteer import launch
from pyppeteer import connect

# 配置日志记录
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler('dom_changes.log')
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 定义日志格式
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class DOMChangeMonitor:
    def __init__(self):
        self.dom_changes = []
        self.pending_requests = 0
        self.network_idle = asyncio.Event()
        self.timer = None
        self.shutdown = False

    async def start(self):
        # 获取 Chrome 调试模式的 WebSocket 端点
        response = requests.get('http://localhost:9222/json/version')
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        browser_ws_url = data['webSocketDebuggerUrl']
        logger.info(f"浏览器级别的 WebSocket 端点: {browser_ws_url}")

        # 连接到浏览器
        browser = await connect(browserWSEndpoint = browser_ws_url, defaultViewport= None,args= [])

        # 导航到目标 URL
        target_url = 'http://39.105.217.139:8181/yhbackstage/Index/index'
        is_find = False
        # 获取所有页面
        pages = await browser.pages()
        for page in pages:
            # 打印页面的 URL
            logger.info(f"页面 URL: {page.url}")
            if page.url == target_url:
                logger.info("找到了目标 page, 跳出")
                is_find = True
                self.page = page
                break

        if is_find:
            logger.info(f"连接到了{page.url}页面")
        else:
            logger.info("没有找到目标的页面")

        self.cdp = await self.page.target.createCDPSession()
        await self.setup_network_monitoring()
        await self.setup_dom_monitoring()
        logger.info(" createCDPSession() ")

        logger.info("Monitoring started. Press Ctrl+C to exit...")
        await self.monitor_loop()

    async def setup_network_monitoring(self):
        await self.cdp.send('Network.enable')
        self.cdp.on('Network.requestWillBeSent', self.on_request_start)
        self.cdp.on('Network.responseReceived', self.on_request_end)
        self.cdp.on('Network.loadingFinished', self.on_request_end)
        self.cdp.on('Network.loadingFailed', self.on_request_end)

    async def setup_dom_monitoring(self):
        await self.page.evaluate('''() => {
            // XPath生成函数
            window.getXPath = function(element) {
                if (element.id) {
                    return '//*[@id="' + element.id + '"]';
                }
                if (element === document.body) {
                    return '/html/body';
                }

                let path = [];
                while (element !== document.documentElement && element.parentNode) {
                    let index = 1;
                    let siblings = element.parentNode.childNodes;
                    for (let i = 0; i < siblings.length; i++) {
                        let sibling = siblings[i];
                        if (sibling === element) {
                            path.unshift(element.tagName + '[' + index + ']');
                            break;
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            index++;
                        }
                    }
                    element = element.parentNode;
                }
                return '/html/' + path.join('/');
            };

            window.domChanges = [];
            const observer = new MutationObserver(mutations => {
                window.domChanges.push(...mutations.map(mutation => ({
                    type: mutation.type,
                    target: {
                        nodeName: mutation.target.nodeName,
                        attributes: Array.from(mutation.target.attributes).reduce((obj, attr) => {
                            obj[attr.name] = attr.value;
                            return obj;
                        }, {}),
                        nodeValue: mutation.target.nodeValue,
                        xpath: window.getXPath(mutation.target),
                        outerHTML: mutation.target.outerHTML
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

    async def collect_dom_changes(self):


        changes = await self.page.evaluate('''() => {
            const changes = window.domChanges.filter(c => c.type);
            window.domChanges = [];
            return changes;
        }''')
        return changes

    def print_mutation(self, mutation):
        target = mutation.get('target', {})
        xpath = target.get('xpath', 'Unknown XPath')

        outer_html = target.get('outerHTML', 'Unknown')
        if len(outer_html) > 200:
            outer_html = outer_html[:200] + '...'  # 保留前200字符并添加省略号

        if mutation['type'] == 'attributes':
            log_message = f"Attribute changed at {xpath}\n"
            log_message += f"  Element: {target.get('nodeName', 'Unknown')}\n"
            log_message += f"  Attribute: {mutation.get('attributeName', 'Unnamed')}\n"
            log_message += f"  New value: {target.get('attributes', {}).get(mutation.get('attributeName'), '')}\n"
            
            log_message += f"  HTML: {outer_html}"
            logger.info(log_message)
        elif mutation['type'] == 'characterData':
            log_message = f"Text changed at {xpath}\n"
            log_message += f"  Element: {target.get('nodeName', 'Unknown')}\n"
            log_message += f"  Content: {str(target.get('nodeValue', '')).replace('\n', ' ')[:50]}...\n"
            log_message += f"  HTML: {outer_html}"
            logger.info(log_message)
        elif mutation['type'] == 'childList':
            log_message = f"Children modified at {xpath}\n"
            log_message += f"  Element: {target.get('nodeName', 'Unknown')}\n"
            log_message += f"  Added: {mutation.get('addedNodes', 0)}, Removed: {mutation.get('removedNodes', 0)}\n"
            log_message += f"  HTML: {outer_html}"
            logger.info(log_message)

    async def monitor_loop(self):
        try:
            while not self.shutdown:
                await self.network_idle.wait()
                changes = await self.collect_dom_changes()
                if changes:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    logger.info(f"\n ===={timestamp} Detected {len(changes)} DOM changes...")

                    for change in changes:
                        self.print_mutation(change)
                self.network_idle.clear()
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.error("ERROR")
            # await self.cleanup()

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
    