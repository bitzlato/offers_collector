import logging
import pathlib
from logging.handlers import RotatingFileHandler

log_dir = pathlib.Path(__file__).parent.parent / 'logs'
log_maxBytes = 30 * 1024 * 1024
log_backupCount = 3

if not log_dir.exists():
    log_dir.mkdir()


def setup_logging(is_debug: bool = False):
    handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(log_dir / 'liquidator_bot.log', maxBytes=log_maxBytes, backupCount=log_backupCount),
    ]

    logging.basicConfig(format='%(asctime)-15s %(threadName)s %(levelname)-8s %(message)s',
                        level=(logging.DEBUG if is_debug else logging.INFO), handlers=handlers)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.INFO)

    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.INFO)
