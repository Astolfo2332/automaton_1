import os
from pdf2image import convert_from_path
from PIL import Image

SERVER = "http://192.168.0.106:8000/data/pdfs/"

class BytesImageDataset:
    def __init__(self, image_bytes_list, transform=None):
        self.image_bytes_list = image_bytes_list
        self.transform = transform

    def __len__(self):
        return len(self.image_bytes_list)

    def __getitem__(self, idx):
        img = self.image_bytes_list[idx].convert("RGB")

        if self.transform:
            img = self.transform(img)

        return img


def merge_images_vertically(images):
    widths, heights = zip(*(img.size for img in images))

    max_width = max(widths)
    total_height = sum(heights)

    merged_img = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    for img in images:
        merged_img.paste(img, (0, y_offset))
        y_offset += img.height

    return merged_img



def convert_pdf_to_images(pdf_path:str) -> list:
    images = []

    # Convert PDF to images
    for file in os.listdir(pdf_path):
        if file.endswith('.pdf'):
            image = convert_from_path(os.path.join(pdf_path, file), thread_count=32)
            images.append((merge_images_vertically(image), SERVER + os.path.basename(file)))
            images[0].show()
            break

    return images

def make_pdf_dataset(pdf_path:str) -> BytesImageDataset:
    print("[INFO] Loading PDF files from path:", pdf_path)

    images = convert_pdf_to_images(pdf_path)
    dataset = BytesImageDataset(images)
    print("[INFO] PDF files loaded successfully.")

    return dataset

if __name__ == "__main__":

    pdf_path = "F:/Documentos/git/automaton_1/data/pdfs"
    images = make_pdf_dataset(pdf_path)

    for image in images:
        break
