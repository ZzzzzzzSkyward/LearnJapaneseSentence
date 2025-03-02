'''
Convert romaji to japanese
'''
import pygtrie
import sl
romanji_jp_dict = sl.load_json("front/public/romaji_jp.jsond")
jp_romanji_dict = {v: k for k, v in romanji_jp_dict.items()}
romanji_trie = pygtrie.CharTrie(romanji_jp_dict)


def romaji_to_japanese(romaji):
    words = []
    while romaji:
        prefix = list(romanji_trie.prefixes(romaji))
        if len(prefix) > 0:
            r, w = prefix[-1]
            words.append(w)
            romaji = romaji[len(r):]
        else:
            w = romaji[0]
            words.append(w)
            romaji = romaji[1:]
    return "".join(words)


if __name__ == "__main__":
    hira = romaji_to_japanese("watashiwagakuseideshou")
    print(hira)
    mixed = romaji_to_japanese("私 wa gakusei deshou")
    print(mixed)
