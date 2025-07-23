'''
这是我一个web网站的界面，其中上面横向的是一级菜单，左边纵向的是二级菜单。
我希望你帮我写一个程序，把所有菜单及其菜单的连接都抓取出来。
输出需要按照菜单的级别树形组织数据。包括菜单名称和菜单连接。
我希望是用playwright插件。
我已经在调试模式下打开了网站的page，程序只需要连接到browser判断page的url = “http://39.105.217.139:8181/yhbackstage/Index/index”。

程序希望能够同时记录日志到日志文件，并且同时在控制台打印输出。
程序最好有一定的健壮性，可以适合不同类型的网站。
请分析问题，并提供解决方案及代码。

第3版本，可以定制代理商管理和系统管理；


第4版本，重新生成了代码，并且需要手工定义系统管理和代理商管理的ul；


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
        # 定位 <a> 标签
        a_element = li_element.locator('a').first
        # 提取菜单名称（从 title 属性）
        menu_name = a_element.get_attribute('title') or a_element.inner_text().strip()
        # 提取链接（从 href 属性）
        menu_link = a_element.get_attribute('href') or 'javascript:;'
        return menu_name, menu_link
    except Exception as e:
        logging.error(f"提取菜单项失败: {e}")
        return None, None

def build_sub_menu_tree(ul_element):
    """从 <ul class='ztree ztree_main'> 或其他嵌套 <ul> 构建子菜单树"""
    menu_tree = []
    try:
        # 获取所有 <li> 元素
        li_elements = ul_element.locator('li').all()
        print(f">>>build_sub_menu_tree {ul_element}  的子li 的数量 {len(li_elements)}")
        for li in li_elements:
            menu_name, menu_link = extract_menu_item(li)
            if menu_name:
                # 检查是否有嵌套的 <ul>（子菜单）
                sub_ul = li.locator('ul').first
                sub_menu = []
                if sub_ul.is_visible():
                    sub_menu = build_sub_menu_tree(sub_ul)
                menu_tree.append({
                    'name': menu_name,
                    'link': menu_link,
                    'sub_menu': sub_menu
                })
    except Exception as e:
        logging.error(f"构建子菜单树失败: {e}")
    return menu_tree

def extract_menu(page):
    """提取一级菜单及其子菜单"""
    menu_tree = []
    try:
        # 等待页面加载完成
        page.wait_for_load_state('networkidle', timeout=10000)
        logging.info("开始提取菜单")

        # 提取一级菜单
        debugLen = 0

        first_level_items = page.locator('#bjui-hnav-navbar > li').all()
        for item in first_level_items:
            
            debugLen = debugLen+1
            if debugLen > 2:
                break

            try:
                # 提取一级菜单名称和链接
                a_element = item.locator('a').first
                menu_name = a_element.inner_text().strip()
                menu_link = a_element.get_attribute('href') or 'javascript:;'

                # 提取子菜单容器 <div class="items">
                sub_menu_div = item.locator('div.items').first
                sub_menu_tree = []


                if sub_menu_div:
                    # 获取 <ul class="ztree ztree_main">
                    print(f"print CCC item{ ul_element } >>>{menu_name}")
                    ul_element = sub_menu_div.locator('ul.ztree.ztree_main').first

                    if menu_name == '系统管理':                        
                        ul_element = page.locator('#bjui-hnav-tree01000000_1_ul')
                        print(f"print AAA系统管理 sub_menu_div{ ul_element.inner_html()  }")
                    elif menu_name == '代理商管理':                      
                        ul_element = page.locator('#bjui-hnav-tree02000000_1_ul')
                        print(f"print AAA代理商管理 sub_menu_div{ ul_element.inner_html() }")

                    if ul_element:
                        # 构建子菜单树
                        sub_menu_tree = build_sub_menu_tree(ul_element)

                menu_tree.append({
                    'name': menu_name,
                    'link': menu_link,
                    'sub_menu': sub_menu_tree
                })
            except Exception as e:
                logging.error(f"提取一级菜单项失败: {e}")

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
            # 连接到调试模式的浏览器
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