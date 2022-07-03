class ParseResult:
    def __init__(self):
        self.to_reverse_count = 0
        self.error = None
        self.node = None
        self.advancements = 0

    def register_advancement(self):
        self.advancements += 1

    def register(self, res):
        self.advancements += res.advancements
        if res.error:
            self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advancements
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advancements == 0:
            self.error = error
        return self
