from src.scripts.pdf_loader import make_pdf_dataset
from src.scripts.utils.ask_a_model import query_model



def main():

    pdf_path = "F:/Documentos/git/automaton_1/data/pdfs"
    images = make_pdf_dataset(pdf_path)

    for image, url in images:
        response = query_model(image, "Cual es el valor total de la factura?")
        print(response)
        break

if __name__ == "__main__":
    main()