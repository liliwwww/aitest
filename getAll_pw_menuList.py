'''
这是我一个web网站的界面，其中上面横向的是一级菜单，左边纵向的是二级菜单。
我希望你帮我写一个程序，把所有菜单及其菜单的连接都抓取出来。
输出需要按照菜单的级别树形组织数据。包括菜单名称和菜单连接。
我希望是用playwright插件。
我已经在调试模式下打开了网站的page，程序只需要连接到browser判断page的url = “http://39.105.217.139:8181/yhbackstage/Index/index”。

程序希望能够同时记录日志到日志文件，并且同时在控制台打印输出。
程序最好有一定的健壮性，可以适合不同类型的网站。
请分析问题，并提供解决方案及代码。
'''

import logging
from playwright.sync_api import sync_playwright, TimeoutError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('menu_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def extract_menu(page):
    """提取一级和二级菜单并组织为树形结构"""
    menu_tree = []

    try:
        # 等待页面加载完成
        page.wait_for_load_state('networkidle', timeout=10000)

        # 提取一级菜单（顶部横向）
        logging.info("开始提取一级菜单")
        first_level_menu = page.locator('nav a, ul > li > a, [role="navigation"] a')
        first_level_items = first_level_menu.all()

        if not first_level_items:
            logging.warning("未找到一级菜单元素")
            return menu_tree

        for item in first_level_items:
            try:
                menu_name = item.inner_text().strip()
                menu_link = item.get_attribute('href') or page.url  # 如果没有 href，使用当前页面 URL
                if menu_name:
                    menu_tree.append({
                        'name': menu_name,
                        'link': menu_link,
                        'sub_menu': []
                    })
            except Exception as e:
                logging.error(f"提取一级菜单项失败: {e}")

        # 提取二级菜单（左侧纵向）
        logging.info("开始提取二级菜单")
        second_level_menu = page.locator('aside a, [role="navigation"] ul li a, .sidebar a')
        second_level_items = second_level_menu.all()

        if not second_level_items:
            logging.warning("未找到二级菜单元素")
        else:
            # 假设二级菜单属于最后一个一级菜单，实际可根据网站结构调整
            for item in second_level_items:
                try:
                    menu_name = item.inner_text().strip()
                    menu_link = item.get_attribute('href') or page.url
                    if menu_name and menu_tree:
                        menu_tree[-1]['sub_menu'].append({
                            'name': menu_name,
                            'link': menu_link
                        })
                except Exception as e:
                    logging.error(f"提取二级菜单项失败: {e}")

    except TimeoutError:
        logging.error("页面加载超时")
    except Exception as e:
        logging.error(f"提取菜单时发生未知错误: {e}")

    return menu_tree

def main():
    """主函数：连接浏览器并提取菜单"""
    with sync_playwright() as p:
        try:
            # 连接到调试模式的浏览器实例（需确保浏览器以 --remote-debugging-port=9222 启动）
            browser = p.chromium.connect_over_cdp('http://localhost:9222')
            pages = browser.contexts[0].pages
            target_page = None

            # 查找目标页面
            for page in pages:
                if page.url == 'http://39.105.217.139:8181/yhbackstage/Index/index':
                    target_page = page
                    break

            if not target_page:
                logging.error("未找到目标页面 'http://39.105.217.139:8181/yhbackstage/Index/index'")
                return

            logging.info("成功连接到目标页面")
            # 提取菜单
            menu_tree = extract_menu(target_page)

            if not menu_tree:
                logging.warning("未提取到任何菜单数据")
                return

            # 输出菜单树
            logging.info("菜单树结构：")
            print("菜单树结构：")
            for menu in menu_tree:
                logging.info(f"{menu['name']} - {menu['link']}")
                print(f"{menu['name']} - {menu['link']}")
                for sub_menu in menu['sub_menu']:
                    logging.info(f"  {sub_menu['name']} - {sub_menu['link']}")
                    print(f"  {sub_menu['name']} - {sub_menu['link']}")

        except Exception as e:
            logging.error(f"程序执行失败: {e}")
        finally:
            if 'browser' in locals():
                browser.close()

if __name__ == '__main__':
    main()