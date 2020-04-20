class Bundle(object):
    def __init__(self):
        self.payload = {}

    def __len__(self):
        return len(self.payload.keys())

    def put(self, itemType, item):
        self.payload[itemType] = item

    def get(self, itemType):
        return self.payload.get(itemType, None)

    def has(self, itemType):
        return itemType in self.payload.keys()
