from datetime import datetime, timedelta, timezone


def get_current_datetime() -> datetime:
    return datetime.now(timezone(timedelta(hours=9)))
