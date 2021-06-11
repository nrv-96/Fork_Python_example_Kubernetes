import os
from ccplatlogging.SWALogging import SWALogger

log = SWALogger(__name__)
CCPLAT_LOGGER = log.getLogger()
CCPLAT_LOGGER.setLevel(os.getenv("CCPLAT_LOG_LEVEL", "INFO"))
