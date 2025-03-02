import sl


class FREQ:
    def __init__(self):
        pass

    def load_json(self, name):
        data = sl.load_json(name)
        if not data:
            print(name, "not found")
            return
        self.data = data

    def print(self):
        for i in self.data:
            print(i["headword"])


if __name__ == "__main__":
    f = FREQ()
    test = [
        "250adv.json",
        "500adj.json",
        "1000.json",
        "2000.json",
        "2000v.json",
        "3000.json",
        "adjj.json",
    ]
    for i in test:
        print(i)
        f.load_json(i)
        f.print()
