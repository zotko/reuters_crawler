import scrapy
import logging
from scrapy_selenium import SeleniumRequest

from scrapy.loader import ItemLoader

from reuters_crawler.items import CrawlerItem
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ReutersSpider(scrapy.Spider):
    name = "reuters"

    def __init__(self, search=None, *args, **kwargs):
        self.file_name = search.lower().replace(' ', '_')
        self.url = f"https://de.reuters.com/search/news?sortBy=&dateRange=&blob={search.replace(' ', '+')}"

    def start_requests(self):
        yield SeleniumRequest(url=self.url, callback=self.parse)

    def parse(self, response):
        driver = response.request.meta['driver']

        # Click cookies banner
        # try:
        #     element = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, 'evidon-barrier-acceptbutton'))
        #     )
        #     element.click()
        # except TimeoutException:
        #     pass
        #
        # # Show all articles
        # while True:
        #     element = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, 'search-result-more-txt'))
        #     )
        #     if element.text.lower() == 'keine weiteren ergebnisse':
        #         break
        #     else:
        #         element.click()

        links = driver.find_elements_by_css_selector('.search-result-title a')

        for link in links:
            logging.debug(link)
            yield response.follow(link.get_attribute('href'), callback=self.parse_article)

    def parse_article(self, response):
        item_loader = ItemLoader(item=CrawlerItem(), response=response)
        item_loader.add_xpath('title', "//h1[contains(@class, 'ArticleHeader_headline')]//text()")
        item_loader.add_css('text', ".StandardArticleBody_body p::text")
        item_loader.add_css('date', '.ArticleHeader_date::text')
        yield item_loader.load_item()
