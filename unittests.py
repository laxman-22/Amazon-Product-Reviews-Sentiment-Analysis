import unittest
from fake_useragent import UserAgent
import csv
import os
import pandas as pd
from unittest.mock import MagicMock, patch
from selenium.webdriver.support.ui import WebDriverWait
from webscraper import check_url, check_review_id, log_data, get_links, remove_link, click_dropdown, scrape, setup


class TestScraperFunctions(unittest.TestCase):
    
    def test_check_url_exists(self):
        result = check_url("https://www.amazon.com/Beats-Solo-Wireless-Headphones-Matte/dp/B0CZPLV566/?_encoding=UTF8&pd_rd_w=RoPYP&content-id=amzn1.sym.8a144415-f607-40cf-a9f1-91eb713510a8&pf_rd_p=8a144415-f607-40cf-a9f1-91eb713510a8&pf_rd_r=A32VV4PSJWM8HJG7R9ZQ&pd_rd_wg=YcXIk&pd_rd_r=707cce1a-83f4-440a-bb46-423437ff13cd&ref_=pd_hp_d_atf_unk")
        self.assertFalse(result)
        result = check_url("https://www.amazon.com/Apple-2022-10-9-inch-iPad-Wi-Fi/product-reviews/B0BJLXMVMV/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1")
        self.assertTrue(result)        

    def test_check_review_id(self):
        result = check_review_id('RB47WOU0Q32Y5')
        self.assertTrue(result)
        result = check_review_id('test')
        self.assertFalse(result)

    def test_log_data(self):
        with open('ProductReviews.csv', mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            rows = list(csv_reader)
        log_data('product1', 'Product Name', 'review1', 'Type A', '4.5', '4', '100', 'Great product!', 'https://example.com')
        with open('ProductReviews.csv', mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if 'product1' in str(row[0]):
                    worked = True
                else:
                    worked = False
        self.assertTrue(worked)
        # Rollback the change
        with open('ProductReviews.csv', mode='w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(rows)

    def test_setup(self):
        ua = UserAgent()
        driver = setup(ua)
        self.assertIsNotNone(driver)
        driver.quit()

    def test_get_links(self):
        ua = UserAgent()
        driver = setup(ua)
        url = f'https://www.amazon.com/s?k=electronics&i=electronics&page=1'
        links = get_links(driver, url)
        self.assertIsNotNone(links)
        # Rollback file creation
        os.remove('links.csv')
        driver.quit()
    
    def test_remove_link(self):
        url = f'https://example.com'
        df = pd.DataFrame()
        df['link'] = url
        df.to_csv('links.csv', index=False)
        remove_link(url)
        with open('links.csv', mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if url not in str(row[0]):
                    worked = True
                else:
                    worked = False
        self.assertTrue(worked)
        # Rollback file creation
        os.remove('links.csv')

    
if __name__ == "__main__":
    unittest.main()
