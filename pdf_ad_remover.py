import fitz  # PyMuPDF
import os

# Dentro de una carpeta metes los archivos con anuncios.
# Puedes limpiar cualquier cantidad de archivos (pdf).
# Los archivos sin anuncios no llevan "wuolah-free" delante.

# Especificar la dirección de la carpeta (importante "/" del final)
path = "C:/Users/name/Downloads/Apuntes/"
dir_list = os.listdir(path)

# Eliminar la zona de frases con links
txt = fitz.Rect(0.0, 799.489501953125, 567.5390014648438, 831.964599609375)

# Frases que aparecen en los bordes
text_to_remove = ["""Reservados todos los derechos.
     No se permite la explotación económica ni la transformación de esta obra.
     Queda permitida la impresión en su totalidad."""]

for i in range(len(dir_list)):

    pdf_file = path + dir_list[i]
    if pdf_file[-3:] != 'pdf' or dir_list[i][0:11] != 'wuolah-free':
        continue

    # Si un archivo ya se limpió previamente, no lo vuelve a limpiar.
    if dir_list[i][12:] in dir_list:
        print(f"File {dir_list[i]} already cleaned.")
        continue

    pdf_path = pdf_file
    doc = fitz.open(pdf_path)
    if len(doc) > 3:
        doc.delete_pages([0, 3, 4])
    else:
        doc.delete_pages([0])

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Eliminar los links de los anuncios
        links = page.get_links()

        if links:
            for link in links:
                if link['from'] == txt:
                    page.add_redact_annot(link['from'], fill=False)
                else:
                    page.delete_link(link)

        # Eliminar los textos adicionales
        for text in text_to_remove:
            text_instances = page.search_for(text)
            if text_instances:
                for rect in text_instances:
                    page.add_redact_annot(rect, fill=False)
            page.apply_redactions()

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Eliminar los banners y la marca de agua de Wuolah
        image_list = page.get_images(full=True)
        for img_index, image in enumerate(image_list):
            xref = image[0]

            # Dimensiones de los banners
            ad_dims = [(395, 72), (1246, 218), (147, 1538), (974, 251)]
            dims = (image[2], image[3])
            if dims in ad_dims:
                page.delete_image(xref)

    # Reescalado de las páginas con banners ya eliminados
    for page_num in range(len(doc)):
        if page_num == 0 or page_num % 3 == 0:
            page = doc[page_num]
            original = page.mediabox
            page.set_cropbox(fitz.Rect(73.90355935, 104.52, 595.28, 841.89))

    # Crear el PDF ya limpio
    src = fitz.open()
    for page_num in range(len(doc)):
        page = doc[page_num]
        w, h = page.rect.br
        if page_num == 0 or page_num % 3 == 0:
            factor = 1.141747017
            newpage = src.new_page(width=factor*w, height=factor*h)
            newpage.show_pdf_page(newpage.rect, doc, page.number)
        else:
            newpage = src.new_page(width=w, height=h)
            newpage.show_pdf_page(newpage.rect, doc, page.number)

    src.ez_save(path + dir_list[i][12:])
    doc.close()
