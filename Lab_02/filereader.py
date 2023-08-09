from docx import Document

for paragraph in Document('DockerBasics.docx').paragraphs:
    print(paragraph.text)