import streamlit as st
from openai import OpenAI
import time
import re

st.set_page_config(page_title="微光", page_icon="✨", layout="centered")

st.title("✨ 微光 AIGC 叙事与情绪疗愈平台")
st.caption("把你的真实经历，变成一部温暖的小短剧，并记录此刻的心情")

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
                    
                    # 升级版 Prompt：包含扩写机制与积极心理暗示
                    prompt = f"""你是一位深谙叙事疗法与积极心理学的微短剧编剧。请根据用户的真实经历，创作一部具有治愈力量的微短剧。

【核心任务与字数要求】
1. 创作一部时长约 20-30 秒的微短剧（字数约 200-300 字）。
2. 如果用户的输入字数极少（例如只有“我好累”、“挂科了”几个字），你必须展开合理的想象，补充环境细节（如光线、声音、天气）和内心独白，以丰富剧情，绝不能只写一两句话。

【积极心理学干预指令（极度重要）】
1. 用户的输入可能全篇都是负面情绪或抱怨。在剧本的后半段，你必须硬性加入“积极心理暗示”。
2. 加入一个具体的【微小行动】（比如：深呼吸三次、整理一下桌面、洗个热水澡、推开窗户看云）。
3. 加入一个【积极的心理暗示】（比如：允许自己今天做个废物、这不是我的错、慢慢来比较快）。
4. 全程以第一人称“我”展开，情绪走向是从“陷入困境”到“通过微小行动获得掌控感与平静”。
5. 风格基调：{style}。

【输出格式要求】（请严格按以下格式输出）
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
                    
                    image_prompts = []
                    for line in script.split('\n'):
                        if '【画面描述】' in line:
                            match = re.search(r'【画面描述】[：:\s]*(.*)', line)
                            if match:
                                clean_text = match.group(1).strip()
                                if len(clean_text) > 5: 
                                    image_prompts.append(clean_text)
                    
                    if image_prompts:
                        for i, img_prompt in enumerate(image_prompts[:2]): 
                            with st.spinner(f"正在绘制场景 {i+1} 的画面……"):
                                try:
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

                    st.session_state['has_created'] = True
                    st.success("👆 你的短剧已生成！现在请点击上方的 **【🌟 拾取微光】** 标签，记录你的感受。")

                except Exception as e:
                    st.error(f"生成失败，请检查 API Key 或网络。错误信息：{e}")


# ==========================================
# 标签页 2：拾取微光（树状图穷举逻辑）
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
            st.write("刚刚的故事看完了，此刻的你，最接近下面哪种状态呢？")

        # 核心：大学生专属“情绪-场景-话术”树状穷举库
        campus_rules = {
            "😭 委屈": {
                "被室友/同学孤立或误解": "被误解的时候，人本能地想大喊大叫。但委屈往往是因为你曾真诚地对待过这段关系。别急着证明自己，今天先去图书馆或者咖啡馆，给自己买杯好喝的，换个环境透透气。",
                "小组作业被划水/抢功劳": "一个人扛下了所有，最后却要共享分数，换谁都会觉得不公平。但请记住，你锻炼出的能力是别人抢不走的。今晚合上电脑，去操场走一圈，把怒气吹散，不要让别人的懒惰惩罚你的身体。"
            },
            "🌫️ 迷茫": {
                "面临考研/考公/就业的岔路口": "看着身边的人好像都有了去处，自己却连往哪走都不知道。其实，二十岁出头本就是允许迷茫的。你不需要今天就定下终生。哪怕只是花十分钟，列一下你‘绝不想要’的工作，也是一种方向。",
                "对所学专业提不起兴趣": "强逼自己去热爱一件不喜欢的事，是很消耗能量的。不用急着转专业，试着给自己留一块自留地——去旁听一门喜欢的课，或者学一个技能。让本专业成为你的‘饭碗’，而不是你的‘全部’。"
            },
            "😰 焦虑": {
                "期末/DDL逼近，感觉学不完": "大脑在疯狂报警，是因为你想把所有事情一口气做完。现在，深呼吸，闭上眼睛。把任务拆碎，不要看整本书，先看第一页的标题。如果实在学不进，定个15分钟的闹钟去睡一觉，清醒了再战。",
                "同辈压力（身边人太优秀）": "社交软件上的同龄人总是光鲜亮丽，但这只是冰山一角。每个人的时区不同，有人20岁发光，有人30岁才找到路。专注你今天的微小进步，不要让别人的进度条打乱你的节奏。"
            },
            "🔋 疲惫": {
                "社团/学生会工作太多，连轴转": "你不需要对所有人负责，更不需要做一个完美的‘老好人’。允许自己把手机静音半天，或者以身体不舒服为由推掉一次不重要的会议。你的健康和精力，永远排在第一位。",
                "努力了但成绩依然没起色": "长期的熬夜和不理想的分数，让你像一块耗尽的电池。累了就停下来。接纳‘我确实在这方面不擅长’也是一种勇气。去洗个热水澡，睡个自然醒的觉，允许自己今天什么都不做。"
            },
            "🌱 平静": {
                "刚才的故事让我感觉好多了": "真为你高兴，你通过自己的故事，找到了内心的力量。把这种感觉记在心里，以后再遇到难过的事，记得回来看一看。微光永远在这里。"
            }
        }

        main_emotion = st.selectbox("第一步：选择你当前的情绪大类", list(campus_rules.keys()))

        if main_emotion:
            sub_scenes = list(campus_rules[main_emotion].keys())
            sub_scene = st.selectbox("第二步：具体是因为以下哪种情况？", sub_scenes)

            if sub_scene:
                comfort_text = campus_rules[main_emotion][sub_scene]
                
                with st.chat_message("assistant", avatar="🧚‍♀️"):
                    st.write(comfort_text)
                    
                st.markdown("---")
                st.write("### 📁 存入情绪档案")
                
                with st.form("emotion_archive_form", clear_on_submit=True):
                    feedback = st.text_input("用一句话记录此刻的想法：", placeholder="比如：确实，不管别人了，我先去吃点好的。")
                    submitted = st.form_submit_button("记录并存入档案", type="primary")
                    
                    if submitted:
                        if not feedback.strip():
                            st.warning("写点什么再保存吧～哪怕是一个词也可以。")
                        else:
                            new_record = {
                                "time": time.strftime('%Y-%m-%d %H:%M:%S'),
                                "emotion": f"{main_emotion} - {sub_scene}",
                                "feedback": feedback
                            }
                            st.session_state['emotion_archive'].append(new_record)
                            
                            st.balloons()
                            st.success("✅ 已成功存入个人档案！")
                            st.toast("档案已加密保存。", icon="💾")

        st.markdown("---")
        with st.expander("🗂️ 点击查看我的【历史情绪档案】"):
            if len(st.session_state['emotion_archive']) == 0:
                st.info("目前还没有记录哦，打卡后会在这里生成你的心情轨迹。")
            else:
                for record in reversed(st.session_state['emotion_archive']):
                    st.info(f"""
                    **⏱️ 时间**：{record['time']}  
                    **🎭 情绪场景**：{record['emotion']}  
                    **💬 记录**：{record['feedback']}
                    """)
