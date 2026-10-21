import streamlit as st
from openai import OpenAI
import time
import re
import random

# ==========================================
# 1. 页面基础配置与终极视觉 CSS
# ==========================================
st.set_page_config(page_title="微光 · 人生放映厅", page_icon="✨", layout="centered")

st.markdown("""
<style>
    /* 红棕星空背景 */
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

    /* 全局文字与隐藏默认 UI */
    * {
        color: #F5E6D3 !important;
        font-family: 'Noto Serif SC', 'STSong', serif !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 按钮 */
    .stButton>button {
        background-color: rgba(26, 15, 14, 0.6) !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5) !important;
        color: #fff !important;
    }
    
    /* 输入框与聊天气泡 */
    div[data-testid="stTextArea"] div[data-baseweb="textarea"],
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: transparent !important;
        border: 1px solid rgba(255, 215, 0, 0.4) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stChatMessage"] {
        background-color: rgba(26, 15, 14, 0.6) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 215, 0, 0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>✨ 微光 · 人生放映厅 🧚‍♀️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A88B7D;'>“一切经历，无论好坏，都塑造了我。”</p>", unsafe_allow_html=True)

# ==========================================
# 2. 核心资产与初始化
# ==========================================
if 'archives' not in st.session_state: st.session_state['archives'] = []

if 'bottles' not in st.session_state:
    st.session_state['bottles'] = [
        "“如果今天很累，就不要逼自己发光了，做个沐浴在月光下的废物也很好。” —— 来自 阿卷",
        "“今天在图书馆崩溃大哭了一场，擦干眼泪去吃了一碗热汤面，突然觉得人生也就这样，吃饱了还能再战。” —— 来自 匿名的大三狗",
        "“别怕，那些让你内耗的事情，几年后回头看，连个屁都不是。” —— 来自 毕业三年的学姐",
        "“分享一个我的小妙招：每次觉得撑不下去的时候，我就去洗个热水澡，假装把所有的烦恼都冲进下水道。” —— 来自 爱洗澡的猫",
        "“其实大家都很水的，别总觉得自己是最差的那个。允许自己偶尔摆烂，这是身体的自我保护机制。” —— 来自 摸鱼达人",
        "“黑夜不是用来害怕的，是用来孵育星星的。祝你今晚有个好梦。” —— 来自 守夜人",
        "“我今天也搞砸了一个很重要的面试。但我刚刚下楼买了一束花送给自己。你看，我们还是能控制一些事情的。” —— 来自 同在迷路的人",
        "“不管今天过得有多烂，只要你还愿意在这里寻找微光，你就已经比昨天更勇敢了。” —— 来自 微光精灵"
    ]

api_key = st.secrets["API_KEY"]
client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")

tab1, tab2 = st.tabs(["🎬 人生放映厅", "🌟 微光手记"])

# ==========================================
# 3. Tab 1: 人生放映厅
# ==========================================
with tab1:
    st.write("### 今天，生活给你加了什么戏？")
    
    col1, col2, col3 = st.columns(3)
    if col1.button("🌪️ 今天很内耗"): st.session_state['story_input'] = "今天去面试被刷了，自己一无是处。"
    if col2.button("🍃 今天很平淡"): st.session_state['story_input'] = "今天什么都没干，有点无聊。"
    if col3.button("✨ 今天有小确幸"): st.session_state['story_input'] = "买到了最后一份糖醋排骨，看到了可爱的猫。"

    story = st.text_area("输入经历", value=st.session_state.get('story_input', ""), height=120, placeholder="哪怕只是一句“今天好累”，也值得被记录。允许自己在这里停一停……", label_visibility="collapsed")
    
    st.write("**选择你的电影底色：**")
    col_b1, col_b2, col_b3 = st.columns(3)
    if 'vibe' not in st.session_state: st.session_state['vibe'] = "🌪️ 烦心事"
    if col_b1.button("🌪️ 烦心事", use_container_width=True): st.session_state['vibe'] = "🌪️ 烦心事"
    if col_b2.button("🍃 平淡", use_container_width=True): st.session_state['vibe'] = "🍃 平淡"
    if col_b3.button("✨ 小确幸/高光", use_container_width=True): st.session_state['vibe'] = "✨ 小确幸/高光"
    
    st.info(f"当前已选择：**{st.session_state['vibe']}**")

    if st.button("🎬 Action！开拍我的电影", type="primary"):
        if not story.strip():
            st.warning("写点什么吧～")
        else:
            # 全光谱情绪自适应加载提示
            current_vibe = st.session_state['vibe']
            if "烦心事" in current_vibe:
                loading_text = "🪄 正在拾取你的经历...\n\n尝试把眼前的挫折，重写为一次成长的伏笔...\n\n电影即将放映，请深呼吸，准备以旁观者的身份看看自己。"
            elif "平淡" in current_vibe:
                loading_text = "🪄 正在捕捉平淡里的微光...\n\n在那些看似无意义的发呆瞬间，往往藏着最真实的自己...\n\n电影即将放映，请放松身体，准备安静地看看今天。"
            else:
                loading_text = "🪄 正在封存这份美好...\n\n尝试把此刻的快乐放大，让它成为未来抵抗风雨的弹药...\n\n电影即将放映，请带着微笑，重温这个闪闪发光的瞬间。"

            with st.spinner(loading_text):
                try:
                    # 🔥 加入强制画面与底色对齐的“死命令”
                    prompt = f"""你是一位深谙叙事疗法与积极心理学的微电影导演。请根据用户的经历，创作一部第一人称的微电影剧本。

【严格贴合底色的死命令】
1. 当前用户选择的电影底色是：**【{st.session_state['vibe']}】**。
2. 如果底色是“小确幸/高光”：剧本必须全程充满温暖、治愈的细节（如阳光、美食、猫咪的特写），**绝对禁止**出现下雨、悲伤、孤独、长椅等负面意象！
3. 如果底色是“烦心事”：才允许出现挫折和最终的释怀。
4. 如果底色是“平淡”：描写安静、发呆的松弛感。

【画面描述约束】
【画面描述】必须直接提取用户经历里的**核心物品**（比如：糖醋排骨、可爱的猫、温暖的阳光、宿舍的桌子），必须使用纯英文（5-8个词组），写实风格。

【剧本格式要求】
1. 必须是第一人称“我”。
2. 严格输出 3 个场景，【旁白】字数不少于 80 字。
3. 剧本的【场景名】和【旁白】必须使用纯中文。

【输出格式要求】
【场景名】（中文）
【旁白】（中文，80字以上）
【画面描述】（纯英文词组，如：Delicious sweet and sour ribs, warm sunlight, cute cat）

用户经历：{story}"""
                    
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[{"role": "system", "content": "你是一位顶级的微电影导演。"}, {"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    script = response.choices[0].message.content
                    st.success("✨ 你的专属故事已重构完成：")
                    st.write(script)
                    
                    st.markdown("---")
                    st.subheader("🎬 分镜画面生成")
                    
                    image_prompts = re.findall(r'画面描述[^a-zA-Z]*([a-zA-Z0-9\s,\.\'\-]+)', script)
                    
                    if image_prompts:
                        for i, clean_prompt in enumerate(image_prompts[:3]): 
                            with st.spinner(f"正在绘制场景 {i+1}……"):
                                try:
                                    safe_prompt = clean_prompt.strip() + ", realistic, modern Chinese university campus, no luxury"
                                    img_response = client.images.generate(model="cogview-3-flash", prompt=safe_prompt)
                                    img_url = img_response.data[0].url
                                    st.image(img_url, caption=f"场景 {i+1}", use_container_width=True)
                                    if i == 0: st.session_state['poster_img'] = img_url 
                                except Exception as img_e:
                                    st.error(f"画面生成失败: {img_e}")
                    else:
                        st.warning("⚠️ 未能提取到画面描述，请点击重新生成。")
                    
                    st.session_state['user_story'] = story
                    st.session_state['has_created'] = True
                    st.success("👆 故事已生成。请点击上方 **【🌟 微光手记】** 继续。")
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
        
        col_img, col_text = st.columns([1, 2])
        with col_img:
            if 'poster_img' in st.session_state:
                st.image(st.session_state['poster_img'], use_container_width=True)
        with col_text:
            st.caption("你刚才经历的是：")
            st.info(f"“{st.session_state.get('user_story', '')[:30]}……”")
            st.caption("看着刚才的画面，此刻，你想对屏幕里的主角说点什么？")
        
        vibe = st.session_state['vibe']
        
        with st.chat_message("assistant", avatar="🧚‍♀️"):
            if "烦心事" in vibe:
                st.write("💡 **微光夜话：** 你看，电影里的你最后用一个小动作接住了自己。现实中，如果屏幕里那个刚经历完挫折的主角就坐在你面前，你会想带他去做点什么小事？")
            elif "平淡" in vibe:
                st.write("💡 **微光夜话：** 电影里记录了你发呆的瞬间。如果给这个平淡的画面配一句你最想说的旁白，会是什么？")
            else:
                st.write("💡 **微光夜话：** 要把这份开心装进漂流瓶寄给未来的自己，你想在瓶子里塞一张写着什么字的纸条？")

        if "烦心事" in vibe and len(st.session_state.get('archives', [])) > 0:
            pos_records = [a for a in st.session_state['archives'] if "小确幸" in a['vibe']]
            if pos_records:
                past = random.choice(pos_records)
                st.info(f"🕰️ **来自过去的微光：** 还记得 {past['date']} 吗？那天你写下：\n\n“*{past['feedback']}*”\n\n今天虽然难，但那个能感知快乐的你，一直都在。")

        st.markdown("---")
        col_bottle1, col_bottle2 = st.columns([1, 2])
        with col_bottle1:
            if st.button("🌊 捞起一个漂流瓶 🍾"):
                st.session_state['show_bottle'] = True
        with col_bottle2:
            if st.session_state.get('show_bottle', False):
                st.success(f"🌊 捡到了一个发光的瓶子，里面写着：\n\n**{random.choice(st.session_state['bottles'])}**")

        st.markdown("---")
        with st.form("archive_form", clear_on_submit=True):
            feedback = st.text_input("📝 写下你的微光手记：", placeholder="在这里写下你的感悟……")
            is_public = st.checkbox("🌊 愿意把这句话投入大海，或许能温暖另一个迷路的人")
            submitted = st.form_submit_button("🔒 盖印，封存今日胶片", type="primary")
            
            if submitted and feedback.strip():
                st.snow() 
                st.session_state['archives'].append({"date": time.strftime('%Y.%m.%d'), "vibe": vibe, "feedback": feedback})
                if is_public: st.session_state['bottles'].append(f"“{feedback}” —— 来自刚刚的微光")
                
                if "烦心事" in vibe:
                    tags = [("🌪️ 加缪的推石者", "承认荒诞，并在推石头的过程中找到平静。"), ("🌫️ 迷雾航海家", "看不清远方没关系，大雾本身就是风景。")]
                else:
                    tags = [("✨ 人间小太阳", "你拥有感知日常美好的超能力。"), ("📸 幸福拾荒者", "你敏锐地捕捉到了生活里的糖。")]
                tag_title, tag_desc = random.choice(tags)
                
                st.markdown(f"""
                <div style="background: rgba(26, 15, 14, 0.8); border-radius: 15px; padding: 25px; text-align: center; border: 1px solid #FFD700; margin-top: 20px; backdrop-filter: blur(10px);">
                    <p style="color: #A88B7D; font-size: 14px; letter-spacing: 2px;">今日人格：{tag_title}</p>
                    <p style="color: #F5E6D3; font-size: 15px; font-style: italic; margin: 20px 0;">“{tag_desc}”</p>
                    <div style="border-top: 1px dashed #6B4C3A; margin: 15px 0;"></div>
                    <p style="color: #FFD700; font-size: 16px;">“ {feedback} ”</p>
                    <p style="color: #555; font-size: 12px; margin-top: 15px;">—— 记于 {time.strftime('%Y.%m.%d')}</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption("📸 这枚徽章已刻入你的生命档案。下次难过时，记得来看看今天的你有多勇敢。")
                st.toast("如果你愿意，可以把这句话扔进海里，给另一个今晚迷路的人一点光。", icon="🌊")
