#!/usr/bin/env python
# coding=utf-8

import scrapy
import mysql
import simplejson as json
import re
from const import DB_CONFIG
import MySQLdb
import const
from scrapy.selector import Selector
import sys

reload(sys)
sys.setdefaultencoding("utf8")

class BbsSpider(scrapy.Spider):
    name = 'bbs';
    start_urls = const.ALLOW_DOMAINS;
    headers = const.HEADERS;
    db = None;
    start_urls = [];
    art_url_pat = r'article/';
    auart_url_pat = r'board/';

    def parse(self, response):
        cur_page_url = response._get_url();
        #print response.body_as_unicode();
        print 'cur url is [%s]' % cur_page_url;
        if re.search(self.auart_url_pat, cur_page_url, re.I):
            return self.parse_art_list(response);
        elif re.search(self.art_url_pat, cur_page_url, re.I):
            return self.parse_art_cont(response);
            pass;
        else:
            print 'pass this page';
            pass;

    def parse_art_list(self, response):
        cur_page_url = response._get_url();
        print 'this page [%s] is board art list' % cur_page_url;
        #print response.body_as_unicode();
        sel_auart = response.css('div.b-content tbody tr');
        sel_auart_a = sel_auart.css('td.title_9 >a');
        auart_url = sel_auart_a.css('::attr(href)').extract();
        auart_title = sel_auart_a.css('::text').extract();
        auart_time = sel_auart.css('td.title_10::text').extract();
        auart_au = sel_auart.css('td.title_12 >a::text').extract();
        auart_hot = sel_auart.css('td.title_11::text').extract();

        sel_page = response.css('ul.pagination li ol');
        cur_page_num = sel_page.css('li.page-select > a::text').extract();
        page_list_num = sel_page.css('li.page-normal > a::text').extract();
        page_list_url = sel_page.css('li.page-normal > a::attr(href)').extract();

        for idx, u in enumerate(auart_url):
            #print '%d,%s,%s,%s,%s,%s' %(idx, auart_url[idx], auart_title[idx], auart_time[idx], auart_au[idx], auart_hot[idx]);
            next_url = response.urljoin(auart_url[idx]);
            self.store_data({'uptime': auart_time[idx], 'hot': auart_hot[idx],
                    'title': auart_title[idx], 'author': auart_au[idx],
                    'url': next_url, 'table': 'auart'});
            print 'crawl article [%s]' % next_url;
            yield scrapy.Request(next_url, meta={'cookiejar':response.meta['cookiejar']},headers=self.headers, callback=self.parse);

        #crawl next page list for cur page, easy management
        #xpath delete charters >>, so pre page text is null
        print 'cur page is %s' % cur_page_num[0];
        if len(page_list_url) > len(page_list_num):
            pre_page_num = '%d' % (int(cur_page_num[0])-1);
            page_list_num.insert(0, pre_page_num);
        for idx, num in enumerate(page_list_num):
            #print '%d,%s,%s' %(idx, page_list_num[idx], page_list_url[idx]);
            if page_list_num[idx] == '>>':
                next_url = response.urljoin(page_list_url[idx]);
                print 'crawl next page [%s]' % next_url;
                yield scrapy.Request(next_url, meta={'cookiejar':response.meta['cookiejar']},headers=self.headers, callback=self.parse);

    def parse_art_cont(self, response):
        cur_page_url = response._get_url();
        print 'this page [%s] is article' % cur_page_url;
        #print response.body_as_unicode();
        text = response.css('div.b-content table.article div.a-content-wrap ::text').extract();
        text = ' '.join(text);
        text = text.encode('utf8');
        self.store_data({'text': text, 'url': cur_page_url.encode('utf8'), 'table': 'art'});
        ##
        sel_page = response.css('div.t-pre ul.pagination li ol');
        cur_page_num = sel_page.css('li.page-select > a::text').extract();
        page_list_num = sel_page.css('li.page-normal > a::text').extract();
        page_list_url = sel_page.css('li.page-normal > a::attr(href)').extract();
        print 'cur page is %s' % cur_page_num[0];
        if len(page_list_url) > len(page_list_num):
            pre_page_num = '%d' % (int(cur_page_num[0])-1);
            page_list_num.insert(0, pre_page_num);
        for idx, num in enumerate(page_list_num):
            #print '%d,%s,%s' %(idx, page_list_num[idx], page_list_url[idx]);
            if page_list_num[idx] == '>>':
                next_url = response.urljoin(page_list_url[idx]);
                print 'crawl next article page [%s]' % next_url;
                yield scrapy.Request(next_url, meta={'cookiejar':response.meta['cookiejar']},headers=self.headers, callback=self.parse);

    def done(self, response):
        print "done";
        pass;

    def store_data(self, data):
        if data['table'] == 'auart':
            sql = "insert into auart(uptime, hot, author, title, url) values ('%s',%s,'%s','%s','%s')" % (
                    data['uptime'], data['hot'], MySQLdb.escape_string(data['author']),
                    MySQLdb.escape_string(data['title']), MySQLdb.escape_string(data['url']));
        else:
            sql = "insert into art(url,text) values ('%s', '%s')" % (
                    MySQLdb.escape_string(data['url']), MySQLdb.escape_string(data['text']));
        #print 'sql is [%s]' % sql;
        try:
            self.db.update(sql);
        except:
            print 'update failed';
        pass;

    def start_requests(self):
        self.db = mysql.MySQL(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['passwd'], DB_CONFIG['db'], DB_CONFIG['port'], DB_CONFIG['charset'], DB_CONFIG['timeout'], '');
        return [scrapy.FormRequest("http://bbs.byr.cn/user/ajax_login.json",
                formdata = const.LOGIN_DATA,
                meta = {'cookiejar':1},
                headers = self.headers,
                callback=self.logged_in)];

    def logged_in(self, response):
        self.cookiejar = response.meta['cookiejar'];
        self.start_urls = self.load_start_url();
        for url in self.start_urls:
            yield scrapy.Request(url,meta={'cookiejar':response.meta['cookiejar']},headers=self.headers, callback=self.parse)

    def load_start_url(self):
        sql = 'select url from sect limit 170,20';
        rows = self.db.query(sql);
        for row in rows:
            yield const.URL + row[0];

