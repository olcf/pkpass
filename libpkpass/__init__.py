import logging
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level='DEBUG',
    format="%(message)s",
)
