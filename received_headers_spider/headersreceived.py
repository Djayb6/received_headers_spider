import logging

from scrapy.http import HtmlResponse
from scrapy.responsetypes import responsetypes
from scrapy import signals

logger = logging.getLogger('scrapy')


class HeadersReceivedExtension(object):

    def __init__(self, settings):
        self._default_maxsize = settings.getint('DOWNLOAD_MAXSIZE')
        self._default_warnsize = settings.getint('DOWNLOAD_WARNSIZE')

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.settings)
        crawler.signals.connect(ext.on_headers_received, signal=signals.headers_received)
        return ext

    def on_headers_received(self, response, request, spider):
        maxsize = getattr(spider, 'download_maxsize', self._default_maxsize)
        maxsize = request.meta.get('download_maxsize', maxsize)

        warnsize = getattr(spider, 'download_warnsize', self._default_maxsize)
        warnsize = request.meta.get('download_warnsize', warnsize)

        expected_size = response.meta.get('expected_size')

        # cancel if expected_size is above maxsize
        if maxsize and expected_size > maxsize:
            error_message = ("Cancelling download of {url}: expected response "
                             "size ({size}) larger than "
                             "download max size ({maxsize})."
                             ).format(url=request.url, size=expected_size, maxsize=maxsize)

            logger.info(error_message)
            return True

        if warnsize and expected_size > warnsize:
            logger.info("Expected response size (%(size)s) larger than "
                           "download warn size (%(warnsize)s).",
                           {'size': expected_size, 'warnsize': warnsize})

        # don't cancel if non-200 request
        if not (200 <= response.status < 300):
            logger.info('response code not between 200 and 300 {0}'.format(response.status))
            return False

        # don't cancel if robots.txt request
        if 'robots.txt' in request.url:
            logger.info('robots.txt request')
            return False

        # cancel if response is not HTML
        if b'Content-Type' in response.headers:
            cls = responsetypes.from_content_type(response.headers[b'Content-Type'])
            return not issubclass(cls, HtmlResponse)

        # else don't cancel
        return False
