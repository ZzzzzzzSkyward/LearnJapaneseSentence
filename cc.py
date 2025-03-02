import opencc

cc = opencc.OpenCC("t2s")


def to_chs(text):
    if text == "":
        return text
    return cc.convert(text)
