import os.path
from loguru import logger

# Row below removes default logger, that writes to stdout
# logger.remove()

project_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
)
log_dir = "log"
logger.add(
    os.path.join(project_dir, log_dir, "{time:YYYY-MM-DD}.log"),
    rotation="00:00",
    retention="7 days",
    level="WARNING",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    diagnose=False
)