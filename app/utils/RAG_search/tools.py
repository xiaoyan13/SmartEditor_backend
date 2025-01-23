def split_document_by_paragraph(text: str):
    """
      convert a document string into list based on paragraphs
    """
    paragraphs = text.strip().split('\n')
    paragraphs = [para.strip() for para in paragraphs if para.strip()]
    return paragraphs
