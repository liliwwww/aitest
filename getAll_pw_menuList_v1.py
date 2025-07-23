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

def extract_menu_item(li_element):
    """提取单个菜单项的名称和链接"""
    try:
        # 提取菜单名称（<li> 的文本内容）
        menu_name = li_element.inner_text().strip()
        # 提取链接，若无 data-url 则默认 javascript:;
        menu_link = li_element.get_attribute('data-url') or 'javascript:;'
        return menu_name, menu_link
    except Exception as e:
        logging.error(f"提取菜单项失败: {e}")
        return None, None

def build_menu_tree(page, parent_id='0', level=0):
    """递归构建菜单树"""
    menu_tree = []
    try:
        # 根据层级选择菜单项
        if level == 0:
            # 一级菜单：从 #bjui-hnav-navbar > li 提取
            menu_items = page.locator('#bjui-hnav-navbar > li')
        else:
            # 子菜单：从 .ztree li[data-pid="{parent_id}"] 提取
            menu_items = page.locator(f'.ztree li[data-pid="{parent_id}"]')

        items = menu_items.all()
        if not items:
            return menu_tree

        for item in items:
            menu_id = item.get_attribute('data-id') if level > 0 else f"level0_{items.index(item)}"
            menu_name, menu_link = extract_menu_item(item)
            if menu_name:
                # 递归构建子菜单
                sub_menu = build_menu_tree(page, parent_id=menu_id, level=level + 1)
                menu_tree.append({
                    'name': menu_name,
                    'link': menu_link,
                    'sub_menu': sub_menu
                })
    except Exception as e:
        logging.error(f"构建菜单树失败: {e}")
    return menu_tree

def extract_menu(page):
    """提取菜单并构建树形结构"""
    try:
        # 等待页面加载
        page.wait_for_load_state('networkidle', timeout=10000)
        logging.info("开始提取菜单")

        # 构建菜单树
        menu_tree = build_menu_tree(page)
        return menu_tree
    except TimeoutError:
        logging.error("页面加载超时")
        return []
    except Exception as e:
        logging.error(f"提取菜单时发生未知错误: {e}")
        return []

def print_menu_tree(menu_tree, indent=0):
    """打印菜单树到控制台"""
    for menu in menu_tree:
        print('  ' * indent + f"{menu['name']} - {menu['link']}")
        if menu['sub_menu']:
            print_menu_tree(menu['sub_menu'], indent + 1)

def main():
    """主函数：连接浏览器并提取菜单"""
    with sync_playwright() as p:
        try:
            # 连接到调试模式的浏览器（默认端口 9222）
            browser = p.chromium.connect_over_cdp('http://localhost:9222')
            pages = browser.contexts[0].pages
            target_page = None

            # 查找目标页面
            for page in pages:
                if 'yhbackstage/Index/index' in page.url:
                    target_page = page
                    break

            if not target_page:
                logging.error("未找到目标页面")
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
            print_menu_tree(menu_tree)

        except Exception as e:
            logging.error(f"程序执行失败: {e}")
        finally:
            if 'browser' in locals():
                browser.close()

if __name__ == '__main__':
    main()