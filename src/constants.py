import os
from pathlib import Path

BOT_JOB_ID = "bot_job"
BOT_JOB_SCHEDULE = {"minute": 30}

BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = BASE_DIR / "data"
