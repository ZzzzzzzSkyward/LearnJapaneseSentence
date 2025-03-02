from cache import CACHE
import os
import ass
import sl
import re
import tokenizer
from pyfranc import franc

notes = {
    "zh": [
        "CN",
        "CH",
        "chinese",
        "Chinese",
        "CHINESE",
        "中文",
        "汉语",
        "cn",
        "ch",
        "zh",
    ],
    "en": ["US", "UK", "us", "uk", "english", "English", "ENGLISH"],
    "jp": ["JP", "日本語", "Japanese", "jp", "JAPANESE"],
}
supported_langs = list(notes.keys())
langs_map = {
    "cmn": "zh",
    "eng": "en",
    "jpn": "jp",
}
langs_map_langs = list(langs_map.keys())
punctuations=",.;:'\"<>?!@#$%^&*()[]{}-_=+|「」"

def detect_lang(text, note=None, min_length=5):
    guess = None
    # try note
    if note:
        for lang, keywords in notes.items():
            for keyword in keywords:
                if keyword in note:
                    guess = lang
                    break
            if guess:
                break
    # try detect
    try:
        prob = franc.lang_detect(
            text, whitelist=langs_map_langs, minlength=min(
                len(text), min_length)
        )
    except:
        print(f"Warning: cannot detect language of {text}")
        print(f"note: {note}")
        return guess
    for i in prob:
        if i[0] not in langs_map:
            continue
        lang = langs_map[i[0]]
        p = i[1]
        if guess == lang and guess and p >= 0.5:
            return lang
        elif p >= 0.3:
            return lang
    #try this is a fx
    non_char_count=0
    char_count=0
    for i in text:
        if '0'<=i<='9' or i in punctuations:
            non_char_count+=1
        else:
            char_count+=1
    if non_char_count>=char_count and non_char_count>1:
        return None
    print(f"Warning: cannot detect language of {text}")
    print(f"note: {note}")
    print(f"Guess1: {guess}")
    for i in prob:
        print(f"Detect: {i}")
    return None


pattern_bracket = re.compile("{[^}]*}")

tcache = CACHE()
tcache.name = "translation_cache.json"
tcache.load()


