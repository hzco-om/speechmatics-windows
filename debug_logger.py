import logging, pathlib, sys, datetime
LOG_DIR = pathlib.Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / "last_run.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="w", encoding="utf8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.info("=== New run %s ===", datetime.datetime.now().isoformat(timespec='seconds'))