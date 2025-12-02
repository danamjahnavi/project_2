import os
from pathlib import Path
from dotenv import load_dotenv

# ========== DEBUG PRINTS ==========
print("🔍 Loading .env ...")

ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"
print(f"📌 Expecting .env here: {ENV_PATH}")

if ENV_PATH.exists():
    print("✅ .env file exists — loading it now")
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print("❌ .env NOT found at expected path!")

print("🧪 Debug: POSTGRES_HOST loaded as:", os.getenv("POSTGRES_HOST"))
# ==================================

def get_db_url():
    user = os.getenv("POSTGRES_USERNAME")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DATABASE")
    print("🔁 DB URL Built:", f"postgresql://{user}:{password}@{host}:{port}/{db}")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"
