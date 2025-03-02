try:
    import pykakasi
    import spacy
    import ginza
except:
    pass
import re
from cc import to_chs


class BASE_SENT:
    def __init__(self) -> None:
        self.sents = []
    sents = []


class BASE_MORPH:
    def __init__(self, text) -> None:
        self.Reading = [text]
    Reading = []
    Inflection = ""

    def get(self, name, default=None):
        if name == "Reading":
            return self.Reading or default
        elif name == "Inflection":
            return self.Inflection or default
        else:
            raise ValueError(f"Unknown attribute {name}")


class BASE_TOKEN:
    def __init__(self, text=None) -> None:
        if text:
            self.orth_ = text
            self.lemma_ = text
            self.norm_ = text
            self.morph = BASE_MORPH(text)
            self.head = BASE_TOKEN()
    i = 0
    orth_ = ""
    lemma_ = ""
    norm_ = ""
    pos_ = ""
    tag_ = ""
    dep_ = ""

    def __str__(self) -> str:
        return self.orth_

    def __repr__(self) -> str:
        return self.orth_ or "<?>"


class TOKENIZER:
    def __init__(self):
        # self.load_model_ginza()  # default model
        self.model = self.base_tokenize
        self.currentmodel = "base"
        pass

    def load_model_ginza(self):
        if self.currentmodel != "ginza":
            try:
                import ja_ginza_electra
                self.model = spacy.load("ja_ginza_electra")
            except:
                self.model = spacy.load("ja_ginza")
            self.currentmodel = "ginza"

    def load_model_kks(self):
        if self.currentmodel != "kks":
            self.model = self.kks
            self.currentmodel = "kks"

    def tokenize(self, text):
        doc = self.model(text)
        tokens = []
        for sentence in doc.sents:
            for token in sentence:
                token: ginza.Token = token
                i = token.i
                orth_ = token.orth_
                lemma_ = token.lemma_
                norm_ = token.norm_
                Reading = token.morph.get("Reading")
                pos_ = token.pos_
                Inflection = token.morph.get("Inflection")
                tag_ = to_chs(token.tag_)
                dep_ = token.dep_
                headi = token.head.i

                tokens.append(token)
        return tokens

    @staticmethod
    def print_token(token):
        print(
            token.i,
            token.orth_,
            token.lemma_,
            token.norm_,
            token.morph.get("Reading"),
            token.pos_,
            token.morph.get("Inflection"),
            token.tag_,
            token.dep_,
            token.head.i,
        )

    @staticmethod
    def json(token: "ginza.Token"):
        return {
            "orth_": token.orth_,
            "lemma_": token.lemma_,
            "norm_": token.norm_,
            "Reading": token.morph.get("Reading"),
            "pos_": to_chs(token.pos_),
            "Inflection": token.morph.get("Inflection"),
            "tag_": to_chs(token.tag_),
            "dep_": token.dep_,
        }

    @staticmethod
    def create_token(text):
        ret = BASE_TOKEN(text)
        return ret

    @staticmethod
    def simple_split(text):
        # 定义一个正则表达式，用于匹配日文中的空白、标点符号和特殊字符
        pattern = r'(\s+|。|、|「|」|\?|！|…|&)'
        # 使用re.split进行分词
        tokens = re.split(pattern, text)
        # 过滤掉空字符串
        tokens = [token for token in tokens if token]
        return tokens

    @classmethod
    def base_tokenize(cls, text):
        sents = re.split("。|\n", text)
        splitsents = [cls.simple_split(sent.strip())
                      for sent in sents if sent.strip()]
        ret = BASE_SENT()
        for sent in splitsents:
            tokenized = [cls.create_token(i) for i in sent]
            ret.sents.append(tokenized)
        return ret

    @classmethod
    def kks(cls, text):
        ret = BASE_SENT()
        sents = re.split("。|\n", text)
        splitsents = [sent.strip()
                      for sent in sents if sent.strip()]
        for text in splitsents:
            tokens = kks.convert(text)
            sent = []
            for id, i in enumerate(tokens):
                tok = BASE_TOKEN(i["orig"])
                tok.i = id
                tok.morph.Reading = [i["hira"]]
                sent.append(tok)
            ret.sents.append(sent)
        return ret


