import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("你的目标网页")

        select_selector = "你的选择器"
        target_text = "目标选项文本"

        # 所有方法前添加 await
        print("select_option_and_verify1    》》》")
        await page.wait_for_selector(select_selector, state="attached", timeout=10000)
        print(f"select_option_and_verify2    》》》 Found select element: {select_selector}")

        is_select_visible = await page.eval_on_selector(
            select_selector, 'el => window.getComputedStyle(el).display !== "none"'
        )
        print(f"Is native select visible: {is_select_visible}")

        options = await page.query_selector_all(f"{select_selector} option")
        target_value = None
        for option in options:
            text = await option.text_content()  # 异步获取文本
            if text.strip() == target_text:
                target_value = await option.get_attribute('value')  # 异步获取属性
                print(f"Found option with text '{target_text}' and value '{target_value}'")
                break

        if not target_value:
            print(f"No option with text '{target_text}' found")
            for option in options:
                text = await option.text_content()
                value = await option.get_attribute('value')
                print(f"Option: text='{text}', value='{value}'")
            await browser.close()
            return

        if is_select_visible:
            await page.select_option(select_selector, value=target_value)
            print(f"Selected '{target_text}' using native select")
        else:
            select_id = await page.eval_on_selector(select_selector, 'el => el.id')
            button_selector = f'div.bootstrap-select button[data-id="{select_id}"]'
            option_selector = f'//div[contains(@class, "bootstrap-select")]//a[span[text()="{target_text}"]]'

            await page.wait_for_selector(button_selector, state="visible", timeout=5000)
            await page.click(button_selector)
            print("Opened selectpicker dropdown")

            await page.wait_for_selector(option_selector, state="visible", timeout=5000)
            await page.click(option_selector)
            print(f"Selected '{target_text}' from selectpicker dropdown")

            await page.evaluate(
                """
                (args) => {
                    const select = document.querySelector(args.select_selector);
                    select.value = args.value;
                    const event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                }
                """,
                {"select_selector": select_selector, "value": target_value}
            )

        current_value = await page.eval_on_selector(select_selector, 'el => el.value')
        print(f"Current select value: '{current_value}', Expected value: '{target_value}'")
        await browser.close()

asyncio.run(main())