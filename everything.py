# 导入EveryTools类
from everytools import EveryTools

es = EveryTools()  # 实例化，只需要第一次就行


class SORT_TYPE:
    名称升序 = 1
    名称降序 = 2
    路径升序 = 3
    路径降序 = 4
    大小升序 = 5
    大小降序 = 6
    拓展升序 = 7
    拓展降序 = 8


def everything(pattern, sort_type=SORT_TYPE.路径升序, max_num=None):
    # print(pattern)
    es.search(pattern)
    results = es.results(sort_type=sort_type, max_num=max_num)
    return results.values


def search_ext(ext, directory=None):
    if not ext.startswith("*"):
        ext = f"*.{ext}"
    if directory:
        if not directory.endswith("\\"):
            directory = directory + "\\"
        directory = directory.replace("/", "\\")
        ext = f"{directory} {ext}"
    results = everything(ext)
    ret = []
    for i in results:
        ret.append(f"{i[1]}/{i[0]}")
    return ret


def search(pattern):
    print(pattern)
    results = everything(pattern)
    ret = []
    for i in results:
        ret.append(f"{i[1]}/{i[0]}")
    return ret


if __name__ == "__main__":
    print(search_ext("ass")[-1])
