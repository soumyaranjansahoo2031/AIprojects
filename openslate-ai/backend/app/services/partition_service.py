from unstructured.partition.pdf import partition_pdf


def partition_document(file_path: str) -> list[dict]:
    elements = partition_pdf(
        filename=file_path,
        strategy="fast",
        infer_table_structure=True,
        languages=["eng"],
    )

    parsed_elements = []

    for element in elements:
        parsed_elements.append({
            "type": element.category,
            "text": str(element),
            "metadata": element.metadata.to_dict()
        })

    return parsed_elements