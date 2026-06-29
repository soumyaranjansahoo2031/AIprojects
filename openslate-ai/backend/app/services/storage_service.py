from pathlib import Path
import shutil


BASE_DIR = Path("storage")
PROJECTS_DIR = BASE_DIR / "projects"


PROJECTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def save_document(
    project_id: str,
    file
):
    project_dir = (
        PROJECTS_DIR /
        project_id /
        "documents"
    )

    project_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        project_dir /
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    return str(file_path)