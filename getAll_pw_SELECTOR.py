import re
from playwright.sync_api import Playwright, sync_playwright, Page,  expect
import time
import asyncio


### 验证一下窗口

from bs4 import BeautifulSoup


def generate_playwright_selector(html_or_attrs):
    """
    Generate a Playwright-compatible CSS selector for an HTML input, select, or button element.
    Includes all available attributes in order of priority: id > name > class > data-title > data-group > data-icon.

    Args:
        html_or_attrs (str or dict): HTML string of the element (e.g., '<input type="text" name="agent_num" ...>')
                                    or a dictionary of attributes (e.g., {'tag': 'input', 'type': 'text', 'name': 'agent_num'}).

    Returns:
        str: A Playwright selector (e.g., 'input[name="agent_num"][type="text"][class="form-control"]').

    Raises:
        ValueError: If the input is invalid or lacks identifiable attributes.
    """
    # Initialize attributes dictionary
    attrs = {}

    # Handle HTML string input
    if isinstance(html_or_attrs, str):
        try:
            soup = BeautifulSoup(html_or_attrs, 'html.parser')
            element = soup.find(['input', 'select', 'button'])
            if not element:
                raise ValueError("No input, select, or button element found in the provided HTML")
            attrs = element.attrs
            attrs['tag'] = element.name
        except Exception as e:
            raise ValueError(f"Failed to parse HTML: {e}")

    # Handle dictionary input
    elif isinstance(html_or_attrs, dict):
        attrs = html_or_attrs
        if 'tag' not in attrs or attrs['tag'] not in ['input', 'select', 'button']:
            raise ValueError("Dictionary must include 'tag' with value 'input', 'select', or 'button'")

    else:
        raise ValueError("Input must be a string (HTML) or dictionary of attributes")

    # Extract attributes
    tag = attrs.get('tag', 'input')
    elem_id = attrs.get('id', '')
    name = attrs.get('name', '')
    class_name = attrs.get('class', '')
    data_title = attrs.get('data-title', '')
    data_group = attrs.get('data-group', '')
    data_icon = attrs.get('data-icon', '')
    elem_type = attrs.get('type', '') if tag == 'input' else ''

    # Handle class attribute (can be a list or string)
    if isinstance(class_name, list):
        class_name = ' '.join(class_name)
    class_name = class_name.strip()

    # Build selector based on priority: id > name > class > data-title > data-group > data-icon
    selector_parts = [tag]
    primary_attr_added = False

    # Priority 1: id
    if elem_id:
        selector_parts.append(f'[id="{elem_id}"]')
        primary_attr_added = True

    # Priority 2: name
    if name:
        selector_parts.append(f'[name="{name}"]')
        primary_attr_added = True

    # Priority 3: class
    if class_name:
        selector_parts.append(f'[class="{class_name}"]')
        primary_attr_added = True

    # Priority 4: data-title
    if data_title:
        selector_parts.append(f'[data-title="{data_title}"]')
        primary_attr_added = True

    # Priority 5: data-group
    if data_group:
        selector_parts.append(f'[data-group="{data_group}"]')
        primary_attr_added = True

    # Priority 6: data-icon
    if data_icon:
        selector_parts.append(f'[data-icon="{data_icon}"]')
        primary_attr_added = True

    # Ensure at least one attribute was added
    if not primary_attr_added:
        raise ValueError("Element must have at least one of: id, name, class, data-title, data-group, or data-icon")

    # Add type for input elements to increase specificity
    if tag == 'input' and elem_type:
        selector_parts.append(f'[type="{elem_type}"]')

    # Combine parts into final selector
    selector = ''.join(selector_parts)
    return selector

# Example usage and tests
if __name__ == "__main__":
    # Test 1: Input element with name, class
    html_input = '<input type="text" name="agent_num" value="" class="form-control" size="15" style="width: 150px;">'
    print(generate_playwright_selector(html_input))
    # Output: input[name="agent_num"][class="form-control"][type="text"]

    # Test 2: Button element with id, data-title, data-group, data-icon, class
    html_button = '<button href="/yhbackstage/Salesman/findSales" data-toggle="lookupbtn" data-title="业务员查询" data-group="sign_sale" id="haha1" data-width="1200" data-icon="search" class="btn btn-blue">'
    print(generate_playwright_selector(html_button))
    # Output: button[id="haha1"][data-title="业务员查询"][data-group="sign_sale"][data-icon="search"][class="btn btn-blue"]

    # Test 3: Select element with name, id, class
    html_select = '<select name="agent_status" id="agent_nature" class="show-tick"></select>'
    print(generate_playwright_selector(html_select))
    # Output: select[name="agent_status"][id="agent_nature"][class="show-tick"]

    # Test 4: Button with data-title, data-group, class
    html_button_no_id = '<button data-title="业务员查询" data-group="sign_sale" class="btn btn-blue">'
    print(generate_playwright_selector(html_button_no_id))
    # Output: button[data-title="业务员查询"][data-group



'''
# Example usage and tests
if __name__ == "__main__":
    # Test 1: Input element
    html_input = '<input type="text" name="agent_num" value="" class="form-control" size="15" style="width: 150px;">'
    print(generate_playwright_selector(html_input))  # Output: input[name="agent_num"][type="text"]

    # Test 2: Button element
    html_button = '<button href="/yhbackstage/Salesman/findSales" data-toggle="lookupbtn" data-title="业务员查询" data-group="sign_sale" id="haha1" data-width="1200" data-icon="search" class="btn btn-blue">'
    print(generate_playwright_selector(html_button))  # Output: button[id="haha1"]

    # Test 3: Select element
    html_select = '<select name="agent_status" id="agent_nature" class="show-tick"></select>'
    print(generate_playwright_selector(html_select))  # Output: select[name="agent_status"]

    # Test 4: Button with no id, use data-title
    html_button_no_id = '<button data-title="业务员查询" data-group="sign_sale" class="btn btn-blue">'
    print(generate_playwright_selector(html_button_no_id))  # Output: button[data-title="业务员查询"]

    # Test 5: Dictionary input
    attrs = {
        'tag': 'button',
        'data-title': '业务员查询',
        'data-group': 'sign_sale',
        'class': 'btn btn-blue'
    }
    print(generate_playwright_selector(attrs))  # Output: button[data-title="业务员查询"]
'''

