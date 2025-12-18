class BaseOcrModel:
    def __init__(self):
        pass

    def process(self, image):
        raise NotImplementedError("Subclasses must implement this method")
    def start(self):
        pass
    def delete(self):
        pass