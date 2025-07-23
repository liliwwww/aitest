from bs4 import BeautifulSoup
import re
import json
from typing import List, Dict

# ====================== 配置参数 ======================
LOCAL_HTML_PATH = r"C:\Users\wdp\project\aitest\screenshots\page_20250427_174503.html"  # 本地 HTML 文件路径

TARGET_DIV_SELECTOR = {  # 指定目标 div 的属性
    "id": "bjui-navtab",
    "class_": "tabsPage"
}
LLM_API_KEY = "sk-811ba66952094c55b56b51ff87a3013b"  # 需替换为实际 API 密钥
LLM_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"  # Deepseek 端点（示例）

# ====================== 前端解析函数（新增指定 div 范围） ======================
def parse_target_div_html(html_content: str) -> str:
    """提取目标 div 内的 HTML 内容"""
    soup = BeautifulSoup(html_content, "html.parser")
    target_div = soup.find("div", **TARGET_DIV_SELECTOR)
    return str(target_div) if target_div else ""

def parse_control_info_in_div(target_div_html: str) -> List[Dict]:
    """在目标 div 内解析控件上下文信息"""
    soup = BeautifulSoup(target_div_html, "html.parser")
    controls = []
    
    # 仅在目标 div 内查找控件
    for control in soup.find_all(["input", "select", "textarea"]):
        control_info = {
            "type": control.name,
            "id": control.get("id", ""),
            "name": control.get("name", ""),
            "placeholder": control.get("placeholder", ""),
            "aria_label": control.get("aria-label", ""),
            "label_text": "",
            "sibling_texts": [],
            "parent_class": control.find_parent().get("class", [""])[0] if control.find_parent() else "",
            "is_hidden": control.get("type") == "hidden"
        }
        
        # 仅在目标 div 内查找关联的 label（通过 for 或包裹关系）
        label = control.find_parent("label", **TARGET_DIV_SELECTOR) or \
                soup.find("label", attrs={"for": control.get("id")}, **TARGET_DIV_SELECTOR)
        if label:
            control_info["label_text"] = re.sub(r"\s+", " ", label.get_text(strip=True))
        
        # 收集同层级文本节点（限于目标 div 内）
        for sibling in control.find_previous_siblings() + control.find_next_siblings():
            if sibling.parent == control.parent and sibling.name in ["span", "div", "p"]:
                control_info["sibling_texts"].append(re.sub(r"\s+", " ", sibling.get_text(strip=True)))
        
        if not control_info["is_hidden"] and (control_info["id"] or control_info["name"]):
            controls.append(control_info)
    
    return controls

# ====================== 大模型相关函数（无变化） ======================
def build_llm_prompt(control_info: Dict) -> str:
    """构建包含前端规则的 LLM Prompt"""
    prompt = f"""任务：根据以下 HTML 控件的上下文信息，确定用户提示信息（中文自然语言，简洁明确）。
前端规则：
1. 优先使用 `label_text`（若存在且与控件 id/name 关联）。
2. 若无 label，使用 `placeholder` 或 `aria_label`（去除末尾的“：”“*”等符号）。
3. 若仍无，分析 `parent_class` 或 `name`（如 name 包含“tel”映射“电话”，class 包含“email”映射“邮箱”）。
4. 结果仅返回提示信息，无需额外说明。

控件信息：
- 类型: {control_info['type']}
- id: {control_info['id']}
- name: {control_info['name']}
- label_text: {control_info['label_text'] if control_info['label_text'] else "无"}
- placeholder: {control_info['placeholder'] if control_info['placeholder'] else "无"}
- aria_label: {control_info['aria_label'] if control_info['aria_label'] else "无"}
- parent_class: {control_info['parent_class']}
- sibling_texts: {control_info['sibling_texts'] if control_info['sibling_texts'] else "无"}

示例：
输入：{{label_text: "代理商编号", placeholder: "无", name: "agent_num"}} → 输出：代理商编号
输入：{{label_text: "无", placeholder: "请输入联系电话", name: "tel"}} → 输出：联系电话
"""
    return prompt

def mock_llm_inference(prompt: str) -> str:
    """模拟大模型推理（实际需替换为真实 API 调用）"""
    mock_responses = {
        "代理商编号": "代理商编号",
        "请输入您的邮箱": "邮箱地址",
        "无|请输入手机号|user-tel": "联系电话"
    }
    return mock_responses.get(prompt, "待确认")

# ====================== 主流程函数（新增目标 div 处理） ======================
def main():
    # 1. 读取本地 HTML 并提取目标 div 内容
    
    print("AAAAA")
    with open(LOCAL_HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    target_div_html = parse_target_div_html(html_content)
    if not target_div_html:
        print("警告：未找到目标 div，程序终止")
        return
    
    # 2. 解析目标 div 内的控件信息
    print("BBBBB")
    controls = parse_control_info_in_div(target_div_html)
    
    # 3. 生成提示信息（后续步骤无变化）
    print(f"CCCCC{len(controls)}")
    result = []
    for control in controls:
        prompt = build_llm_prompt(control)
        hint_text = mock_llm_inference(prompt)
        result.append({
            "控件标识": control["id"] or control["name"],
            "提示信息": hint_text,
            "控件类型": control["type"],
        })
    
    # 4. 输出结果
    print("=== 指定 div 内的提示信息-控件对应关系 ===")
    for item in result:
        print(f"{item['提示信息']} 对应的输入控件是：{item['控件标识']}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"发生错误: {e}")