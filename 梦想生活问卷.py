import streamlit as st
import requests
import os
import time

#设置背景颜色

# 设置页面标题
st.set_page_config(page_title="梦想生活规划", layout="wide")
st.title("📝 问卷")

# 加载 .env 文件中的环境变量
from dotenv import load_dotenv  # 推荐方式
load_dotenv()

# 配置API（实际部署时应使用环境变量）
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")
deepseek_chat = os.getenv("DEEPSEEK_CHAT")
# 问题列表
questions = [
    {"key": "q1", "text": "Q1：您现在户籍在哪个城市，常住在哪个城市？", "required": True},
    {"key": "q2", "text": "Q2：父母所从事的工作是什么，能为你提供什么？", "required": True},
    {"key": "q3", "text": "Q3：如果用一个颜色形容您理想的生活状态，您会选择什么？为什么？", "required": True},
    {"key": "q4", "text": "Q4：您上次产生'要是能永远停在这一刻多好'的瞬间是？这个场景藏着哪些关键元素？", "required": True},
    {"key": "q5", "text": "Q5：想象有个平行时空的您：他现在生活在哪里(城市/国家)，每天在做什么", "required": True},
    {"key": "q6", "text": "Q6：您希望未来窗外的主旋律是蝉叫鸟鸣、市井喧闹、键盘敲击声、海浪拍打、完全宁静？", "required": True},
    {"key": "q7", "text": "Q7：现在立刻能做的哪个微小改变，会让三个月后的您感谢自己？", "required": True},
    {"key": "q8", "text": "Q8：如果必须牺牲某项现有优势才能换取理想生活，您的底线红线是什么？", "required": True},
    {"key": "q9", "text": "Q9：还有什么问题需要补充的吗？", "required": False}
]

# 初始化session_state保存报告
if "report_content" not in st.session_state:
    st.session_state.report_content = None

# 表单部分
with st.form("survey_form"):
    st.markdown("### 请回答以下问题")

    # 动态生成输入框
    answers = {}
    for question in questions:
        answers[question["key"]] = st.text_area(
            label=question["text"],
            key=f"input_{question['key']}",
            height=100 if question["key"] == "q6" else 80,
            help="必填" if question["required"] else "选填"
        )

    # 提交按钮
    submitted = st.form_submit_button(
        "🚀 生成梦想生活分析报告",
        type="primary",
        use_container_width=True
    )

    # 提交处理
    if submitted:
        missing = [q["text"] for q in questions if q["required"] and not answers[q["key"]].strip()]
        if missing:
            st.error(f"⚠️ 请填写以下必填问题：\n- " + "\n- ".join(missing))
        else:
            with st.spinner("🔍 正在分析您的梦想生活，请稍候..."):
                try:
                    # 构造提示词
                    prompt = f"""请根据以下问卷生成详细梦想生活分析报告：

**居住信息**：{answers['q1']}
**家庭认知**：{answers['q2']}
**代表颜色**：{answers['q3']}
**美好一刻**：{answers['q4']}
**想象生活**：{answers['q5']}
**未来旋律**：{answers['q6']}
**微笑改变**：{answers['q7']}
**牺牲底线**：{answers['q8']}
**补充说明**：{answers['q9'] or "无"}

报告需包含：
1. 用户信息总结
2. 实现概率评估（1-5级）
3. 推荐实现的关键路径（分阶段）
4. 预估需要的钱财
5. 梦想生活计划建议"""

                    # API请求
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": "你是一位梦想生活分析专家，需要生成专业、可执行的分析报告"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.8,
                        "max_tokens": 2000
                    }

                    # 调用API
                    response = requests.post(base_url, headers=headers, json=payload)
                    response.raise_for_status()

                    # 保存报告到session_state
                    st.session_state.report_content = response.json()["choices"][0]["message"]["content"]
                    st.rerun()  # 刷新页面显示报告

                except requests.exceptions.RequestException as e:
                    st.error(f"API请求失败：{str(e)}")
                except Exception as e:
                    st.error(f"生成错误：{str(e)}")

# 报告显示区域（表单外）
if st.session_state.report_content:
    st.success("✅ 梦想生活报告生成完成！")
    st.markdown("---")
    st.subheader("📊 个性化梦想生活分析报告")
    st.markdown(st.session_state.report_content)

    # 下载按钮（在表单外部）
    st.download_button(
        label="💾 下载报告（Markdown格式）",
        data=st.session_state.report_content,
        file_name="AI梦想生活分析报告.md",
        mime="text/markdown",
        key="download_button"
    )

# 侧边栏说明
with st.sidebar:
    st.markdown("### 使用指南")
    st.info("""
    1. 填写所有**必填问题**（带*号）
    2. 点击蓝色生成按钮
    3. 查看生成的报告
    4. 可下载Markdown格式副本
    """)
    st.markdown("---")
    st.caption("ℹ️ 数据仅用于实时分析，不存储任何回答")

from requests.exceptions import HTTPError

def make_api_request(url, headers, payload, max_retries=3):
    retry_delay = 1  # 初始等待 1 秒
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # 检查 4XX/5XX 错误
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 429:  # 速率限制
                st.warning(f"请求过快，等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避（1, 2, 4, 8...秒）
            else:
                raise e
    raise Exception("超过最大重试次数，请稍后再试。")

# 页脚
st.markdown("---")
st.caption("© 2025 AI梦想生活助手 | Powered by DeepSeek API")

#设置背景颜色
gradient_direction = "to right"  # 渐变方向：to right/to left/to top/to bottom
start_color = "#ffffff"           # 起始颜色（纯白）
end_color = "#D3D3D3"             # 终止颜色（浅灰）

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient({gradient_direction}, {start_color}, {end_color});
    }}
    </style>
    """,
    unsafe_allow_html=True
)

#streamlit run 调查问卷.py
