from app.db.session import SessionLocal
from app.services.bootstrap import ensure_defaults


def run():
    db = SessionLocal()
    try:
        ensure_defaults(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print("seed complete")
