from app.services.partition_service import partition_document

file_path = "C:\\Users\\Charlie\\AI\\GEN_AI\\capstone_projects\\openslate-ai\\backend\\storage\\projects\\1b6ad117-bbd6-4fc1-b735-af7a1bd48466\\documents\\Soumya_Ranjan_Sahoo_Software_Developer_Resume_36.pdf"

elements = partition_document(file_path)

print("Total elements:", len(elements))

for element in elements[:10]:
    print(element["type"], "=>", element["text"][:100])