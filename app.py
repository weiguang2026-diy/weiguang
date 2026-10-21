import streamlit as st
from openai import OpenAI
import time
import re
import random
import base64

# ==========================================
# 1. 页面基础配置与终极视觉 CSS
# ==========================================
st.set_page_config(page_title="微光 · 人生放映厅", page_icon="✨", layout="centered")

st.markdown("""
<style>
    /* ==================== 全局红棕星空背景 ==================== */
    .stApp {
        background-color: #1A0F0E !important;
        background-image: 
            radial-gradient(1.5px 1.5px at 20px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 40px 70px, #FFD700, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 50px 160px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 90px 40px, #FFD700, rgba(0,0,0,0)),
            linear-gradient(135deg, #2D1B18 0%, #4A2C2A 40%, #1A0F0E 100%) !important;
        background-repeat: repeat;
        background-size: 200px 200px, 200px 200px, 200px 200px, 200px 200px, 100% 100% !important;
    }
    
    /* ==================== 全局文字与基础排版 ==================== */
    * { color: #F5E6D3 !important; font-family: 'Noto Serif SC', 'STSong', serif !important; }
    header {visibility: hidden;} footer {visibility: hidden;}
    
    /* ==================== 所有按钮样式 ==================== */
    .stButton>button {
        background-color: rgba(26, 15, 14, 0.6) !important;
        color: #FFD700 !important; border: 1px solid #FFD700 !important;
        border-radius: 20px !important; transition: all 0.3s ease !important;
    }
    .stButton>button:hover { 
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5) !important; 
        color: #fff !important; 
        background-color: rgba(255, 215, 0, 0.1) !important;
    }
    
    /* ==================== 输入框与文本框 ==================== */
    div[data-testid="stTextArea"] div[data-baseweb="textarea"],
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: transparent !important; 
        border: 1px solid rgba(255, 215, 0, 0.4) !important; 
        border-radius: 12px !important;
    }
    
    /* ==================== 聊天气泡 ==================== */
    div[data-testid="stChatMessage"] {
        background-color: rgba(26, 15, 14, 0.6) !important; 
        border-radius: 15px !important; 
        border: 1px solid rgba(255, 215, 0, 0.15) !important;
    }
    
    /* ==================== 完美居中的上传组件 ==================== */
    div[data-testid="stFileUploader"] {
        background-color: rgba(26, 15, 14, 0.6) !important;
        border: 1px dashed #FFD700 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        text-align: center !important;
    }
    div[data-testid="stFileUploader"] section > div { display: none !important; }
    div[data-testid="stFileUploader"] small { display: none !important; }
    div[data-testid="stFileUploader"] label { display: none !important; }
    
    div[data-testid="stFileUploader"] button {
        width: 100% !important; height: 100% !important;
        background-color: transparent !important; 
        border: none !important;
        font-size: 0 !important;
        color: transparent !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    div[data-testid="stFileUploader"] button * { display: none !important; }
    div[data-testid="stFileUploader"] button::after {
        content: "📷 点击或拖拽上传环境照" !important;
        color: #FFD700 !important; 
        font-size: 16px !important;
        font-family: 'Noto Serif SC', serif !important;
        font-weight: bold !important;
        white-space: nowrap !important;
        position: absolute !important;
        top: 50% !important; left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>✨ 微光 · 人生放映厅 🧚‍♀️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A88B7D;'>“一切经历，无论好坏，都塑造了我。”</p>", unsafe_allow_html=True)

# ==========================================
# 2. 核心资产与初始化
# ==========================================
if 'archives' not in st.session_state: 
    st.session_state['archives'] = []

if 'bottles' not in st.session_state:
    st.session_state['bottles'] = [
        "“允许自己暂时暗淡，是积蓄下一次微光的力量。” —— 来自 匿名的旅人",
        "“那些让你内耗的巨石，终究会被时间碾成铺路的沙砾。” —— 来自 毕业三年的学姐",
        "“黑夜不是用来害怕的，是用来孵育星星的。祝你今晚有个好梦。” —— 来自 守夜人"
    ]

# 🚨 彻底清空预置的假切片，保证档案库干净
if 'my_archive' not in st.session_state:
    st.session_state['my_archive'] = []

MOCK_COMMUNITY = {
    "考试": [
        {"story": "昨天高数挂科了，感觉天都塌了，不敢告诉爸妈。", "action": "去操场淋着雨跑了三圈，吃了一根烤肠。其实也没什么大不了的。"},
        {"story": "考研失败，差两分进复试，感觉人生毁了。", "action": "大哭一场，开始疯狂投简历，现在已经拿到offer啦。"}
    ],
    "工作": [
        {"story": "面试被HR当场羞辱学历，觉得一无是处。", "action": "买了一杯最贵的奶茶，告诉自己我不缺他这一份工作。"}
    ],
    "感情": [
        {"story": "分手了，感觉再也遇不到喜欢的人了。", "action": "把前任的东西全扔了，给自己做了一顿大餐。"}
    ]
}

ACTION_CORPUS = {
    "烦心事": [
        "去洗个热水澡，想象水流带走今天的疲惫与不甘",
        "闭上眼睛深呼吸三次，把手放在胸口，告诉自己“我辛苦了”",
        "去操场漫无目的地走一圈，让夜风吹散情绪的余温",
        "把心烦的事写在纸上，折成纸飞机飞出去，或者直接撕碎"
    ],
    "平淡": [
        "整理一下杂乱的书桌，给生活建立一点微小的秩序感",
        "下楼走走，抬头看看今晚的月亮，或者路边沉默的树",
        "戴上耳机听一首纯音乐，什么都不做，只发五分钟呆",
        "洗一个苹果吃，认真感受咬下去那一刻的清脆与甘甜"
    ],
    "小确幸": [
        "【记录】拍下此刻的美好，发个朋友圈，把快乐传递给世界",
        "【记录】在备忘录里写下今天最让你开心的3个瞬间，封存起来",
        "【记录】给未来的自己写一句：“今天我很开心，希望你也是”",
        "【记录】把这份快乐分享给身边的人，比如给室友带一杯奶茶"
    ]
}

api_key = st.secrets["API_KEY"]
client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")

tab1, tab2, tab3 = st.tabs(["🎬 人生放映厅", "🌟 微光手记", "📁 我的档案库"])

# ==========================================
# 3. Tab 1: 人生放映厅
# ==========================================
with tab1:
    st.write("### 今天，生活给你加了什么戏？")
    
    st.write("👇 **不知道怎么下笔？点击寻找灵感：**")
    col1, col2, col3 = st.columns(3)
    if col1.button("🌪️ 今天很内耗"): st.toast("💡 灵感参考：写写今天让你心烦、内耗的小事。", icon="🌪️")
    if col2.button("🍃 今天很平淡"): st.toast("💡 灵感参考：写写发呆的瞬间，或无聊时的感觉。", icon="🍃")
    if col3.button("✨ 今天有小确幸"): st.toast("💡 灵感参考：写写吃到的美食、看到的美景。", icon="✨")

    story = st.text_area("输入经历", height=100, placeholder="在这里写下你的真实经历……", label_visibility="collapsed")
    
    st.write("**🎬 建立主角档案（必须锚定当下）：**")
    col_gender, col_env, col_item = st.columns(3)
    
    gender = col_gender.selectbox("主角设定", ["女生", "男生"])
    if gender == "男生":
        char_desc = "Asian young man, short black hair"
    else:
        char_desc = "Asian young woman, long black hair"
        
    env_input = col_env.selectbox("📍 身处哪里？", ["宿舍书桌前", "空荡的教室", "下班/下课的地铁上", "图书馆的角落", "自定义输入..."])
    if env_input == "自定义输入...": env_input = col_env.text_input("输入环境：", value="安静的角落")
        
    item_input = col_item.selectbox("☕ 手边放着什么？", ["手机", "一杯冷掉的咖啡/茶", "揉皱的草稿纸", "自定义输入..."])
    if item_input == "自定义输入...": item_input = col_item.text_input("输入物品：", value="手边小物")

    uploaded_img = st.file_uploader("上传环境照", type=["jpg", "png"], label_visibility="collapsed")

    st.write("**选择电影底色：**")
    col_b1, col_b2, col_b3 = st.columns(3)
    if 'vibe' not in st.session_state: st.session_state['vibe'] = "🌪️ 烦心事"
    if col_b1.button("🌪️ 烦心事", use_container_width=True): st.session_state['vibe'] = "🌪️ 烦心事"
    if col_b2.button("🍃 平淡", use_container_width=True): st.session_state['vibe'] = "🍃 平淡"
    if col_b3.button("✨ 小确幸/高光", use_container_width=True): st.session_state['vibe'] = "✨ 小确幸/高光"
    st.info(f"当前已选择：**{st.session_state['vibe']}**")

    if st.button("🎬 Action！开拍我的电影", type="primary"):
        if not story.strip(): st.warning("请先写下你的经历哦～")
        else:
            final_env = env_input
            if uploaded_img is not None:
                with st.spinner("👁️ 正在读取环境照片..."):
                    try:
                        base64_img = base64.b64encode(uploaded_img.getvalue()).decode('utf-8')
                        vis_res = client.chat.completions.create(
                            model="glm-4v-flash",
                            messages=[{"role": "user", "content": [
                                {"type": "text", "text": "请用极简的词语（5个字以内）提取这张图片里的核心地点（如：办公桌、宿舍）。不要说多余的话。"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                            ]}]
                        )
                        final_env = vis_res.choices[0].message.content.strip()
                    except Exception: pass
            
            vibe = st.session_state['vibe']
            with st.spinner("🪄 正在构建你的绝密档案与剧本..."):
                try:
                    # 🚨 强力修复 Prompt：严禁复述指令，必须写具体的小说细节！
                    prompt = f"""你是一个专业的微电影编剧。请严格按照以下格式输出，不要输出任何多余的解释，直接开始写。

电影名：XXX（请给出2-4个字的极简标题）
代号：XXX
必杀技：XXX
隐藏特质：XXX
命运批注：XXX

场景1：
【旁白】（请以第一人称“我”写一段具体的叙事，必须包含具体的动作、环境描写和心里话。**严禁照抄大纲，必须写具体的故事细节！**例如：“我坐在书桌前，看着那张59分的试卷……”）。字数必须大于150字。
【画面描述】纯英文，5-8个词组。

场景2：
【旁白】（请以第一人称“我”写一段具体的叙事，描写你当时独自消化情绪的挣扎。**严禁写大纲总结！**必须有具体的画面和动作）。字数必须大于150字。
【画面描述】纯英文，5-8个词组。

场景3：
【旁白】（请以第一人称“我”写一段具体的叙事，描写回到【{final_env}】后，看着【{item_input}】，你具体做了一个什么微小动作（如喝了口水），从而完成释怀。**严禁写大纲总结！**）。字数必须大于150字。
【画面描述】纯英文，5-8个词组。

用户经历：{story}"""
                    
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[{"role": "system", "content": "顶级微电影编剧"}, {"role": "user", "content": prompt}]
                    )
                    script = response.choices[0].message.content
                    
                    code_name = re.search(r'代号[：:\s]*(.*)', script).group(1).strip() if re.search(r'代号[：:\s]*', script) else "微光行者"
                    skill = re.search(r'必杀技[：:\s]*(.*)', script).group(1).strip() if re.search(r'必杀技[：:\s]*', script) else "重构现实"
                    trait = re.search(r'隐藏特质[：:\s]*(.*)', script).group(1).strip() if re.search(r'隐藏特质[：:\s]*', script) else "极具韧性"
                    fate = re.search(r'命运批注[：:\s]*(.*)', script).group(1).strip() if re.search(r'命运批注[：:\s]*', script) else "一切经历，都塑造了我。"
                    
                    title_match = re.search(r'电影名[：:\s]*(.*)', script)
                    if title_match:
                        raw_title = re.sub(r'[，。！？、《》\s]', '', title_match.group(1).strip())
                        movie_title = raw_title[:4] # 强行截断，最多4个字
                        if len(movie_title) < 2: movie_title = "微光"
                    else:
                        movie_title = "微光"

                    st.markdown(f"""
                    <div style="background-color: rgba(26, 15, 14, 0.8); border-radius: 8px; padding: 30px; font-family: 'STSong', serif; box-shadow: 0 10px 25px rgba(0,0,0,0.8); border: 1px solid #FFD700; position: relative; margin-bottom: 30px; backdrop-filter: blur(10px);">
                        <div style="text-align: center; border-bottom: 1px dashed #6B4C3A; padding-bottom: 15px; margin-bottom: 20px;">
                            <h1 style="color: #FFD700; margin: 0; font-size: 32px; letter-spacing: 4px; text-shadow: 0 0 10px rgba(255,215,0,0.3);">绝密人物档案</h1>
                        </div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 16px;">
                            <tr><td style="width: 25%; padding: 10px 0; font-weight: bold; color: #A88B7D;">【行动代号】</td><td style="padding: 10px 0; font-size: 20px; font-weight: bold; color: #FFD700;">{code_name}</td></tr>
                            <tr><td style="padding: 10px 0; font-weight: bold; color: #A88B7D;">【核心必杀技】</td><td style="padding: 10px 0; color: #F5E6D3;">{skill}</td></tr>
                            <tr><td style="padding: 10px 0; font-weight: bold; color: #A88B7D;">【隐藏特质】</td><td style="padding: 10px 0; color: #F5E6D3;">{trait}</td></tr>
                        </table>
                        <div style="margin-top: 20px; padding: 15px; background: rgba(255,215,0,0.05); border-left: 4px solid #FFD700;">
                            <p style="margin: 0; font-style: italic; font-size: 16px; color: #FFD700;">「 {fate} 」</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("---")
                    st.subheader("🎬 剧本与分镜生成")
                    
                    clean_script = script
                    if "场景1" in script: clean_script = "场景" + script.split("场景", 1)[1]
                    st.write(clean_script)
                    
                    image_prompts = re.findall(r'(?:【画面描述】|画面描述)[：:\s]*([a-zA-Z0-9\s,\.\'\-]+)', script)
                    if len(image_prompts) < 3:
                        all_en = re.findall(r'([a-zA-Z]+(?:\s+[a-zA-Z,\.]+){2,})', script)
                        for p in all_en:
                            if len(p.split()) >= 3 and p not in image_prompts: image_prompts.append(p)
                    
                    image_prompts = list(dict.fromkeys(image_prompts))[:3]
                    
                    if image_prompts:
                        scene_labels = ["场景 1：事件爆发", "场景 2：情绪发酵", "场景 3：治愈想象与释怀"]
                        for i in range(3):
                            clean_prompt = image_prompts[i] if i < len(image_prompts) else image_prompts[0]
                            with st.spinner(f"正在绘制 {scene_labels[i]}……"):
                                try:
                                    if i == 2:
                                        safe_prompt = f"{char_desc}, {clean_prompt.strip()}, {final_env}, {item_input}, 温暖阳光, 治愈, 电影感, 写实"
                                    elif i == 0:
                                        safe_prompt = f"{char_desc}, {clean_prompt.strip()}, {env_input}, 真实环境, 写实摄影, 电影感"
                                    else:
                                        safe_prompt = f"{char_desc}, {clean_prompt.strip()}, 细节特写, 写实摄影, 真实的室内环境"

                                    img_url = client.images.generate(model="cogview-3-flash", prompt=safe_prompt).data[0].url
                                    st.markdown(f"#### {scene_labels[i]}")
                                    st.image(img_url, use_container_width=True)
                                    if i == 2: st.session_state['poster_img'] = img_url 
                                except Exception as e: st.error(f"画面失败: {e}")
                    
                    if 'poster_img' in st.session_state:
                        st.markdown("---")
                        st.write("### 🎟️ 专属电影海报档案")
                        
                        st.markdown(f"""<div style="position: relative; border-radius: 8px; overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.9); margin: 0 auto; max-width: 400px;"><img src="{st.session_state['poster_img']}" style="width: 100%; display: block; filter: sepia(0.2) contrast(1.1) brightness(0.85);"><div style="position: absolute; top: 20px; left: 0; width: 100%; text-align: center;"><p style="color: rgba(245, 230, 211, 0.6); font-size: 10px; letter-spacing: 4px; margin: 0; font-family: sans-serif;">A MICRO-FILM BY MYSELF</p></div><div style="position: absolute; top: 40%; left: 30px;"><div style="width: 6px; height: 6px; background-color: #FFD700; border-radius: 50%; margin-bottom: 10px; box-shadow: 0 0 10px #FFD700;"></div><h1 style="color: #F5E6D3; margin: 0; font-size: 50px; font-weight: normal; font-family: 'STSong', serif; writing-mode: vertical-rl; letter-spacing: 12px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); line-height: 1.2;">{movie_title}</h1></div><div style="position: absolute; bottom: 20px; right: 20px; text-align: right; background: rgba(0,0,0,0.3); padding: 10px; backdrop-filter: blur(5px); border-radius: 4px; border-right: 2px solid #FFD700;"><p style="color: #F5E6D3; margin: 0 0 5px 0; font-size: 12px; letter-spacing: 1px; font-family: 'STSong', serif;">主演 / {code_name}</p><p style="color: #A88B7D; margin: 0; font-size: 10px;">SCENE / {final_env}</p></div></div>""", unsafe_allow_html=True)
                        
                        st.caption("📸 长按保存或截图，分享你的专属电影时刻。")

                        new_record = {"title": movie_title, "poster": st.session_state['poster_img'], "date": time.strftime('%m.%d')}
                        if new_record not in st.session_state['my_archive']:
                            st.session_state['my_archive'].insert(0, new_record)

                        st.markdown("---")
                        st.subheader("🌊 来自微光共鸣广场")
                        st.write("系统正在为你匹配有相似经历的同伴故事...")
                        
                        matched = False
                        for keyword, posts in MOCK_COMMUNITY.items():
                            if keyword in story:
                                post = posts[0]
                                st.info(f"**匿名用户的经历**：{post['story']}")
                                st.success(f"**他/她后来做了**：{post['action']}")
                                matched = True
                                break
                        
                        if not matched:
                            post = MOCK_COMMUNITY["考试"][1]
                            st.info(f"**匿名用户的经历**：{post['story']}")
                            st.success(f"**他/她后来做了**：{post['action']}")
                    
                    st.session_state['user_story'] = story
                    st.session_state['has_created'] = True
                except Exception as e:
                    st.error(f"生成失败: {e}")

# ==========================================
# 4. Tab 2: 微光手记
# ==========================================
with tab2:
    if not st.session_state.get('has_created', False):
        st.info("请先去【🎬 人生放映厅】生成你的专属电影。")
    else:
        st.write("### 🎞️ 杀青后的微光夜话")
        vibe = st.session_state['vibe']
        
        corpus_quotes = {"烦": "“允许自己休息五分钟，天塌不下来。”", "平": "“人会在平静的日子里重新长出生命力。”", "小": "“你看，生活也会偷偷爱你。”"}
        quote_key = "烦" if "烦" in vibe else ("平" if "平" in vibe else "小")

        with st.chat_message("assistant", avatar="🧚‍♀️"):
            st.write(f"✨ **微光语录：** {corpus_quotes[quote_key]}")
            st.write("💡 **微光夜话：** 电影已经杀青。现在，请为今天选一个画上句号的小行动：")

        st.markdown("---")
        vibe_key = "烦心事" if "烦" in vibe else ("小确幸" if "小" in vibe or "高" in vibe else "平淡")
        selected_actions = random.sample(ACTION_CORPUS[vibe_key], 3)
        options = selected_actions + ["✍️ 其他（我自己写）"]

        chosen_action = st.radio("（行动完成后，再点击下方按钮封存）", options, label_visibility="collapsed", key="action_radio")
        
        if "其他" in chosen_action:
            feedback = st.text_input("📝 写下你的专属微行动：", placeholder="比如：去天台吹吹风...", key="custom_feedback_input")
        else:
            feedback = chosen_action

        st.markdown("---")
        if st.checkbox("🌊 去海边捞一个漂流瓶（点击展开/收起）"):
            if st.button("捞起一个漂流瓶 🍾"):
                st.success(f"🌊 捞到了一个发光的瓶子，里面写着：\n\n**{random.choice(st.session_state['bottles'])}**")

        st.markdown("---")
        is_public = st.checkbox("🌊 愿意把这句话投入大海，或许能温暖另一个迷路的人")

        if st.button("🔒 盖印，封存今日胶片", type="primary"):
            if not feedback.strip():
                st.warning("选一个或写一个吧～")
            else:
                st.snow() 
                st.session_state['archives'].append({"date": time.strftime('%Y.%m.%d'), "vibe": vibe, "feedback": feedback})
                if is_public:
                    st.session_state['bottles'].append(f"“{feedback}” —— 来自刚刚的微光")

                if "烦" in vibe:
                    tags = [("🌪️ 加缪的推石者", "承认荒诞，找到平静。")]
                elif "小" in vibe or "高" in vibe:
                    tags = [("✨ 人间小太阳", "拥有感知美好的超能力。")]
                else:
                    tags = [("📸 幸福拾荒者", "捕捉生活里的糖。")]
                    
                title, desc = random.choice(tags)
                
                st.markdown(f"""
                <div style="background: rgba(26,15,14,0.8); border-radius: 15px; padding: 25px; text-align: center; border: 1px solid #FFD700; margin-top: 20px;">
                    <p style="color: #A88B7D; font-size: 14px;">今日人格：{title}</p>
                    <p style="color: #F5E6D3; font-size: 15px;">“{desc}”</p>
                    <div style="border-top: 1px dashed #6B4C3A; margin: 15px 0;"></div>
                    <p style="color: #FFD700; font-size: 16px;">“ {feedback} ”</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.toast("已记入人生档案，下次难过记得来看看。", icon="🌊")

# ==========================================
# 5. Tab 3: 我的档案库
# ==========================================
with tab3:
    st.write("### 🎞️ 我的专属人生切片")
    st.caption("每一次微小的重构，都在这里沉淀为你抵抗风雨的心理资产。")
    
    if not st.session_state['my_archive']:
        st.info("你还没有生成过档案，快去人生放映厅创作吧～")
    else:
        cols = st.columns(3)
        for idx, record in enumerate(st.session_state['my_archive']):
            with cols[idx % 3]:
                if record.get('poster'):
                    st.markdown(f"""
                    <div style="border-radius: 10px; overflow: hidden; border: 1px solid #6B4C3A; margin-bottom: 15px;">
                        <img src="{record['poster']}" style="width: 100%; display: block;">
                        <div style="padding: 10px; background: rgba(26, 15, 14, 0.9);">
                            <p style="color: #FFD700; margin: 0 0 5px 0; font-size: 14px; font-weight: bold;">《{record['title']}》</p>
                            <p style="color: #A88B7D; margin: 0; font-size: 10px;">记于 {record['date']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")
    st.write("### 📜 历史微光手记回顾")
    if 'archives' in st.session_state and len(st.session_state['archives']) > 0:
        for idx, record in enumerate(reversed(st.session_state['archives'])):
            st.markdown(f"""
            <div style="border: 1px solid #6B4C3A; border-radius: 10px; padding: 15px; margin-bottom: 10px; background: rgba(26, 15, 14, 0.6);">
                <p style="color: #FFD700; margin: 0 0 5px 0; font-weight: bold;">🗓️ {record['date']} · 底色：{record['vibe']}</p>
                <p style="color: #F5E6D3; margin: 0; font-style: italic;">“ {record['feedback']} ”</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("还没有写下过微光手记哦～")
