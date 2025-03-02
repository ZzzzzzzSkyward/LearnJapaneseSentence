import copy
from google_search import do_search
import openai
from config import config as cfg
config = cfg.ai
client = openai.OpenAI(api_key=config.api_key, base_url=config.endpoint)
translate_prompt1 = '''我是一个日语初学者，我想要理解日语句子或单词的含义，你的任务是对于我给出的字符串，先拆分句子，详细解释重点难点单词（汉字给出发音）的字典义、语境义，然后给出简体中文翻译，最后提示易错点，总体字数控制在10~50字/个单词。
需要解释的字符串=あなた'''
# created by deepseek-r1 at 2025/3/2
translate_prompt_answer1 = '''
### 拆分

1. あなた

    - **字典义** 第二人称代词"你"。
    - **语境义** 直接称呼时可能稍显疏离（正式场合可用），夫妻间使用表亲昵。

### 翻译

你 / 亲爱的（配偶间）

### 解析

现代日语中过度使用易显生硬，建议多用姓名+さん的称呼方式。  '''
translate_prompt2 = '''需要解释的字符串=世間の音など 気にもせず'''
translate_prompt_answer2 = '''
### 拆分

1. 世間`せけん`

    - **字典义** 社会/人世间
    - **语境义** 社会舆论

2. 音`おと`

    - **字典义** 声音。需要注意“音”和“声`こえ`”的区别，前者多指无生命的声音，后者多指人或动物发出的声音
    - **语境义** 议论、流言、闲言碎语

3. など

    - **字典义** 之类的、什么的，带有不屑或轻视的语气
    - **语境义** 暗示上文主语不值一提

4. 気`き`にもせず

    - **字典义** 完全不放在心上。原形：気にする，在意

### 翻译

对周围的杂音毫不在意。

### 解析

1. “せず”是“しない”的古语或书面形式，由“する”的未然形“せ”加上否定助动词“ず”构成。

'''


def openai_send(query: str, message: list, use_web=False, config=config):
    me = message
    if use_web:
        from google_search import do_search
        web_res = do_search(query)
        from sl import jsondump
        if web_res:
            print(web_res)
            web_res = jsondump({i['title']: i['content'] for i in web_res})
            me.append({"role": "user", "content": f"以下是web搜索结果：{web_res}"})
    response = client.chat.completions.create(
        model=config.model,
        messages=me,
        temperature=config.temperature,
        stream=False,
        timeout=60
    )
    return response.choices[0].message.content


msg_explain = [
    {"role": "user", "content": translate_prompt1},
    {"role": "assistant", "content": translate_prompt_answer1},
    {"role": "user", "content": translate_prompt2},
    {"role": "assistant", "content": translate_prompt_answer2},
    {"role": "user"}
]
msg_memorize = [
    {"role": "user", "content": "我是日语初学者。我想要通过联想法背单词。请你根据我给出的单词进行近义词、反义词、词源、用词搭配检索，帮我找到一些能够一起记忆的单词。比如我现在要背【限界】"},
    {"role": "assistant", "content": '''
### 1. 核心词：限界（げんかい）

**含义**：极限、界限（物理或抽象的边界）

**词源分解**：
- **限（げん）**：限制
- **界（かい）**：范围、领域（如「世界（せかい）」中的「界」）

---

### 2. 近义词 & 同类词联想

1. 境界（きょうかい）

    - **联想点**：同样是「かい」结尾，表示边界（如国境、意识边界）。

    - **差异**：「限界」强调“极限”，「境界」更中性（如「境界線」）。

2. 限度（げんど）
    - **联想点**：共享「限」表示限制，但「限度」更强调“允许的最大值”（如时间限度）。

3. 制限（せいげん）
    - **联想点**：含「限」，指外部施加的限制（如法律限制）。

---

### 3. 反义词 & 对比词
1. 無限（むげん）
    - **反义焦点**：「無」否定「限」，直接对立（如「無限の可能性」）。

2. 無制限（むせいげん）
    - **对比**：否定「制限」，强调“无约束”（如时间无限制）。

---

### 4. 搭配用法强化记忆
- **限界を超える（超限界）**：突破极限（例：体力の限界を超える）
- **限界に達する**：达到极限（例：忍耐の限界に達した）
- **限界点**：临界点（物理/心理）

---

### 5. 发音 & 词形联想
1. 同音词：原価（げんか）**
    - **对比记忆**：发音相近但意义不同（「原価」= 成本），需注意区分。

2. 词尾扩展：～界（～かい）**
    - **世界（せかい）**：世界
    - **業界（ぎょうかい）**：行业
    - **冥界（めいかい）**：冥界（神话）

---

### 6. 汉字部首联想
1. 限（gen）的延伸**
    - **期限（きげん）**：截止日期
    - **限定（げんてい）**：限定款

2. 界（kai）的延伸**
    - **外界（がいかい）**：外部世界
    - **限界点（げんかいてん）**：临界点

---

### 7. 反向应用：造句巩固
- **例1**：
  「**限界**を超えるために、毎日**制限**時間内に練習する」（为突破极限，每天在限定时间内练习）
- **例2**：
  「**無限**の可能性を信じるが、現実の**限界**も知る」（相信无限可能，但也知晓现实界限）

---

### 记忆技巧总结
1. **词根拆分**：将「限界」拆解为「限（限制）+ 界（范围）」，联想“被限制的范围”。

2. **对比法**：通过反义词「無限」强化“界限存在与否”的对比。

3. **场景联想**：想象运动员突破体力「限界」，或游戏中「制限時間」倒数。

'''},
    {"role": "user"}
]


def talk_to_ai(text, message=msg_explain, web=False):
    try:
        msg = copy.deepcopy(message)
        msg[-1]['content'] = text
        response = openai_send(text, msg, use_web=web)
        if response:
            return response.replace('\n  -', '\n     -')
    except Exception as e:
        print("Exception in talk_to_ai", e)
        return ""
