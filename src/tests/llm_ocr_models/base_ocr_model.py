from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import wraps

def timeout(seconds=300, default=""):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(fn, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except TimeoutError:
                    print("Function call timed out")
                    return default
        return wrapper
    return decorator


class BaseOcrModel:
    def __init__(self):
        self.model = None
        self.processor = None

    def process(self, image):
        raise NotImplementedError("Subclasses must implement this method")
    def start(self):
        pass
    def delete(self):
        pass