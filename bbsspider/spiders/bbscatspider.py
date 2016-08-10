#!/usr/bin/env python
# coding=utf-8

import scrapy
import mysql
import simplejson as json
import re
import const
from const import DB_CONFIG
import MySQLdb

class BbsCatSpider(scrapy.Spider):
    name = 'bbscat';
    allowd_domains = const.ALLOW_DOMAINS;
    cookiejar = {};
    pat = r'href="(/\w+/\w+)" title="(.*)"\s*>';
    headers = const.HEADERS;
    db = None;
    start_urls = ['http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-0', 
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-1',
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-2',
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-3',
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-4',
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-5',
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-6',
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-7',
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-8',
                    'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-9'];
    
    def parse(self, response):
        body = response.body_as_unicode();
        try:
            data = json.loads(body.encode('utf8'));
            for panel in data:
                ma = re.search(self.pat, panel['t'], re.I);
                url = ma.group(1);
                title = ma.group(2);
                print 'url [%s], title [%s]' %(url, title);
                if panel.has_key('id'):
                    print 'current data is new url sec';
                    print panel;
                    nurl = 'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=' + panel['id'];
                    yield scrapy.Request(nurl, meta={'cookiejar':self.cookiejar}, headers=self.headers, callback=self.parse);
                else:
                    self.store_data({'url': url, 'name': title.encode('utf8')});
        except:
            print 'parse json [%s] failed' % body;


    def parse_content(self, response):
        pass;

    def start_requests(self):
        self.db = mysql.MySQL(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['passwd'], DB_CONFIG['db'], DB_CONFIG['port'], DB_CONFIG['charset'], DB_CONFIG['timeout'], '');
        return [scrapy.FormRequest("http://bbs.byr.cn/user/ajax_login.json",
                formdata = const.LOGIN_DATA,
                meta = {'cookiejar':1},
                headers = self.headers,
                callback=self.logged_in)];

    def logged_in(self, response):
        print response.body_as_unicode();
        self.cookiejar = response.meta['cookiejar'];
        for url in self.start_urls:
            yield scrapy.Request(url,meta={'cookiejar':response.meta['cookiejar']},headers=self.headers, callback=self.parse)

    def store_data(self, data):
        sql = "insert into sect(url, name) values ('%s', '%s')" % (MySQLdb.escape_string(data['url']), MySQLdb.escape_string(data['name']));
        self.db.update(sql);


