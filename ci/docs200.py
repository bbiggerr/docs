import logging
import scrapy

from scrapy import Item, Field
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess

BASE_URL = 'http://localhost:1313/docs/guides/getting-started'

class Docs404Item(Item):
    referer = Field()
    status = Field()
    url = Field()

class Docs404Spider(CrawlSpider):
    name = 'docs404'
    allowed_domains = ['localhost']
    start_urls = ['http://localhost:1313/docs/guides/getting-started']
    handle_httpstatus_list = [200]

    rules = (
        Rule(LinkExtractor(allow=r'/docs/guides', deny=r'/docs/contribute'),
             callback='parse_item', follow=True, ),
    )

    def parse_start_url(self, response):
        return self.parse_item(response)

    def parse_item(self, response):
        item = Docs404Item()

        h1 = response.xpath('//h1').get()
        if '<h1>\n  404\n</h1>' in h1:
            item['referer'] = response.request.headers.get('Referer')
            item['status'] = '404'
            item['url'] = response.url
            yield item
        yield None

if __name__ == "__main__":
    import os
    import sys
    import requests

    #from blueberry import BASE_URL



    process = CrawlerProcess({ 'USER_AGENT': 'docs404',
                               'FEED_URI': 'temp.csv',
                               'FEED_FORMAT': 'csv' })
    process.crawl(Docs404Spider)
    process.start()
    f = open('temp.csv')
    os.remove('temp.csv')

    try:
        requests.get(BASE_URL)
    except requests.exceptions.ConnectionError:
        print('\n\nHugo server not running on port 1313')
        sys.exit(1)

    if sum([1 for line in f]) != 0:
        print('404 response in HTML - see logs')
        sys.exit(1)
    else:
        print('\n\nScraper did not find any 404 links')
