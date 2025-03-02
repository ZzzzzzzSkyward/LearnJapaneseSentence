'''
Convert Chinese word to Japanese word
'''
import sl
# https://github.com/beyondacm/CN2JP-Translator
chs_jp_dict: dict = sl.load_json("chs_jp.jsond")


class JAPANESE_WORD:
    @staticmethod
    def to_jp(char):
        if char in chs_jp_dict:
            return chs_jp_dict[char][0]
        return char

    @staticmethod
    def chinese_to_japanese(text):
        ret = []
        for i in text:
            ret.append(JAPANESE_WORD.to_jp(i))
        return "".join(ret)

    @staticmethod
    def has_japanese(text):
        for i in text:
            if JAPANESE_WORD.is_katakana_single(i) or JAPANESE_WORD.is_hiragana_single(i):
                return True
        return False

    @staticmethod
    def is_hiragana(text):
        '''
        判断是否是平假名
        '''
        for i in text:
            if not (0x3041 <= ord(i) <= 0x309F):
                return False
        return True

    @staticmethod
    def is_japanese(text):
        for i in text:
            if not (JAPANESE_WORD.is_hiragana_single(i) or JAPANESE_WORD.is_katakana_single(i) or JAPANESE_WORD.is_kanji_single(i) or JAPANESE_WORD.is_punctuation_single(i)):
                return False
        return True

    @staticmethod
    def is_katakana(text):
        '''
        判断是否是片假名
        '''
        for i in text:
            if not (0x30a1 <= ord(i) <= 0x30f7):
                return False
        return True

    @staticmethod
    def is_kanji(text):
        '''
        判断是否是汉字
        '''
        for i in text:
            if not JAPANESE_WORD.is_chinese_single(i):
                return False
        return True

    @staticmethod
    def is_hiragana_single(char):
        return 0x3041 <= ord(char) <= 0x309F

    @staticmethod
    def is_punctuation_single(char):
        return (0x30fb <= ord(char) <= 0x30fe) or char in JAPANESE_WORD.punctuations
    punctuations = {i: True for i in set('。·《》「」『』')}

    @staticmethod
    def is_katakana_single(char):
        return 0x30a1 <= ord(char) <= 0x30f7

    @staticmethod
    def is_kanji_single(char):
        return 0x4e00 <= ord(char) <= 0x9fa5

    @staticmethod
    def is_chinese_single(uchar):
        """
        :param uchar: input char in unicode
        :return: whether the input char is a Chinese character.
        """
        if uchar >= u'\u3400' and uchar <= u'\u4db5':  # CJK Unified Ideographs Extension A, release 3.0
            return True
        elif uchar >= u'\u4e00' and uchar <= u'\u9fa5':  # CJK Unified Ideographs, release 1.1
            return True
        elif uchar >= u'\u9fa6' and uchar <= u'\u9fbb':  # CJK Unified Ideographs, release 4.1
            return True
        elif uchar >= u'\uf900' and uchar <= u'\ufa2d':  # CJK Compatibility Ideographs, release 1.1
            return True
        elif uchar >= u'\ufa30' and uchar <= u'\ufa6a':  # CJK Compatibility Ideographs, release 3.2
            return True
        elif uchar >= u'\ufa70' and uchar <= u'\ufad9':  # CJK Compatibility Ideographs, release 4.1
            return True
        elif uchar >= u'\u20000' and uchar <= u'\u2a6d6':  # CJK Unified Ideographs Extension B, release 3.1
            return True
        elif uchar >= u'\u2f800' and uchar <= u'\u2fa1d':  # CJK Compatibility Supplement, release 3.1
            return True
        # Full width ASCII, full width of English punctuation, half width Katakana, half wide half width kana, Korean alphabet
        elif uchar >= u'\uff00' and uchar <= u'\uffef':
            return True
        elif uchar >= u'\u2e80' and uchar <= u'\u2eff':  # CJK Radicals Supplement
            return True
        elif uchar >= u'\u3000' and uchar <= u'\u303f':  # CJK punctuation mark
            return True
        elif uchar >= u'\u31c0' and uchar <= u'\u31ef':  # CJK stroke
            return True
        elif uchar >= u'\u2f00' and uchar <= u'\u2fdf':  # Kangxi Radicals
            return True
        elif uchar >= u'\u2ff0' and uchar <= u'\u2fff':  # Chinese character structure
            return True
        elif uchar >= u'\u3100' and uchar <= u'\u312f':  # Phonetic symbols
            return True
        # Phonetic symbols (Taiwanese and Hakka expansion)
        elif uchar >= u'\u31a0' and uchar <= u'\u31bf':
            return True
        elif uchar >= u'\ufe10' and uchar <= u'\ufe1f':
            return True
        elif uchar >= u'\ufe30' and uchar <= u'\ufe4f':
            return True
        elif uchar >= u'\u2600' and uchar <= u'\u26ff':
            return True
        elif uchar >= u'\u2700' and uchar <= u'\u27bf':
            return True
        elif uchar >= u'\u3200' and uchar <= u'\u32ff':
            return True
        elif uchar >= u'\u3300' and uchar <= u'\u33ff':
            return True

        return False
