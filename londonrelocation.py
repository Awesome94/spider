import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from property import Property


class LondonrelocationSpider(scrapy.Spider):
    name = 'londonrelocation'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url,
                          callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath(
            './/div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            yield Request(url=area_url,
                          callback=self.parse_area_pages)

    def parse_area_pages(self, response):
        # Write your code here and remove `pass` in the following line
        paginated = response.xpath(
            '//div[contains(@class,"pagination-wrap")]//div[contains(@class,"pagination")]/ul//@href').extract()

        for url in paginated[:3]:
            yield Request(url=url, callback=self.extract_data)

    def extract_data(self, response):
        urls = response.xpath(
            './/div[contains(@class,"h4-space")]//h4/a/@href').extract()
        for url in urls:
            abs_url = 'https://londonrelocation.com'+url
            yield Request(url=abs_url, callback=self.get_title_and_rent_value)

    def get_title_and_rent_value(self, response):
        title, url, price = '', '', ''
        title = response.xpath(
            './/div[contains(@class,"content")]//h1/text()')[0].extract()
        url = response.url
        price = response.xpath(
            './/div[contains(@class,"content")]//h3/text()')[0].extract().lower()
        if 'pw' in price:
            price = str(int(price[1:].replace('pw', ''))*4)
        else:
            price = price.split(' ')[0][1:]

        property = ItemLoader(item=Property())
        property.add_value('title', title)
        property.add_value('url', url)
        property.add_value('price', price)
        return property.load_item()
