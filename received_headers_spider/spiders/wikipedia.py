# -*- coding: utf-8 -*-
import scrapy


class WikipediaSpider(scrapy.Spider):
    name = "wikipedia"
    start_urls = (
        # HTML file
        'https://www.wikipedia.org/',
        # image
        'https://www.wikipedia.org/portal/wikipedia.org/assets/img/Wikipedia-logo-v2@2x.png',
        # huge file
        'http://download.thinkbroadband.com/1GB.zip'
    )

    def parse(self, response):
        self.log('{0}'.format(response))
