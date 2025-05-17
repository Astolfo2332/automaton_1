import os
import zipfile

def extract_zip(zip_path: str, extract_to: str) -> None:
    if not zipfile.is_zipfile(zip_path):
        return

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


if __name__ == "__main__":
    main = os.getcwd().split("src")[0]
    zip_files = os.listdir(os.path.join(main, "data", "zips"))

    os.makedirs(os.path.join(main, "data", "extracted"), exist_ok=True)
    [extract_zip(os.path.join(main, "data", "zips", file), os.path.join(main, "data", "extracted")) for file in zip_files]