class Blackboard:
    """
    Blackboard for global configuration
    """

    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key, None)

    def set(self, key, value):
        self.data[key] = value

    def update(self, data):
        self.data.update(data)

    def clear(self):
        self.data.clear()
