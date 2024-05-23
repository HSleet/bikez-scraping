import scrapy


class MotorcyclesSpider(scrapy.Spider):
    name = "motorcycles"
    allowed_domains = ["bikez.com"]
    start_urls = ["https://bikez.com"]

    def parse(self, response):
        pass
