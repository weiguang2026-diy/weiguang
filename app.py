import streamlit as st
from openai import OpenAI
import time
import re
import random

st.set_page_config(page_title="微光：意义建构与情绪疗愈", page_icon="✨", layout="centered")

# ==========================================
# 🪄 特效注入区：CSS 动画（精灵蹦跳与闪烁）
# ==========================================
st.markdown("""
<style>
/* 精灵蹦跳动画 */
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
.bouncing-elf {
    display: inline-block;
    animation: bounce 1.5s infinite;
}

/* 呼吸闪烁光效 */
@keyframes glow {
    0% { text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #ffcc00; }
    50% { text-shadow: 0 0 10px #fff, 0 0 20px #ffcc00, 0 0 30px #ffcc00; }
    100% { text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #ffcc00; }
}
.glow-text {
    animation: glow 2s infinite;
    color: #ff9900;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# 将标题改为带动画效果的 HTML
st.markdown('<h1 style="text-align: center;">✨ 微光 AIGC 叙事与自我认同平台 <span class="bouncing-elf">🧚‍♀️</span></h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: gray;">把真实的经历，重构为一部赋予生命意义的微电影</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎬 创作微光 (叙事重构)", "🌟 拾取微光 (认知探索)"])

# ==========================================
# 底层核心资产：认知与情绪干预大字典
# ==========================================
COGNITION_RULES = {
    "😰 焦虑": {
        "strategy": "允许暂停与聚焦当下",
        "action": "闭上眼睛深呼吸，用手抚摸胸口安抚自己，关掉电脑去洗把脸",
        "corpus": [
            "大脑在报警，是因为你想一口气做完。允许自己休息五分钟，天塌不下来。",
            "别盯着屏幕了，去洗把脸，回来先做第一件小事。",
            "闭上眼睛，轻声告诉自己：我一定可以复习完的，我一定能轻松抓住考试要点。"
        ]
    },
    "😭 悲伤/孤独": {
        "strategy": "情绪接纳与独立人格建构",
        "action": "给父母打视频通话，喝了药安静睡下，打开手机接受朋友的邀约，把烦心事写下来",
        "corpus": [
            "想哭就哭吧，眼泪不是软弱的证明，而是情绪的自然流动。就像天空下雨是为了洗净尘埃。",
            "大学里的孤独，往往是因为你开始独立思考。试着把‘孤独’重新定义为‘独处’。",
            "你不需要成为别人眼中的完美主角，只需要做自己故事里最真实的主人公。",
            "再黑的黑夜也会迎来黎明，再长的坎坷也会出现平路。耐心点，给好运一点时间。"
        ]
    },
    "😤 愤怒": {
        "strategy": "建立边界感与自我正当性",
        "action": "拉开床帘委婉说明需求，带上耳机隔离噪音，拍下插队证据去举报，去走廊吹风",
        "corpus": [
            "不用假装快乐和温柔，生气和愤怒也是被允许的。",
            "撕碎一张纸，去允许自己发泄愤怒；去做你认为正确的事，不要因为别人的错误惩罚自己。",
            "厌恶也是一种清晰的边界。现在的烦躁像暴雨，可是，雨总会停。"
        ]
    },
    "😳 羞愧": {
        "strategy": "自我宽恕与去中心化",
        "action": "接受自己犯错的事实，告诉自己每个人一天经历很多事，没人会一直记得你的小插曲",
        "corpus": [
            "接纳自己的不完美，就像接纳四季的更迭；你不需要成为任何人，你本身的存在就已经足够美好。",
            "不必觉得自己不够亮，微光也是光。我们不需要先成为一个完美的人，才配拥有完美的人生。",
            "别人明天就会忘了，只有你还在惩罚自己。把注意力收回来，你没有那么多观众。"
        ]
    },
    "👀 嫉妒": {
        "strategy": "认知重评与专注自身赛道",
        "action": "关上手机，拿上书去图书馆学习，主动寻找资源改变自己，多参与群里的活动",
        "corpus": [
            "允许别人发光，也相信自己有节奏。把目光移向自己。",
            "你有自己的赛道，也有自己的远方。别人过的好，不代表你的人生就没机会了。",
            "与其眼红别人的高光，不如去点亮自己的灯。把比较的精力收回到提升自己上。"
        ]
    },
    "😩 厌恶": {
        "strategy": "保护能量场与物理隔离",
        "action": "去走廊吹风，去公园散步，在草稿纸上画搞笑的涂鸦，专注自己喜欢的手工",
        "corpus": [
            "你不必总是理性，总是平静温和，允许自己的厌恶与烦躁。",
            "如果环境让你感到窒息，戴上耳机，给自己建一个安全的避难所。",
            "去专注做一件自己喜欢的小事，把讨厌的世界隔绝在外。"
        ]
    },
    "🌫️ 迷茫": {
        "strategy": "存在主义探索与意义建构",
        "action": "关掉手机去操场走一圈，打开真正感兴趣的书，写下目标和方向开始列计划，与同辈交谈",
        "corpus": [
            "你不必在风暴里立刻找到岸。允许自己漂一会儿；二十几岁，不是人生的答案期，而是探索期。",
            "我身体里的火车从来不会错过，所以允许大雪，风暴，泥石流和荒谬。",
            "有时候，你得先迷路，才能找到你要走的路。微光会陪你一起寻找。"
        ]
    },
    "🍃 平静/无聊": {
        "strategy": "正念觉察与自我关怀",
        "action": "闭上眼睛听音乐，阅读纸质书，在阳台伸懒腰，下楼看看树叶，洗个苹果吃，整理床铺",
        "corpus": [
            "今天的天气很好，我也很好。人会在平静的日子里重新长出生命力。",
            "去做你热爱的事，如果还没有找到热爱，就去看看世界。",
            "如果连思考都觉得提不起劲也没关系，微光在这里陪你坐着，虚度一些时光也没关系。",
            "人间至味是清欢，生活缓缓，一切都在慢慢变好。"
        ]
    },
    "✨ 开心/幸运": {
        "strategy": "积极情绪扩建与感恩",
        "action": "拍下这一刻发朋友圈，奖励自己一杯奶茶，把好运和快乐存进心理账户",
        "corpus": [
            "你看，生活也会偷偷爱你。要相信结局一定配得上这一路的颠沛流离。",
            "去拥抱这份好运吧，不要觉得受之有愧，你值得一切美好的事物。",
            "今天的心情是苹果汽水，记住这一刻的甜，以后不开心的时候拿出来回味。",
            "没有永恒的梅雨季，只有久违的艳阳天。"
        ]
    }
}

# ==========================================
# 标签页 1：创作微光
# ==========================================
with tab1:
    st.write("### 写下今天发生的一件小事")
    st.caption("无论是一次挫折，还是一个微小的高光时刻，微光都会陪你把它变成一部人生微电影。")
    story = st.text_area("你的经历", height=120, placeholder="例如：今天面试失败了，感觉自己一无是处；或者，今天路上看到了一朵很好看的云……", label_visibility="collapsed")
    
    style = st.selectbox("选择你的叙事方式", [
        "🧠 重构挫折 (寻找经历背后的意义)", 
        "🌿 放大美好 (记录你的高光与小确幸)", 
        "🍃 纯粹记录 (不加评判，只是存在)"
    ])
    if st.button("生成专属叙事微电影", type="primary"):
        if not story.strip():
            st.warning("写点什么吧，哪怕只有几个字～")
        else:
            with st.spinner("🧚‍♀️ 微光精灵正在施展叙事魔法，为你重构故事……"):
                try:
                    api_key = st.secrets["API_KEY"]
                    client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
                    
                    prompt = f"""你是一位深谙叙事疗法与积极心理学的导师。请根据用户的经历，创作一部赋予生命意义的“自传体微电影”剧本。
                    
【认知干预指令】
1. 负面经历：运用“认知重评”，把挫折转化为自我成长的契机。
2. 正面经历：运用“积极情绪扩建”，放大美好瞬间。
3. 叙事方式偏好：{style}。

【字数与逻辑要求（极度重要）】
1. 严格输出 3 个场景。
2. 每个场景的【旁白】字数必须丰富（不少于 80 字），要有细腻的内心独白和环境描写，不要像大纲！
3. 场景2到场景3的转折必须自然，不能直接跳跃。必须加入一个具体的“微小细节”（如：冰凉的指尖、窗外的一阵冷风），让主角顺理成章地过渡到【微小行动】。

【画图提示词约束（极度重要）】
在【画面描述】中，请使用纯英文，并必须强制使用写实、接地气的词汇（例如：student dormitory, messy desk, narrow shower room, casual clothes）。绝对禁止使用导致画面变得奢华或西方的词（如：palace, luxury bathtub, Victorian room）。

【输出格式要求】
【场景名】（中文）
【旁白】（中文，第一人称，80字以上）
【画面描述】（纯英文，5-8个词组，例如：Messy student dormitory, a tired student in casual clothes, dim light, realistic）

用户经历：{story}"""
                    
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[{"role": "system", "content": "你是一个叙事疗法编剧。"}, {"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    
                    script = response.choices[0].message.content
                    
                    # 成功特效：气球 + 雪花
                    st.balloons()
                    st.snow()
                    
                    st.markdown('<h3 class="glow-text">✨ 你的专属故事已重构完成：</h3>', unsafe_allow_html=True)
                    st.write(script)
                    
                    st.markdown("---")
                    st.subheader("🎬 分镜画面生成")
                    
                    # 究极暴力提取法
                    image_prompts = []
                    for line in script.split('\n'):
                        if '画面描述' in line:
                            raw_text = line.split('】')[-1]
                            clean_prompt = "".join(c for c in raw_text if (c.isascii() and (c.isalnum() or c in ' ,.')))
                            clean_prompt = clean_prompt.strip()
                            
                            if len(clean_prompt) > 5:
                                safe_prompt = clean_prompt + ", realistic, modern Chinese university campus, humble setting, casual everyday life, no luxury"
                                image_prompts.append(safe_prompt)
                    
                    if image_prompts:
                        for i, img_prompt in enumerate(image_prompts[:3]): 
                            with st.spinner(f"正在绘制场景 {i+1} 的画面……（请稍候）"):
                                try:
                                    img_response = client.images.generate(
                                        model="cogview-3-flash",
                                        prompt=img_prompt
                                    )
                                    st.image(img_response.data[0].url, caption=f"场景 {i+1}", use_container_width=True)
                                except Exception as img_e:
                                    st.error(f"画面 {i+1} 生成失败，接口报错: {img_e}")
                    else:
                        st.warning("⚠️ 系统没有提取到标准的【画面描述】英文，请重新生成一次。")

                    st.session_state['has_created'] = True
                    st.success("👆 故事已生成。现在请点击上方 **【🌟 拾取微光】**，进行更深度的自我对话。")

                except Exception as e:
                    st.error(f"生成失败，请检查 API Key。错误信息：{e}")

with tab2:
    if 'emotion_archive' not in st.session_state:
        st.session_state['emotion_archive'] = []

    if not st.session_state.get('has_created', False):
        with st.chat_message("assistant", avatar="🧚‍♀️"):
            st.write("你好呀，我是微光。请先去左侧 **【创作微光】** 完成你的故事，我们再一起聊聊。")
    else:
        with st.chat_message("assistant", avatar="🧚‍♀️"):
            st.write("刚刚你重新导演了自己的故事。此刻，你心底最真实的感受是什么？")
            
        emotion = st.selectbox("选择你当下的状态：", list(COGNITION_RULES.keys()))
        
        if emotion:
            rule = COGNITION_RULES[emotion]
            selected_corpus = random.choice(rule['corpus'])
            
            with st.chat_message("assistant", avatar="🧚‍♀️"):
                st.write(f"> {selected_corpus}")
                
                if "迷茫" in emotion:
                    st.write("💡 **微光想问你：** 如果十年后的你，回头看今天这个迷茫的自己，你觉得他/她会拍拍你的肩膀，对你说句什么话呢？")
                elif "焦虑" in emotion or "悲伤" in emotion:
                    st.write("💡 **微光想问你：** 那个让你感到充满压力的‘自己’，其实已经很努力了。如果现在给你一个拥抱，你最想对他说什么？")
                else:
                    st.write("💡 **微光想问你：** 感受着此刻的情绪，你觉得身体哪个部位最放松？可以把手轻轻放在那里吗？")
                
                st.info(f"🌱 **微光行动卡：** 在刚刚的故事里，主角做了一件事——*{rule['action']}*。这其实就是你在尝试照顾自己。")
                
            st.markdown("---")
            st.write("### 📁 存入你的「自我对话」档案")
            st.caption("请把刚刚在心里对自己的回答写下来。")
            
            with st.form("archive_form", clear_on_submit=True):
                feedback = st.text_input("你想对自己说：", placeholder="比如：别怕，慢一点也没关系，我已经做得很好了。")
                submitted = st.form_submit_button("记录此刻，完成自我建构", type="primary")
                
                if submitted:
                    if not feedback.strip():
                        st.warning("写一句对自己说的话吧～")
                    else:
                        new_record = {
                            "time": time.strftime('%Y-%m-%d %H:%M'),
                            "emotion": emotion,
                            "feedback": feedback
                        }
                        st.session_state['emotion_archive'].append(new_record)
                        st.balloons()
                        st.success("✅ 已存入！你正在慢慢长出力量。")

        st.markdown("---")
        with st.expander("🗂️ 查看我的「内心成长」轨迹"):
            if len(st.session_state['emotion_archive']) == 0:
                st.info("还没有记录哦，快去打卡吧。")
            else:
                for record in reversed(st.session_state['emotion_archive']):
                    st.info(f"**{record['time']}** | 状态: {record['emotion']} \n\n**我想对自己说:** {record['feedback']}")
