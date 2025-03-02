from romaji_jp import romanji_jp_dict
import ollama
api_endpoint = 'http://localhost:11111'
api_chat = '/api/chat'
client = ollama.Client(
    host=api_endpoint,
)
m = {i: v for i, v in romanji_jp_dict.items() if i.lower() == i}
for r, j in m.items():
    print(r, j)
    msg = {"role": "user", "content": f'{r} 的日文发音是 {j}，请给出最接近它的拼音。'}
    response = client.chat(
        model="deepseek",
        messages=[{"role": "user", "content": '当前任务是判断拼音里最接近某个日语的发音的是哪个。例如要找到最接近 "つ"（tsu）发音的拼音，我们需要考虑中文拼音系统中的音值。"つ"在日文中发音类似于英语的 "ts"，在拼音系统中，"ts" 的对应拼音是 "ci"。直接给出一个最可能的答案，必须使用英文字母[a-z]回答，不要说明，不要提问。答案可以不存在对应汉字。禁止回复汉字。'}, msg]
    )
    ret = response.message.content
    print(ret)
romaji_pinyin_dict = {
    "be": ["bei", "bie", "bai"]
}