_TOK = TOKENIZER()


def tokenize(text, model="ginza"):
    try:
        if model == "ginza":
            _TOK.load_model_ginza()
        elif model == "kks":
            _TOK.load_model_kks()
    except:
        pass
    return _TOK.tokenize(text)


kks = pykakasi.kakasi()


def romanize_list(tokens: "list[dict]"):
    """
    将包含日语平假名字符串的列表转换为罗马字列表。

    Args:
        tokens (list[dict]): 包含字典的列表，每个字典中包含一个"Reading"键，其值是一个包含日语平假名字符串的列表。

    Returns:
        list: 包含罗马字字符串的列表。

    """
    result = []
    for i in tokens:
        hira = i.get("Reading")
        if hira and len(hira) > 0:
            romajis = romanize(hira[0])
            result.append(" ".join(romajis))
        else:
            result.append("")

    return result


def hiragize_list(tokens: "list[dict]"):
    result = []
    for i in tokens:
        hira = i.get("Reading")
        if hira and len(hira) > 0:
            hirajis = hiraize(hira[0])
            result.append(" ".join(hirajis))
        else:
            result.append("")

    return result


def romanize(text):
    """
    将给定的文本转换为罗马字表示。

    Args:
        text (str): 需要转换的文本。

    Returns:
        list[str]: 转换后的罗马字表示

    """
    items = kks.convert(text)
    romajis = [i['hepburn'] for i in items]
    return romajis


def hiraize(text):
    """
    将输入的文本转换为平假名字符串。

    Args:
        text (str): 要转换的文本。

    Returns:
        str: 转换后的平假名字符串，单词之间用空格分隔。

    """
    items = kks.convert(text)
    hiras = [i['hira'] for i in items]
    return "".join(hiras)


if __name__ == "__main__":
    text = "しかし　他の技量が　あまりにも卓越し過ぎている"
    tokens = tokenize(text, "kks")
    print(tokens)
    for i in tokens:
        TOKENIZER.print_token(i)
    print(romanize_list([TOKENIZER.json(i) for i in tokens]))
    print(hiragize_list([TOKENIZER.json(i) for i in tokens]))

"""かな: kana 'カナ', hiragana: 'かな', romaji: 'kana'
漢字: kana 'カンジ', hiragana: 'かんじ', romaji: 'kanji"""
"""
[しかし, 　, 他, の, 技量, が, 　, あまり, に, も, 卓越, し, 過ぎ, て, いる]
i orth_ lemma_  norm_   Reading      pos_   Inflection tag_        dep_ headi
0 しかし しかし    然し    ['シカシ']    CCONJ  []         接続詞       cc 10
1 　 　 　               []           NOUN   []         空白         advmod 10
2 他    他       他      ['タ']       NOUN   []          名詞-普通名詞-副詞可能 nmod 4
3 の    の       の      ['ノ']       ADP    []         助詞-格助詞    case 2
4 技量  技量      技量    ['ギリョウ']   NOUN   []        名詞-普通名詞-一般 nsubj 10
5 が    が       が      ['ガ']       ADP    []        助詞-格助詞     case 4
6 　 　 　               []           NOUN   []         空白          advmod 10
7 あまり あまり   余り     ['アマリ']    ADJ    []         形状詞-一般     advcl 10
8 に    だ       だ       ['ニ']       AUX    ['助動詞-ダ;連用形-ニ'] 助動詞 aux 7
9 も    も       も       ['モ']       ADP    []         助詞-係助詞     case 7
10 卓越 卓越      卓越    ['タクエツ']  VERB    []         名詞-普通名詞-サ変可能 ROOT 10
11 し   する      為る    ['シ']       AUX    ['サ行変格;連用形-一般'] 動詞-非自立可能 aux 10
12 過ぎ 過ぎる    過ぎる   ['スギ']     VERB    ['上一段-ガ行;連用形-一般'] 動詞-非自立可能 advcl 10
13 て   て      て       ['テ']       SCONJ   []          助詞-接続助詞  mark 10
14 いる いる     居る     ['イル']      VERB    ['上一段-ア行;終止形-一般'] 動詞-非自立可能 fixed 13
"""
