import streamlit as st
import requests
import os
# 设置页面标题
st.set_page_config(page_title="槟榔调研", layout="wide")
st.title("📝 槟榔调研问卷")

# 加载 .env 文件中的环境变量
from dotenv import load_dotenv  # 推荐方式
load_dotenv()

# 配置API（实际部署时应使用环境变量）
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")
deepseek_chat = os.getenv("DEEPSEEK_CHAT")
# 问题列表
questions = [
    {"key": "q1", "text": "Q1：您现在户籍在哪个城市，父母所从事的工作是什么？", "required": True},
    {"key": "q2", "text": "Q2：对槟榔有多少的认知，了解多少食用方法？", "required": True},
    {"key": "q3", "text": "Q3：对槟榔的最核心需求是什么？", "required": True},
    {"key": "q4", "text": "Q4：是否有戒断反应，有没有长时间吃槟榔？", "required": True},
    {"key": "q5", "text": "Q5：每月花多少钱💴来吃槟榔？", "required": True},
    {"key": "q6", "text": "Q6：是否有其他问题想要补充？", "required": False}
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
        "🚀 生成分析报告",
        type="primary",
        use_container_width=True
    )

    # 提交处理
    if submitted:
        missing = [q["text"] for q in questions if q["required"] and not answers[q["key"]].strip()]
        if missing:
            st.error(f"⚠️ 请填写以下必填问题：\n- " + "\n- ".join(missing))
        else:
            with st.spinner("🔍 正在分析您的回答，请稍候..."):
                try:
                    # 构造提示词
                    prompt = f"""请根据以下问卷生成详细吃槟榔分析报告：

**基础信息**：{answers['q1']}
**信息认知**：{answers['q2']}
**成瘾程度**：{answers['q3']}
**戒断反应**：{answers['q4']}
**钱财投入**：{answers['q5']}
**补充说明**：{answers['q6'] or "无"}

报告需包含：
1. 用户常识总结
2. 戒断反应评估（1-5级）
3. 推荐戒断路径（分阶段）
4. 分配关键钱财
5. 每月吃槟榔计划建议"""

                    # API请求
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": "你是一位槟榔分析专家，需要生成专业、可执行的分析报告"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
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
    st.success("✅ 报告生成完成！")
    st.markdown("---")
    st.subheader("📊 个性化槟榔分析报告")
    st.markdown(st.session_state.report_content)

    # 下载按钮（在表单外部）
    st.download_button(
        label="💾 下载报告（Markdown格式）",
        data=st.session_state.report_content,
        file_name="AI槟榔分析报告.md",
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

# 页脚
st.markdown("---")
st.caption("© 2025 AI槟榔助手 | Powered by DeepSeek API")
#streamlit run 调查问卷.py
