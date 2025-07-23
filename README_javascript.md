按钮与下拉菜单的关联逻辑（以 Bootstrap 为例）
1. DOM 结构的隐含关联
每个 <button> 通常与其对应的下拉菜单 <div class="dropdown-menu"> 存在于同一个父容器（如 <div class="btn-group">）中。例如：
html
预览
<div class="btn-group">
  <button data-id="agent_nature">...</button> <!-- 按钮 -->
  <div class="dropdown-menu">...</div> <!-- 对应的下拉菜单 -->
</div>


JavaScript 通过 DOM 遍历找到最近的关联菜单：当点击按钮时，脚本会通过 parentNode 找到父容器 btn-group，然后在其中查找 <div class="dropdown-menu"> 子元素。

2. 数据属性（data-*）的显式关联

按钮的 data-id 属性通常对应 <select> 元素的 id（如 data-id="agent_nature" 对应 <select id="agent_nature">）。

<button class="btn dropdown-toggle selectpicker btn-default" data-id="agent_nature" data-toggle="dropdown" title="请选择" type="button">

<select class="show-tick" data-toggle="selectpicker" id="agent_nature" name="agent_nature" selectvl="" style="height: 25px; display: none;">


插件初始化时会建立映射关系：将每个按钮的 data-id 与对应的 <select> 和下拉菜单 <div> 绑定。例如，通过一个对象存储 {id: 下拉菜单元素}。













```py
async def select_option_and_verify(page: Page, select_selector: str, target_text: str) -> bool:
    """
    Selects an option in a <select> or selectpicker by text and verifies the selected value.
    
    Args:
        page: Playwright Page object.
        select_selector: CSS selector for the <select> element (e.g., 'select[name="agent_status"]').
        target_text: Text of the option to select (e.g., '已驳回').
    
    Returns:
        bool: True if the select's current value matches the target option's value, False otherwise.
    """
    try:
  
        # 1. 定义目标选项和选择器
        target_option_text = target_text
        select_id = select_selector

        print(f"select_option_and_verify1    》》》 {select_id}》》》 {target_option_text}")
        
        # 2. 定位并点击下拉按钮
        dropdown_button_selector = f'button[data-id="{select_id}"]'

        print(f"select_option_and_verify2   》》》 {dropdown_button_selector}")
        button = await page.wait_for_selector(dropdown_button_selector, state='visible')
        print(f"select_option_and_verify2.1   》》》 ")
        
        await button.click()
        print(f"select_option_and_verify2.2   》》》 ")

        
        
        # 3. 等待下拉菜单展开并定位目标选项
        # 使用 XPath 处理可能包含空格的文本

        # 立云的方法
        # 在bootstrap框架中，每次下列框打开的div， 都叫这个名字；
        option_xpath = '.btn-group.bootstrap-select.show-tick.open>.dropdown-menu.open'

        btn_group = await page.wait_for_selector(option_xpath)  # '..' 表示父元素
        print(f"select_option_and_verify5   inner》》》 {await btn_group.inner_html() }")
        # print(f"select_option_and_verify5   outer》》》 {btn_group.outer_html() }")

        # 执行 JavaScript 代码在浏览器控制台打印
        #await page.evaluate('(element) => console.log(element.outerHTML)', btn_group)
        
        # 获取父元素的 outerHTML
        btn_group_html = await btn_group.evaluate('el => el.outerHTML')
        print(f"select_option_and_verify5   js》》》 {btn_group_html }")


        
        #option_xpath = f'.//ul[contains(@class, "dropdown-menu inner")]//li/a/span[normalize-space(text())="{target_option_text}"]'
        #option_xpath = f'.//ul[contains(concat(" ", normalize-space(@class), " "), " dropdown-menu inner ")]//li/a/span[normalize-space(text())="{target_option_text}"]'
        #option_xpath = '.dropdown-menu.inner >> xpath=.//span[normalize-space(text())="{}"]'.format(target_option_text.strip() )
        

        # 使用CSS选择器结合XPath
        # 在btn-group容器内定位选项
        # 使用CSS选择器定位下拉菜单，XPath定位选项文本

        #然后在父亲窗口中， 再查找text
        option_selector = '.dropdown-menu.inner >> xpath=.//span[contains(text(), "{}")]'.format(target_option_text.strip())
    

        print(f"select_option_and_verify5.1   》》》 {option_selector}")

        # 在btn_group上下文中查找选项
        option = await btn_group.wait_for_selector(option_selector, state='visible')
        print(f"select_option_and_verify5.2   》》》 ")
        # 点击选项
        await option.click()


        # 4. 验证选择结果（可选）
        selected_value = await page.eval_on_selector(
            f'select#{select_id}',
            'select => select.value'
        )
        print(f"select_option_and_verify4   》》》 {selected_value}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
```