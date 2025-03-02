'''
Build json file and Anki card
'''
import mdict
import subtitle
import sl
import everything
import freq
import sys
import os
import tqdm
import rich


def main():
    # 读取字幕文件
    subtitles = sl.readstr("subtitles.txt").split("\n")
    progress = tqdm.tqdm()
    subs = {}
    this_dir = os.path.dirname(os.path.abspath(__file__)) + "\\"
    for i in subtitles:
        subs[i] = {}
        skip_save = False
        if os.path.isfile(i):
            print(f"Processing Single Subtitle {i}")
            subdirtitles = [i]
            if os.path.exists(
                f"{this_dir}{os.path.basename(i)[:-3]}@{os.path.basename(i)}"
            ):
                skip_save = True
        else:
            print(f"Processing Directory {i}")
            subdirtitles = everything.search_ext("ass", i)
            if len(subdirtitles) == 0:
                subdirtitles = everything.search(
                    f"{this_dir}{os.path.basename(i)} @ .ass"
                )
                skip_save = True
        for j in subdirtitles:
            print(f"  Processing Subtitle{j}")
            if skip_save:
                name = os.path.basename(j)
                namejson = name
            else:
                name = os.path.basename(i) + "@" + os.path.basename(j)
                namejson = f"{name}.json"
            s = subtitle.SUBTITLE()
            if os.path.exists(namejson):
                s.load_json(namejson)
            elif not skip_save:
                s.load_ass(j)
                s.save_json(namejson)
            subs[i][name] = s
            progress.update(1)
    progress.close()
    # 跨文档清理
    for bangumi, subtitles in subs.items():
        # 清理没有翻译的字段
        # 清理空字段
        # 清理在许多文件中出现(>80%)重复的字段：具有完全相同的原文和翻译（只保留第一份）
        # filter_notrans(subtitles)
        # filter_void(subtitles)
        # filter_multiincidence(subtitles)
        pass
    # 解析日文
    # 统计词频
    # 输出词频
    return subs


def main_freq():
    # 打开字典
    md = mdict.MDICT()
    md.load_json()
    # 读取频数
    test = [
        "250adv.json",
        "500adj.json",
        "1000.json",
        "2000.json",
        "2000v.json",
        "3000.json",
        "adjj.json",
    ]
    test = ["500adj.json"]
    datas = []
    for i in test:
        f = freq.FREQ()
        f.load_json(i)
        for i in f.data:
            datas.append((i["headword"], i["freq"]))
    datas.sort(key=lambda x: x[1], reverse=True)
    sl.save("freq.json", datas, pretty=True)


def main_freq_rank():
    max_rank = 400
    min_rank = 0
    datas: list[list] = sl.load("freq.json")
    datas = datas[min_rank:max_rank]
    md = mdict.MDICT()
    md.load_json()
    md.textify = lambda text: str(text)
    f = md.find
    md.find = lambda word: (f(word) or f(word[:-1])) + find_subs(word, subs)
    subs = main()
    progress = tqdm.tqdm(datas)
    ret = []
    for i in progress:
        word = i[0]
        if word.find("非自立") >= 0:
            continue
        i.append(md.find(word))
        ret.append(i)
    sl.save(f"dict-freq-adj-{min_rank}-{max_rank}.json", ret)


def filter_void(subs: "dict[str,subtitle.SUBTITLE]"):
    for i, data in subs.items():
        index = data.get_index()
        for i in index:
            line_ids = data.index[i]
            for p, id in enumerate(line_ids):
                line = data.lines[id]
                if len(line) == 0:
                    pass


def filter_sub_normal(l):
    ret = []
    for i in l:
        score = 0
        lines = [l for l in i.split("\n") if l]
        if len(lines) == 2:
            score += 10
        if len(lines) == 0:
            score = 0
        elif len(lines[0]) <= 1:
            score += 1
        ret.append((score, i))
    ret.sort(key=lambda x: x[0], reverse=True)
    return [i[1] for i in ret]


def find_subs(text, subs: "dict[str,dict[str,subtitle.SUBTITLE]]"):
    ret = set()
    max_len_subs = 10
    progress = tqdm.tqdm(leave=False)
    for i, subtitles in subs.items():
        for i, data in subtitles.items():
            val = data.find(text, split=True)
            ret.update(val)
            progress.update(1)
    ret = filter_sub_normal(ret)
    if len(ret) > max_len_subs:
        ret = ret[:max_len_subs]
    return htmlify(ret)


def htmlify(ret):
    s = ["""<div class="subtitles">"""]
    linebreak = "\n\n"
    for i in ret:
        s.append(
            f"""<div class="subtitle"><div>{i.replace(linebreak,"<br/>")}</div>""")
    s.append("</div>")
    return "".join(s)


if __name__ == "__main__":
    # main()
    main_freq()
    main_freq_rank()
