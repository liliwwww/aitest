from bs4 import BeautifulSoup
import re
import json
from typing import List, Dict
import requests

# ====================== 配置参数 ======================
LOCAL_HTML_PATH = r"C:\Users\wdp\project\aitest\screenshots\page_20250427_174503.html"  # 本地 HTML 文件路径

TARGET_DIV_SELECTOR = {  # 指定目标 div 的属性
    "id": "bjui-navtab",
    "class_": "tabsPage"
}
LLM_API_KEY = "sk-811ba66952094c55b56b51ff87a3013b"  # 需替换为实际 API 密钥
LLM_ENDPOINT = "https://api.deepseek.com/chat/completions"  # Deepseek 端点（示例）


def build_batch_llm_prompt(controls: List[Dict]) -> str:
    """构建批量处理的LLM Prompt（要求返回JSON数组）"""
    prompt = f"""任务：根据以下多个HTML控件的上下文信息，批量确定用户提示信息（中文自然语言，简洁明确）。
前端规则：
1. 优先使用 `label_text`（若存在且与控件 id/name 关联）。
2. 若无label，使用 `placeholder` 或 `aria_label`（去除末尾的“：”“*”等符号）。
3. 若仍无，分析 `parent_class` 或 `name`（如 name 包含“tel”映射“电话”，class 包含“email”映射“邮箱”）。
4. 返回格式：JSON数组，每个对象包含"控件标识","控件类型","提示信息"。控件类型比如：text 输入框，datepicker 输入框，select 下拉框等。

控件列表（共{len(controls)}个）：
{json.dumps(controls, ensure_ascii=False, indent=2)}

示例输出：
[{{"控件标识": "agent_num", "控件类型": "text 输入框", "提示信息": "代理商编号"}}, {{"控件标识": "agent_name", "控件类型": "text 输入框", "提示信息": "代理商名称"}}]
"""
    return prompt

def remove_json_markers(text):
    # 去除开头的 ```json
    if text.startswith("```json"):
        text = text[len("```json"):]
    # 去除结尾的 ```
    if text.endswith("```"):
        text = text[:-len("```")]
    # 去除前后多余的空白字符
    return text.strip()


# 示例使用
'''
input_text = """```json
[
  {"控件标识": "agent_num", "提示信息": "代理商编号"},
  {"控件标识": "agent_name", "提示信息": "代理商名称"},
  {"控件标识": "_identity_num", "提示信息": "法人身份证号码"},
  {"控件标识": "sign_sale.sm_name", "提示信息": "销售经理"},
  {"控件标识": "maintain.sm_name", "提示信息": "运营经理"},
  {"控件标识": "admin_name", "提示信息": "登录账号"},
  {"控件标识": "department", "提示信息": "部门"},
  {"控件标识": "argeaarea", "提示信息": "大区"},
  {"控件标识": "branchoffice", "提示信息": "分公司"},
  {"控件标识": "agent_status", "提示信息": "审核状态"},
  {"控件标识": "agent_nature", "提示信息": "代理商性质"},
  {"控件标识": "startlocaldate", "提示信息": "开始日期"},
  {"控件标识": "endlocaldate", "提示信息": "结束日期"},
  {"控件标识": "begin_valid", "提示信息": "有效期开始"},
  {"控件标识": "end_valid", "提示信息": "有效期结束"},
  {"控件标识": "numPerPage", "提示信息": "每页显示数量"}
]
```"""
'''

def remove_json_markers(text):
    # 去除开头的 ```json
    if text.startswith("```json"):
        text = text[len("```json"):]
    # 去除结尾的 ```
    if text.endswith("```"):
        text = text[:-len("```")]
    # 去除前后多余的空白字符
    return text.strip()



def deepseek_batch_inference(prompt: str) -> List[Dict]:
    """真实Deepseek API调用（支持批量处理）"""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer sk-811ba66952094c55b56b51ff87a3013b'
    }
    
    data = {
        "model": "deepseek-chat",  # 替换为实际支持的模型
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096
    }


    #$$$$$$$$$$$$$$$
    
    try:
        print(">>>>GO1")
        response = requests.request("POST", LLM_ENDPOINT,headers=headers, json=data  )
        print(">>>>GO2")
        response.raise_for_status()
        print(">>>>GO3")
        llm_output = response.json()["choices"][0]["message"]["content"]
        
        # 解析LLM返回的JSON（需处理可能的格式问题）
        llm_output = remove_json_markers(llm_output )
        print(f">>>>GO4 {llm_output}")
        return json.loads(llm_output)
    
    except Exception as e:
        print(f"LLM调用失败：{str(e)}")
        return []


# ====================== 前端解析函数（新增指定 div 范围） ======================
def parse_target_div_html(html_content: str) -> str:
    """提取目标 div 内的 HTML 内容"""
    soup = BeautifulSoup(html_content, "html.parser")
    target_div = soup.find("div", **TARGET_DIV_SELECTOR)

    #print("$$$$\n\n\n\n$$$$")
    #print(str(target_div))
    #print("$$$$\n\n\n\n$$$$")
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

    # 3. 构建批量Prompt并调用LLM
    if not controls:
        print("警告：未找到有效控件")
        return
    
    # 3. 生成提示信息（后续步骤无变化）
    print(f"CCCCC{len(controls)}")
    
    
    # 提取LLM所需的精简控件信息（避免冗余字段影响Prompt长度）
    llm_controls = [{
        "id": c["id"],
        "name": c["name"],
        "label_text": c["label_text"],
        "placeholder": c["placeholder"],
        "aria_label": c["aria_label"],
        "parent_class": c["parent_class"],
        "sibling_texts": c["sibling_texts"]
    } for c in controls]
    
    batch_prompt = build_batch_llm_prompt(llm_controls)
    llm_results = deepseek_batch_inference(batch_prompt)
    
    # 4. 匹配LLM结果与原始控件（处理可能的顺序差异）
    result = []
    for control, llm_result in zip(controls, llm_results):
        result.append({
            "控件标识": llm_result.get("控件标识", control["id"] or control["name"]),
            "提示信息": llm_result.get("提示信息", "待确认"),
            "控件类型": control["type"]
        })
    
    # 4. 输出结果
    print("=== 指定 div 内的提示信息-控件对应关系 ===")
    for item in result:
        print(f"{item['提示信息']} 对应的输入控件是：{item['控件标识']}, {item['控件类型']}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"发生错误: {e}")