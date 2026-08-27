import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger.json import JsonFormatter

import configs


LOG_FILE = configs.PORTAL_API_LOG_FILE


class SafeExtraFormatter(logging.Formatter):
    def format(self, record):
        # Add defaults for missing attributes
        for key in ["msisdn", "customer_id", "admin_id"]:
            if not hasattr(record, key):
                setattr(record, key, "-")
        return super().format(record)

file_formatter = SafeExtraFormatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
    "[msisdn=%(msisdn)s customer_id=%(customer_id)s admin_id=%(admin_id)s]"
)

rotating_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=configs.MAX_LOG_BYTES, backupCount=configs.MAX_LOG_BACKUPS
)
rotating_handler.setFormatter(file_formatter)

stream_handler = logging.StreamHandler()
json_formatter = JsonFormatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s"
)
stream_handler.setFormatter(json_formatter)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        rotating_handler,
        stream_handler
    ],
)

logger = logging.getLogger('claims_portal_api')
