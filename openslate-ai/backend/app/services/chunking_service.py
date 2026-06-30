def is_noise(text: str) -> bool:
    text = text.strip()

    if len(text) < 8:
        return True

    noisy_patterns = [
        "arxiv",
        "provided proper attribution",
        "] L C . s c [",
        "v i X r a",
    ]

    lower_text = text.lower()

    for pattern in noisy_patterns:
        if pattern.lower() in lower_text:
            return True

    words = text.split()

    if len(words) > 4:
        one_char_count = sum(1 for word in words if len(word) == 1)
        if one_char_count / len(words) > 0.5:
            return True

    return False


def is_real_title(text: str) -> bool:
    text = text.strip()

    if is_noise(text):
        return False

    if len(text) > 120:
        return False

    section_keywords = [
        "abstract",
        "introduction",
        "background",
        "model",
        "architecture",
        "attention",
        "training",
        "results",
        "evaluation",
        "experiments",
        "conclusion",
        "references",
        "appendix",
        "acknowledgements",
    ]

    lower_text = text.lower()

    if any(keyword in lower_text for keyword in section_keywords):
        return True

    if lower_text[:2].isdigit():
        return True

    if text.istitle() and len(text.split()) <= 8:
        return True

    return False


def chunk_by_title(elements: list[dict]) -> list[dict]:
    chunks = []
    current_title = "Document Start"
    current_content = []
    current_pages = set()
    current_types = set()

    for element in elements:
        element_type = element.get("type")
        text = element.get("text", "").strip()
        metadata = element.get("metadata", {})

        if not text or is_noise(text):
            continue

        page_number = metadata.get("page_number")

        if element_type == "Title" and is_real_title(text):
            if current_content:
                chunks.append({
                    "title": current_title,
                    "content": "\n".join(current_content),
                    "pages": sorted(list(current_pages)),
                    "types": sorted(list(current_types)),
                })

            current_title = text
            current_content = [text]
            current_pages = set()
            current_types = {"Title"}

            if page_number:
                current_pages.add(page_number)

        else:
            current_content.append(text)
            current_types.add(element_type)

            if page_number:
                current_pages.add(page_number)

    if current_content:
        chunks.append({
            "title": current_title,
            "content": "\n".join(current_content),
            "pages": sorted(list(current_pages)),
            "types": sorted(list(current_types)),
        })

    return chunks