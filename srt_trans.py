import baidutrans
maxlen = 20


def splitline(text):
    multilines = []
    while len(text) > maxlen:
        _text = text[:maxlen]
        multilines.append(_text)
        text = text[maxlen:]
    if len(text) > 0:
        multilines.append(text)
    return multilines


def trans(text, translated=False):
    while translated is False:
        translated = baidutrans.translate_baidu(text)
    if not translated:
        print('Translation failed')
        translated = ""
    multilines = splitline(text)
    multilines.extend(splitline(translated))
    return '\n'.join(multilines)


buffer = []


def process_translation(text):
    '''
    create a buffer
    '''
    # make sure there is no \n in text
    text = text.replace('\n', '$')
    buffer.append(text)


maxcount = 3000


def get_translations():
    '''
    get the translation from the buffer
    '''
    lines = []
    count = 0
    group = []
    for i in range(len(buffer)):
        line = buffer[i].strip()
        if line == '':
            group.append('@')
            count += 1
        else:
            group.append(line)
            count += len(line)
        if count > maxcount or i == len(buffer)-1:
            text = '\n'.join(group)
            translated = False
            while translated is False:
                translated = baidutrans.translate_baidu(text)
            if not translated:
                print('Translation failed')
                translated = ""
            translated = translated.replace('$', '\n').replace('@', '')
            trg = translated.split('\n')
            lines.extend(trg)
            if len(group) != len(trg):
                print("Error: the number of lines does not match")
                print(text)
                print(translated)
            for i in range(len(translated), len(group)):
                lines.append("<error>")
            count = 0
            group.clear()
    return lines
