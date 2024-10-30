import json
from pathlib import Path

from app.main import app

ROOT_DIR = Path(__file__).parent.parent.parent

if __name__ == "__main__":
    openapi_schema = app.openapi()

    with open(ROOT_DIR / "openapi.json", "w", encoding="utf-8") as file:
        json.dump(openapi_schema, file)
