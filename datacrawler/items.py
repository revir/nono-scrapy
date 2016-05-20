# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BorrowItem(scrapy.Item):
    numb = scrapy.Field()
    title = scrapy.Field()
    amount = scrapy.Field()
    rate = scrapy.Field()
    borrow_date = scrapy.Field()
    pay_amount = scrapy.Field()
    paid_periods = scrapy.Field()
    status = scrapy.Field()

class BillItem(scrapy.Item):
    title = scrapy.Field()
    paid_periods = scrapy.Field()
    paid_date = scrapy.Field()
    paid_amount = scrapy.Field()
    paid_interest = scrapy.Field()
    paid_punishment = scrapy.Field()
    paid_total = scrapy.Field()
    status = scrapy.Field()
