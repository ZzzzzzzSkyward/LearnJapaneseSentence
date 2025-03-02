import sl


class CACHE:
    def __init__(self):
        self.cache = {}
        self.name = "cache.json"
        self.dirty = False
        pass

    def get(self, text):
        if text in self.cache:
            return self.cache[text]
        return None

    def set(self, text, trans):
        if not text:
            return
        self.dirty = True
        self.cache[text] = trans

    def load(self):
        self.cache = sl.load(self.name) or self.cache
        self.dirty = False

    def save(self):
        if self.dirty:
            self.dirty = False
            sl.save(self.name, self.cache)
