import scrapy
from bs4 import BeautifulSoup


class PttSpider(scrapy.Spider):
    name = 'ptt'
    allowed_domains = ['www.ptt.cc']
    start_urls = ['https://www.ptt.cc/bbs/movie/index.html',
                  'https://www.ptt.cc/bbs/car/index.html',
                  'https://www.ptt.cc/bbs/Tech_Job/index.html']
    count = 0  # 執行次數

    def parse(self, response):
        domain = 'https://www.ptt.cc'
        for q in response.css('div.r-ent'):
            url = q.css('div.title > a::attr(href)').get()
            if url == None :
                continue
            # print(domain+url)
            yield scrapy.Request(domain+url, callback = self.parse2)

        last_page = response.css('div.btn-group-paging a::attr(href)').getall()[1]

        if last_page is not None:
            # 頁數
            self.count += 1
            if self.count <= 5 :
                yield response.follow(domain+last_page, callback= self.parse)


    def parse2(self, response):
        # 發文數
        soup = BeautifulSoup(response.text)
        articles = soup.find_all('div', 'push')
        for article in articles:
            messages = article.find('span', 'f3 push-content').getText()
            speak = len(messages)

        # 推文數
        score = 0
        pushes = soup.find_all("span", class_="push-tag")
        for p in pushes:
            if "推" in p.text:
                score = score + 1
        # print("推噓文分數:", score)

        # 內文
        content = soup.find("div", id="main-content")
        ds = content.find_all("div", class_="article-metaline")
        for d in ds:
            d.extract()
        ds = content.find_all("div", class_="article-metaline-right")
        for d in ds:
            d.extract()
        ds = content.find_all("div", class_="push")
        for d in ds:
            d.extract()
        ds = content.find_all("span", class_="f2")
        for d in ds:
            d.extract()
        # print("內文:", content.text)

        ans = {}
        try:
            if response.css('div.article-metaline ::text').getall()[3] in response.text:
                ans['title'] =  response.css('div.article-metaline ::text').getall()[3]
        except IndexError:
            pass
        try:
            if response.css('div.article-metaline ::text').getall()[1] in response.text :
                ans['author'] = response.css('div.article-metaline ::text').getall()[1]
        except IndexError:
            pass
        try:
            if response.css('div.article-metaline ::text').getall()[5] in response.text :
                ans['time'] = response.css('div.article-metaline ::text').getall()[5]
        except IndexError:
            pass

        try:
            ans['speak'] = speak
        except UnboundLocalError:
            pass

        ans['push'] = score
        ans['text'] = content.text
        yield ans
