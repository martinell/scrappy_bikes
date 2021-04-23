import scrapy
import json
import re
import datetime

BASE_URL = 'https://www.canyon.com'


class BlogSpider(scrapy.Spider):
    name = 'blogspider'

    start_urls = ['https://www.canyon.com/en-es/outlet/road-bikes/?cgid=outlet-road&prefn1=pc_outlet&prefn2=pc_rahmengroesse&prefv1=true&prefv2=M&srule=sort_price_ascending&start=0'] # noqa
    bikes = []

    def parse(self, response):
        for article in response.css('li.productGrid__listItem'):
            product_link = article.css('a.productTile__link ::attr(href)').extract_first()
            product_data_raw = article.css('div.productTile ::attr(data-gtm-impression)').extract_first()
            product_data = json.loads(product_data_raw)
            product_info = product_data.get("ecommerce", {}).get("impressions", [{}])[0]
            product_info["url"] = BASE_URL + product_link
            #print("PROD: " + json.dumps(product_info, indent=4))

            def _extract_price(name):
                price = article.css(name).extract_first().strip()
                price = price.replace(".", "")
                price = price.replace(",", ".")
                price = re.findall(r"\d+[.]?\d*", price)
                if not price:
                    price = ["0"]
                price = price[0]
                return float(price)

            product_info["price_original"] = _extract_price("span.productTile__productPriceOriginal::text")
            product_info["price_sale"] = _extract_price("span.productTile__productPriceSale::text")

            if product_info["price_sale"] < 1000:
                bike_str = (
                    "{date} ---------------------\n"
                    "   Name:  {name}\n"
                    "   Size:  {size}\n"
                    "   Price: {price_sale} ({price_original})\n"
                    "   Link:  {url}\n"
                )
                print(bike_str.format(
                        date=datetime.datetime.now(),
                        name=product_info.get("name", "???"),
                        size=product_info.get("dimension53", "???"),
                        price_sale=product_info.get("price_sale"),
                        price_original=product_info.get("price_original"),
                        url=product_info.get("url", "???")
                    )
                )
            yield product_info