class SUBTITLE:
    def __init__(self):
        self.lines = None
        self.name = None
        self.index = None
        pass

    def load_subtitle(self, name):
        if name.endswith(".ass"):
            return self.load_ass(name)

    def load_ass(self, name):
        try:
            s = sl.readstr(name)
            subtitle = ass.parse_string(s)
        except:
            return
        if self.name and self.name != name:
            print(f"Warning: {self.name} will be overridden.")
        self.name = name
        lines = subtitle.sections["Events"]._lines
        self.lines = self.lines or []
        self.index = self.index or {}
        errors = 0
        len_lines = len(lines)
        for i in lines:
            if type(i) == ass.Comment:
                continue
            style = i.style
            text = i.text
            id = self.get_ass_id(i)
            text = self.textify(text)
            style = detect_lang(text, style)
            if not style:
                errors += 1
                error_rate = errors / len_lines
                if error_rate > 0.1:
                    print(f"Warning: {name} has too many errors. Refuse!")
                    return
                continue
            self.lines.append((style, text,i))
        self.sort_lines()
    @staticmethod
    def get_time(t_str):
        #0:00:04.530000
        parts=t_str.split(":")
        t=0
        for i in parts:
            try:
                tt=float(i)
                t+=tt
                t*=60
            except:
                break
        return t
    def sort_lines(self):
        lines=self.lines
        jpnlines=[]
        tranlines=[]
        timeline=[]
        timeline_trans=[]
        for i in lines:
            if i[0]=='jp':
                jpnlines.append(i)
                timeline.append([self.get_time(i[2]),i])
            else:
                tranlines.append(i)
                timeline_trans.append([self.get_time(i[2]),i])
        timeline=self.merge_timeline(timeline)
        timeline_trans=self.merge_timeline(timeline_trans)
        timeline,timeline_trans=self.compare_timeline(timeline,timeline_trans)
        #rebuild index
        self.index={}
        for id,i in enumerate(timeline):
            t=i[0]
            t1=timeline_trans[id][1]
            if t not in self.index:
                self.index[t]=[]
            self.index[t].append([i[1][0],i[1][1]])
            self.index[t].append([t1[0],t1[1]])
            
    @staticmethod
    def merge_timeline(timeline):
        if len(timeline)==0:
            return timeline
        new_line=[]
        timeline.sort(key=lambda x:x[0])
        now=-1
        delta=0.1
        new_line.append(timeline[0])
        for i in timeline[1:]:
            if i[0]-now<=delta:
                thisline=i[1]
                lastline=new_line[len(new_line)-1][1]
                text=lastline[1]
                style=lastline[0]
                text+=thisline[1]
                newsub=[style,text,lastline[2]]
                new_line[len(new_line)-1][1]=newsub
            else:
                now=i[0]
        return new_line
    @staticmethod
    def compare_timeline(t1,t2):
        #t1 is the standard
        intermediate=-1
        delta=0.5
        large=1e5
        small=1e-3
        bounds=[]
        for id,i in enumerate(t1):
            t=i[0]
            prev_bound=max(t-delta,0,intermediate)
            next_line=t1[id+1] if id+1<len(t1) else None
            if next_line:
                intermediate=(t+next_line[0])/2
            else:
                intermediate=large
            next_bound=min(t+delta,intermediate)+small
            bounds.append((prev_bound,next_bound))
        #prev_bound<=t<next_bound
        curr=0
        prev_bound,next_bound=bounds[curr]
        mapping=[[] for i in bounds]
        for id,i in enumerate(t2):
            t=i[0]
            while 1:
                if t>=prev_bound:
                    if t<next_bound:
                        #OK, found the boundary
                        mapping[curr].append(i)
                        break
                    else:
                        #go ahead
                        curr+=1
                        if curr>=len(bounds):
                            #not found, and force break
                            print(f"can't find a bound for {i[1]} ")
                            break
                        #next bound
                        prev_bound,next_bound=bounds[curr]
                else:
                    if curr>0:
                        #put it back to the last
                        mapping[curr-1].append(i)
                    else:
                        #not found, and force break
                        print(f"can't find a bound for {i[1]}")
                        break
        #check if there still have some lines left
        flag=curr<len(bounds)
        if flag:
            print(f"There are some lines left: pointer at{curr}, total {len(bounds)}" )
        #rebuild two timelines using mapping
        new_t1=t1
        new_t2=[]
        for id,i in enumerate(mapping):
            t1_time=new_t1[id][0]
            if len(i)>0:
                first_line=i[0]
                text=" ".join([j[1][1] for j in i])
                new_line=[t1_time,[first_line[0],text,first_line[2]]]
        return new_t1,new_t2
        
    @staticmethod
    def get_ass_id(i):
        start = i.start
        end = i.end
        id = str(start)
        last_zero = id.rfind("0")
        if last_zero != -1:
            first_last_zero = last_zero
            while id[first_last_zero] == "0":
                first_last_zero -= 1
            id = id[: first_last_zero + 1]
        return id
        # somehow the end time is not accurate
        return f"{start}-{end}"

    @staticmethod
    def remove_bracket(text):
        return re.sub(pattern_bracket, "", text)

    @staticmethod
    def textify(text):
        text = text.replace("\\N", "\n")
        # remove {xxx}
        text = SUBTITLE.remove_bracket(text)
        return text

    def print(self):
        if not self.lines:
            ("No subtitle loaded.")
        else:
            print(f"Subtitle {self.name}")
            for line in self.lines:
                print(line[0], line[1])

    def print_indexed(self):
        if not self.lines or not self.index:
            ("No subtitle loaded.")
        else:
            print(f"Subtitle {self.name}")
            index = sorted(list(self.index.keys()))
            for i in index:
                for j in self.index[i]:
                    data = self.lines[j]
                    print(data[0], data[1])

    def get_index(self) -> "list[str]":
        if not self.index:
            return []
        return sorted(list(self.index.keys()))

    def get_data(self, index):
        if not self.index or not self.lines:
            return []
        ids = self.index[index]
        ret = []
        for i in ids:
            data = self.lines[i]
            ret.append(data)
        return ret

    def save_json(self, name=None):
        name = name or self.name
        data = {"index": self.index, "lines": self.lines}
        sl.save(name, data)

    def load_json(self, name=None):
        name = name or self.name
        data = sl.load(name)
        if not data:
            return
        if self.name and self.name != name:
            print(f"Warning: {self.name} will be overridden.")
        self.index = data["index"]
        self.lines = data["lines"]
        self.name = name

    def find(self, word, split=False):
        # 去重、乱序
        ret = set()
        if not self.lines:
            return ret
        index = self.get_index()
        # params = [(i, word, split) for i in index]
        # 创建一个进程池
        # with multiprocessing.Pool() as pool:
        #    # 使用进程池来并行执行self.get_data
        #    results = pool.starmap(self.find_word, params)
        # 汇总结果
        # results = [item for sublist in results for item in sublist]
        for i in index:
            result = self.find_word(i, word, split)
            ret.update(result)
        # 保存缓存
        tcache.save()
        return ret

    def find_word(self, id, word: str, split=False):
        dat = self.get_data(id)
        ret = set()
        for j in dat:
            style = j[0]
            text = j[1]
            if text and style == "jp":
                if split:
                    # only japanese requires split
                    tokens = tcache.get(text)
                    if not tokens:
                        # cache
                        tokens = tokenizer.tokenize(text)
                        tokens = [tokenizer.TOKENIZER.json(i) for i in tokens]
                        tcache.set(text, tokens)
                    tokens = [i["lemma_"] for i in tokens]
                    if word in tokens:
                        lines = set([k[1] for k in dat])
                        ret.add("\n\n".join(lines))
                        break
                elif text.find(word) != -1:
                    lines = set([k[1] for k in dat])
                    ret.add("\n\n".join(lines))
                    break
        return ret


if __name__ == "__main__":
    s = SUBTITLE()
    test_sutitle = "J:/video/电影短片/[DBD-Raws][葬送的芙莉莲][01-28TV全集+特典映像][1080P][BDRip][HEVC-10bit][简繁日双语外挂][FLAC][MKV]/[DBD-Raws][Sousou no Frieren][14][1080P][BDRip][HEVC-10bit][FLACx2].scjp.ass"
    s.load_subtitle(test_sutitle)
    print(s.get_data(s.get_index()[0]))
