"""
util to load a mdx/mdd dictionary
"""

import os
import sys
import html2text
import sl
from cc import to_chs
from readmdict import MDX, MDD
# from bloom_filter import BloomFilter

h = html2text.HTML2Text()


class MDICT:
    filename = "mdict.zip"
    jsonname = "mdict.json"

    def __init__(self):
        self.entries = []
        self.index = {}
        self.maxlenth = 10000
        self.bloom_error_rate = 0.1
        # self.bloom = BloomFilter(
        #    max_elements=self.maxlenth, error_rate=self.bloom_error_rate)

    def load_dict(self, path):
        if not path or not os.path.exists(path):
            print("dictionary not found", path)
            return
        if path.endswith(".mdd"):
            dic = MDD(path)
        else:
            dic = MDX(path)
        self.append_dict(dic)

    def append_dict(self, dic):
        error_rate = 0
        error_count = 0
        l = 0
        for k, v in dic.items():
            l += 1
            key = k.decode()
            try:
                value = v.decode()
            except:
                error_count += 1
                error_rate = error_count / l
                if error_rate > 0.1:
                    print("error rate too high, abort")
                    return
                else:
                    continue
            self.entries.append((key, value))
            # self.bloom.add(key)
            if key in self.index:
                self.index[key].append(len(self.entries) - 1)
            else:
                self.index[key] = [len(self.entries) - 1]
        l = len(self.entries)
        if l > self.maxlenth*10:
            self.rebuild_filter()

    def rebuild_filter(self):
        self.maxlenth = len(self.entries)
        # self.bloom = BloomFilter(
        #    max_elements=self.maxlenth, error_rate=self.bloom_error_rate)
        # for k in self.index.keys():
        #    self.bloom.add(k)

    @staticmethod
    def textify(text):
        text = h.handle(text)
        # text = to_chs(text)
        if text.startswith('@@@LINK='):
            l1, l2 = text.find('【'), text.find('】')
            if l1 > 0 and l2 > l1:
                text = text[l1+1:l2]
                return text, True
        return text

    def find(self, word):
        if word not in self.index:
            return ""
        entries = self.index.get(word)
        if not entries:
            return f"{word} not found"
        s = [self.textify(self.entries[i][1]) for i in entries]
        for id, i in enumerate(s):
            if isinstance(i, tuple):
                i = i[0]
                s[id] = ""
                if word in i or i in word:
                    # self reference
                    pass
                else:
                    w = self.find(i)
                    if not w:
                        w = self.find(i[:-1])
                    if w:
                        s[id] = w
        st = "\n\n".join(s)
        return st

    def save_json(self, filename=None, jsonname=None):
        if jsonname or self.jsonname:
            sl.save_json_zip(filename or self.filename,
                             jsonname or self.jsonname, {"entries": self.entries, "index": self.index})
        else:
            sl.save(
                filename or self.filename, {
                    "entries": self.entries, "index": self.index}
            )

    def load_json(self, filename=None, jsonname=None):
        if jsonname or self.jsonname:
            data = sl.load_json_zip(filename or self.filename,
                                    jsonname or self.jsonname)
        else:
            data = sl.load_json(filename or self.filename)
        if not data:
            return
        if len(self.entries) > 0:
            print("warning: reloading mdict will clear previous entries")
        self.entries = data["entries"]
        self.index = data["index"]
        self.rebuild_filter()

    def batch_load_dict(self, directory):
        """
        try to read a batch of mdx/mdd files
        """
        found_dict = []
        for root, dirs, files in os.walk(directory):
            for f in files:
                if not (f.endswith(".mdx") or f.endswith(".mdd")):
                    continue
                found_dict.append(os.path.join(root, f))
        found_mapping = {}
        for dic in found_dict:
            if dic.endswith(".mdd"):
                found_mapping[dic] = True
            else:
                dic_mdd = dic.replace(".mdx", ".mdd")
                if dic_mdd not in found_dict:
                    found_mapping[dic] = True
        for dic in found_mapping:
            print("loading", dic)
            self.load_dict(dic)


if __name__ == "__main__":
    m = MDICT()
    m.batch_load_dict("H:/dict/日语/")
    m.save_json()
