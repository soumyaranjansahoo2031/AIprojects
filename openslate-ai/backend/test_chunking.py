from app.services.partition_service import partition_document
from app.services.chunking_service import chunk_by_title

file_path = "C:\\Users\\Charlie\\AI\\GEN_AI\\capstone_projects\\openslate-ai\\backend\\storage\\projects\\aa7a4e93-2e02-4b36-adba-f93fc7813e3a\\documents\\attention-is-all-you-need.pdf"

elements = partition_document(file_path)
chunks = chunk_by_title(elements)

print("Total elements:", len(elements))
print("Total chunks:", len(chunks))

for chunk in chunks[:5]:
    print("=" * 80)
    print("TITLE:", chunk["title"])
    print("PAGES:", chunk["pages"])
    print("TYPES:", chunk["types"])
    print("CONTENT:", chunk["content"][:500])