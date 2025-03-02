import json
import re
import xml.etree.ElementTree as ET


def is_katakana(reb):
    # 去掉片假名中的・
    if '・' in reb:
        return False
    # 判断reb是否为片假名，包含英文字母、数字和片假名
    katakana_regex = r'^[A-Za-z0-9\u30a0-\u30ff]+$'
    return bool(re.fullmatch(katakana_regex, reb))


def main():
    # 加载 JMDict 文件
    tree = ET.parse('z:/JMdict.xml')
    root = tree.getroot()

    jp_en_dict = {}  # 用于存储结果的字典

    for entry in root.findall('entry'):
        # 检查条目中是否有<k_ele>标签
        k_eles = entry.findall('k_ele')
        if k_eles:
            continue  # 如果存在<k_ele>，跳过

        r_eles = entry.findall('r_ele')
        if not r_eles:
            continue  # 如果不存在<r_ele>，跳过

        # 遍历所有<r_ele>
        for r_ele in r_eles:
            reb = r_ele.find('reb')
            if reb is None:
                continue  # 跳过没有reb的<r_ele>

            reb_text = reb.text.strip()
            # 判断reb是否符合条件
            if is_katakana(reb_text):
                # 提取sense中的gloss内容
                sense_list = []
                senses = entry.findall('sense')
                for sense in senses:
                    gloss = sense.find('gloss')
                    if gloss is not None:
                        sense_list.append(gloss.text.strip())
                # 合并所有sense的gloss内容，每个取第一个，可能有多个sense
                merged_gloss = '; '.join(sense_list)
                if merged_gloss:
                    # 将结果存入字典
                    if reb_text in jp_en_dict:
                        # 如果已存在，则覆盖或合并？这里覆盖
                        jp_en_dict[reb_text] = merged_gloss
                    else:
                        jp_en_dict[reb_text] = merged_gloss

    # 保存为json文件
    with open('z:/jp_en.json', 'w', encoding='utf-8') as f:
        json.dump(jp_en_dict, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
