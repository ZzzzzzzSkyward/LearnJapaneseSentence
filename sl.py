'''
Save and load
'''
import zipfile
import os
import simplejson as json


def jsondump(data, pretty=False):
    return json.dumps(data, ensure_ascii=False, sort_keys=pretty, indent=2 if pretty else None, check_circular=False)


def jsonload(data):
    try:
        return json.loads(data)
    except:
        return None


def save_json(name, data, pretty=False):
    with open(name, "w", encoding="utf-8") as f:
        f.write(jsondump(data, pretty))


def load_json(name):
    if not os.path.exists(name):
        return None
    with open(name, "r", encoding="utf-8") as f:
        try:
            s = f.read()
            return jsonload(s)
        except:
            return None


def save(name, data, *args, **kwargs):
    if not name.endswith(".json"):
        name = name + ".json"
    save_json(name, data, *args, **kwargs)


def load(name):
    if not name.endswith(".json"):
        name = name + ".json"
    return load_json(name)


encodings = ["utf-8-sig", "utf-8", "gbk", "gb2312", "utf-16"]


def readstr(name):
    for encoding in encodings:
        try:
            with open(name, "r", encoding=encoding) as f:
                return f.read()
        except:
            pass
    raise Exception("Cannot read file: " + name)


def writestr(name, data):
    if type(data) == list:
        data = '\n'.join(data)
    try:
        with open(name, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception as e:
        raise e


def writelist(name, data, sep=','):
    '''
    input: a list[list]
    '''
    with open(name, "w", encoding="utf-8") as f:
        firstflag = True
        for i in data:
            if firstflag:
                firstflag = False
            else:
                f.write('\n')
            if isinstance(i, list) or isinstance(i, tuple):
                innerflag = True
                for j in i:
                    if innerflag:
                        innerflag = False
                    else:
                        f.write(sep)
                    f.write(str(j))
            else:
                f.write(i)


def load_zip(zipname, name):
    with zipfile.ZipFile(zipname, 'r') as zf:
        return zf.open(name).read().decode('utf-8')


def load_json_zip(zipname, name):
    with zipfile.ZipFile(zipname, 'r') as zf:
        d = zf.open(name).read().decode('utf-8')
        return jsonload(d)


def save_zip(zipname, name, data):
    with zipfile.ZipFile(zipname, 'a', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(name, data)


def save_json_zip(zipname, name, data):
    with zipfile.ZipFile(zipname, 'a', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(name, jsondump(data))
