#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import FormRequest, Request
from PIL import Image
from StringIO import StringIO
from captcha import crack
from datacrawler.items import BorrowItem, BillItem

import hashlib
import json
import traceback

class NonoSpider(scrapy.Spider):
    name = "nono"
    allowed_domains = ["nonobank.com"]
    max_login_try = 3
    username = ''
    password = ''

    def start_requests(self):
        if hasattr(self, '_login_try'):
            self._login_try += 1
        else:
            self._login_try = 0

        if self._login_try >= self.max_login_try:
            print "Have tried max times (%d)." % self.max_login_try
        else:
            print "Try login %d time..." % (self._login_try + 1)
            return [FormRequest("https://www.nonobank.com/Login/AjaxLogin",
                                dont_filter=True,
                                callback=self   .get_capcha)]

    def get_capcha(self, response):
        return Request('https://www.nonobank.com/Validate/checkCode',
                       dont_filter=True,
                       callback=self.login)

    def handle_capcha(self, response):
        img = Image.open(StringIO(response.body))
        captcha = crack(img)
        print "cracked capcha: " + captcha
        return captcha

    def login(self, response):
        return FormRequest("https://www.nonobank.com/Login/AjaxLogin", formdata={
            'loginname': self.username,
            'loginpwd': hashlib.md5(self.password).hexdigest(),
            'checkCode': self.handle_capcha(response),
            'rememberme': ''
        }, dont_filter=True, callback=self.handle_login)

    def handle_login(self, response):
        try:
            res = json.loads(response.body)
            if res.get('result') != 1:
                print res.get('msg') or 'login failed.'
                start_requests = self.start_requests()
                if start_requests:
                    for r in start_requests:
                        yield r
            else:
                print "login succeed!"
                yield Request('https://www.nonobank.com/AccountBorrow/BorrowList', callback=self.handle_borrows)
                yield Request('https://www.nonobank.com/AccountBorrow/Bills', callback=self.handle_bills)

        except:
            traceback.print_exc()

    def handle_borrows(self, response):
        """
        @url file:///Users/Revir/Temp/borrows.html
        """
        for i, tr in enumerate(response.xpath('//div[@class="myaccound_list"]/table//tr')):
            if i == 0:
                continue
            item = BorrowItem()
            item['numb'] = tr.xpath('td[1]/text()').re_first(u'【(\w+)】')
            item['title'] = tr.xpath('td[1]/a/@title').extract_first()
            item['amount'] = float(tr.xpath('td[2]/text()').re_first(u'(\d.*)').replace(',', ''))
            item['rate'] = tr.xpath('td[3]/text()').extract_first()
            item['borrow_date'] = tr.xpath('td[4]/text()').extract_first()
            item['pay_amount'] = float(tr.xpath('td[5]/text()').re_first(u'(\d.*)').replace(',', ''))
            item['paid_periods'] = tr.xpath('td[6]/text()').extract_first()
            item['status'] = tr.xpath('td[7]/text()').extract_first().strip()
            # print item
            yield item

    def handle_bills(self, response):
        """
        @url file:///Users/Revir/Temp/bills.html
        """
        for i, tr in enumerate(response.xpath('//div[@class="bill_list"]/table//tr')):
            if i % 3 == 0:
                item = BillItem()
                item['paid_date'] = tr.xpath('.//div[@class="time"]/text()').re_first(u'还款日：(.*)')
                item['paid_periods'] = tr.xpath('.//div[@class="sort"]/text()').re_first(u'【(.*)】')
                item['status'] = tr.xpath('.//div[@class="button"]/input/@value').extract_first()
            elif i % 3 == 1:
                item['title'] = tr.xpath('td[1]/a/@title').extract_first()
                item['paid_amount'] = float(tr.xpath('td[2]/text()').re_first(u'(\d.*)').replace(',', ''))
                item['paid_interest'] = float(tr.xpath('td[3]/text()').re_first(u'(\d.*)').replace(',', ''))
                item['paid_punishment'] = float(tr.xpath('td[4]/text()').re_first(u'(\d.*)').replace(',', ''))
                item['paid_total'] = item['paid_amount'] + item['paid_interest'] + item['paid_punishment']
                # print item
                yield item

        for link in response.xpath('//div[@class="pager"]//td/a'):
            text = link.extract()
            if u'下一页' in text:
                href = link.xpath('./@href').extract_first()
                url = response.urljoin(href)
                print url
                yield scrapy.Request(url, callback=self.handle_bills)
