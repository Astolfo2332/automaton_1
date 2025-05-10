from PIL import Image
from src.scripts.utils.ask_a_model import query_model
from src.scripts.utils.prompts.prompts import *

def make_all_queries(image: Image, query: str, url:str) -> dict:
