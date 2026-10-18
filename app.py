import streamlit as st
from openai import OpenAI
import time
import re

# 页面基础设置
st.set_page_config(page_title="微光", page_icon="✨", layout="centered")

st.title("✨ 微光 AIGC 叙事与情绪疗愈平台")
st.caption("把你的真实经历，变成一部温暖的小短剧，并记录此刻的心情")

# 创建两个顶部标签页
tab1, tab2 = st.tabs(["🎬 创作微光 (生成短剧)", "🌟 拾取微光 (情绪打卡)"])

# ==========================================
# 标签页 1：创作微光
# ==========================================
with tab1:
    story = st.text_area("写下你的经历", height=150, placeholder="例如：大一挂科后，我一个人在操场走了很久……")
    style = st.selectbox("选择风格", ["治愈", "温柔", "轻幽默"])

    if st.button("生成微短剧", type="primary"):
        if not story.strip():
            st.warning("先写点什么吧～")
        else:
            with st.spinner("正在构思剧本与分镜，请稍候……"):
                try:
                    api_key = st.secrets["API_KEY"]
                    client = OpenAI(
                        api_key=api_key,
                        base_url="https://open.bigmodel.cn/api/paas/v4/"
                    )
                    
                    prompt = f"""你是一位深谙叙事疗法的微短剧编剧。请根据用户的真实经历，创作一部具有治愈力量的微短剧。

【严格限制规则】
1. 必须紧密围绕用户的真实经历，提取其中的【核心冲突】和【具体场景元素】。
2. 全程以第一人称“我”展开叙述，冲突数量不超过1个。
3. 情绪走向必须是“接纳式”的，禁止说教、强行鸡汤。
4. 风格基调：{style}。

【输出格式要求】（请严格按以下格式输出，不要输出多余的废话）
【场景名】（必须是中文）
【旁白】（必须是中文）
【画面描述】（必须为纯英文，由5-8个英文词组组成，例如：A quiet window, cloudy night, rain stopped, warm light, cinematic。严禁使用长句）。

用户真实经历：{story}"""
                    
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[
                            {"role": "system", "content": "你是一个遵循叙事心理学约束的短剧编剧。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    
                    script = response.choices[0].message.content
                    st.success("剧本与分镜已生成：")
                    st.write(script)
                    
                    st.markdown("---")
                    st.subheader("🎬 短剧分镜画面生成")
                    
                    # 【暴力提取法】不管三七二十一，切掉中括号，剩下的全拿走
                    image_prompts = []
                    for line in script.split('\n'):
                        if '【画面描述】' in line:
                            raw_text = line.split('】')[-1]
                            # 清理掉冒号、空格、引号等多余符号
                            clean_text = raw_text.strip(' :：\n"\'')
                            # 只要长度够，且有英文字母，就加进去
                            if len(clean_text) > 3 and any(c.isalpha() for c in clean_text):
                                image_prompts.append(clean_text)
                    
                    if image_prompts:
                        for i, img_prompt in enumerate(image_prompts[:2]): 
                            with st.spinner(f"正在绘制场景 {i+1} 的画面……"):
                                try:
                                    # 使用免费画图模型 cogview-3-flash
                                    img_response = client.images.generate(
                                        model="cogview-3-flash",
                                        prompt=img_prompt
                                    )
                                    image_url = img_response.data[0].url
                                    st.image(image_url, caption=f"场景 {i+1}", use_container_width=True)
                                except Exception as img_e:
                                    st.error(f"画面 {i+1} 生成失败，错误信息: {img_e}")
                    else:
                        st.info("未提取到英文画面描述，请重试一次。")

                    # 存下状态，供下一个标签页使用
                    st.session_state['has_created'] = True
                    st.success("👆 你的短剧已生成！现在请点击上方的 **【🌟 拾取微光】** 标签，记录你的感受。")

                except Exception as e:
                    st.error(f"生成失败，请检查 API Key 或网络。错误信息：{e}")

# ==========================================
# 标签页 2：拾取微光
# ==========================================
with tab2:
    if 'emotion_archive' not in st.session_state:
        st.session_state['emotion_archive'] = []

    if not st.session_state.get('has_created', False):
        with st.chat_message("assistant", avatar="🧚‍♀️"):
            st.write("你好呀，我是微光精灵。")
            st.write("我还没有看到你的专属故事呢。请先去上方的 **【🎬 创作微光】** 标签页写下你的经历并生成短剧。看完之后，再来这里找我聊聊吧。")
    else:
        with st.chat_message("assistant", avatar="🧚‍♀️"):
            st.write("你好呀，我是微光精灵。")
            st.write("刚刚的故事，是你真实的经历变成的。看完它之后，此刻的你，感觉怎么样呢？")
            
        emotion = st.selectbox("请选择你此刻最接近的情绪：", ["请选择", "委屈", "迷茫", "焦虑", "疲惫", "平静了"])
        
        if emotion != "请选择":
            emotion_data = {
                "委屈": "委屈往往是因为你曾真诚地对待某件事。这份真诚没有错，只是暂时没被接住。现在，去给自己倒杯水吧。",
                "迷茫": "迷茫说明你正在认真思考方向。不用急着找到答案，今天先做一件确定的小事就好。",
                "焦虑": "焦虑是大脑在试图保护你。但此刻，你可以告诉它：我看到了，我先休息五分钟。",
                "疲惫": "累了就停一停。你不需要一直发光，微光也是光。",
                "平静了": "真为你高兴，你通过自己的故事，找到了内心的平静。请记住这一刻的感觉。"
            }
            
            with st.chat_message("assistant", avatar="🧚‍♀️"):
                st.write(emotion_data[emotion])
                
            st.markdown("---")
            st.write("### 📁 存入情绪档案")
            
            with st.form("emotion_archive_form", clear_on_submit=True):
                feedback = st.text_input("用一句话记录此刻的想法：", placeholder="比如：好像没那么难过了，明天去吃顿好的。")
                submitted = st.form_submit_button("记录并存入档案", type="primary")
                
                if submitted:
                    if not feedback.strip():
                        st.warning("写点什么再保存吧～哪怕是一个词也可以。")
                    else:
                        new_record = {
                            "time": time.strftime('%Y-%m-%d %H:%M:%S'),
                            "emotion": emotion,
                            "feedback": feedback
                        }
                        st.session_state['emotion_archive'].append(new_record)
                        
                        # 气球特效！
                        st.balloons()
                        st.success("✅ 已成功存入个人档案！")
                        st.toast("档案已加密保存。", icon="💾")

        # 档案调取面板
        st.markdown("---")
        with st.expander("🗂️ 点击查看我的【历史情绪档案】"):
            if len(st.session_state['emotion_archive']) == 0:
                st.info("目前还没有记录哦，打卡后会在这里生成你的心情轨迹。")
            else:
                for record in reversed(st.session_state['emotion_archive']):
                    st.info(f"""
                    **⏱️ 时间**：{record['time']}  
                    **🎭 情绪**：{record['emotion']}  
                    **💬 记录**：{record['feedback']}
                    """)