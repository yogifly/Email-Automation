class Policy:
    def __init__(self):
        self.temperature = 1.0

    def update(self, reward):
        if reward > 0.7:
            self.temperature = max(0.7, self.temperature - 0.05)
        else:
            self.temperature = min(1.2, self.temperature + 0.05)

policy = Policy()
