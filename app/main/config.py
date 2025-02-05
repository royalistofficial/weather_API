import logging
import openmeteo_requests
import requests_cache
from retry_requests import retry


def setup_logging():
    logging.basicConfig(
        filename='app.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


cache_session = requests_cache.CachedSession('.cache', expire_after=15 * 60)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
