import streamlit as st
import requests

# ========== 页面基础配置 ==========
st.set_page_config(page_title="简历STAR优化助手", layout="centered")
st.title("📝 大学生简历经历智能优化工具")
st.caption("基于HR专业STAR法则，一键优化实习/社团/项目经历")

# 安全读取secrets：本地无文件不报错，线上自动读取后台配置
try:
    secret_api_key = st.secrets.get("doubao_api_key", "")
    secret_api_url = st.secrets.get("api_url", "https://ark.cn-beijing.volces.com/api/v3")
    secret_model_id = st.secrets.get("model_id", "doubao-lite-4k")
except Exception:
    # 本地没有secrets.toml时，全部使用默认值
    secret_api_key = ""
    secret_api_url = "https://ark.cn-beijing.volces.com/api/v3"
    secret_model_id = "doubao-lite-4k"


with st.sidebar:
    st.subheader("API配置（可选）")
    api_key = st.text_input("豆包API密钥", value=secret_api_key, type="password")
    api_url = st.text_input("接口地址", value=secret_api_url)
    model_id = st.text_input("模型ID", value=secret_model_id)
    st.info("不填密钥将展示示例效果，可直接用于演示")

# ========== HR专业优化规则 ==========
prompt_template = """
你是有5年校招经验的资深HR，严格按STAR法则改写以下大学生简历经历：
1. 分【情境S】【任务T】【行动A】【结果R】四块呈现
2. 补充符合大学生真实水平的量化数据，不虚构夸大
3. 语言精简正式，单段经历控制在150字内
4. 结尾标注2-3个核心能力标签
待优化原文：
{user_text}
"""


# ========== 核心生成函数 ==========
def generate_result(user_text):
    # 没填密钥时返回示例结果，保证能正常演示
    if not api_key:
        return """
【情境S】负责学院秋季招聘会的企业对接与现场统筹
【任务T】保障12家企业顺利宣讲，提升参会学生体验
【行动A】提前对接确认场地需求，制作参会指引，安排30名志愿者分工值守
【结果R】到场人数超200人，企业满意度92%，零现场流程事故
✅ 核心能力：活动协调、沟通对接、执行落地
        """
    # 填写密钥后真实调用AI
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "你是专业的校招简历辅导HR。"},
            {"role": "user", "content": prompt_template.format(user_text=user_text)}
        ],
        "temperature": 0.3
    }
    try:
        resp = requests.post(f"{api_url}/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"调用出错，请检查API配置：{str(e)}"


# ========== 主界面 ==========
st.markdown("### 请输入简历经历原文")
user_input = st.text_area(
    "粘贴一段实习/社团/项目经历",
    height=120,
    placeholder="例如：负责学院招聘会工作，联系企业，安排现场，最后顺利办完了"
)

optimize_btn = st.button("✨ 一键STAR优化", type="primary", use_container_width=True)

if optimize_btn:
    if not user_input.strip():
        st.warning("请先输入要优化的内容")
    else:
        with st.spinner("优化中..."):
            result = generate_result(user_input)
        st.markdown("---")
        st.subheader("优化前后对比")
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("**原文**")
            st.write(user_input)
        with col_right:
            st.markdown("**STAR优化版**")
            st.write(result)
