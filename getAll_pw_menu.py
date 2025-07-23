import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError

async def get_menu_items(page):
    """提取菜单项及其选择器"""
    # 等待菜单加载
    await page.locator('#bjui-accordionmenu').wait_for(state="visible", timeout=10000)
    
    # 获取所有叶子菜单项（有有效 href 的 <a>）
    menu_elements = await page.locator(
        '#bjui-accordionmenu a[href]:not([href="javascript:;"])'
    ).all()
    
    menu_items = []
    for element in menu_elements:
        title = await element.get_attribute('title')
        print(f">>>menu >>>{title} ")
        if title:  # 确保有 title
            selector = f'a[title="{title}"]'
            menu_items.append({
                'name': title,
                'selector': selector,
                'href': await element.get_attribute('href')
            })
    
    
    return menu_items

async def print_menu_items(menu_items):
    """打印菜单项列表"""
    print("\n可用菜单项：")
    for i, item in enumerate(menu_items, 1):
        print(f"{i}. {item['name']} (选择器: {item['selector']})")

async def navigate_to_menu(page, menu_name, menu_items):
    """根据菜单名称跳转"""
    for item in menu_items:
        if item['name'].lower() == menu_name.lower():
            print(f"\n尝试跳转到: {item['name']}")
            try:
                # 确保菜单可见
                await page.locator('#bjui-accordionmenu').wait_for(state="visible", timeout=10000)
                
                # 点击菜单项
                await page.locator(item['selector']).wait_for(state="visible", timeout=10000)
                await page.locator(item['selector']).click()
                
                # 等待页面加载（navtab 切换）
                await page.wait_for_load_state('networkidle', timeout=15000)
                print(f"成功跳转到: {item['name']} (URL: {page.url})")
                await page.screenshot(path=f"screenshot_{item['name']}.png")
                return True
            except TimeoutError:
                print(f"错误: 菜单 '{item['name']}' 在 10000ms 内不可见")
                await page.screenshot(path="error_timeout.png")
                return False
            except Exception as e:
                print(f"跳转错误: {e}")
                await page.screenshot(path="error_general.png")
                return False
    
    print(f"错误: 未找到菜单 '{menu_name}'")
    return False

async def main():
    async with async_playwright() as p:
        try:
            # 连接现有浏览器（基于你的 CDP 调试端口）
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[-1]  # 使用最新页面
            print(f"当前 URL: {page.url}")

            # 获取菜单项
            menu_items = await get_menu_items(page)
            
            # 打印菜单项
            await print_menu_items(menu_items)
            
            # 循环提示用户输入
            while True:
                menu_name = input("\n请输入菜单名称（输入 '退出' 结束）：")
                if menu_name.lower() == '退出':
                    print("程序退出")
                    break
                
                # 执行跳转
                success = await navigate_to_menu(page, menu_name, menu_items)
                if not success:
                    print("请检查菜单名称或页面状态后重试")
                
        except Exception as e:
            print(f"主程序错误: {e}")
            await page.screenshot(path="main_error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())