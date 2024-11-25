import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd

from webscraper import check_url, check_review_id, log_data, get_links, remove_link, click_dropdown, scrape, setup

class TestScraperFunctions(unittest.TestCase):
    
    @patch("os.path.exists")
    def test_check_url_exists(self, mock_exists):
        mock_exists.return_value = True
        with patch("builtins.open", mock_open(read_data="header,link\n,,,https://someurl.com")):
            result = check_url("https://someurl.com")
            self.assertTrue(result)

    @patch("os.path.exists")
    def test_check_url_not_exists(self, mock_exists):
        mock_exists.return_value = True
        with patch("builtins.open", mock_open(read_data="header,link\n,,,https://otherurl.com")):
            result = check_url("https://someurl.com")
            self.assertFalse(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_log_data_new_file(self, mock_open, mock_exists):
        mock_exists.return_value = False
        log_data('product1', 'Product Name', 'review1', 'Type A', '4.5', '4', '100', 'Great product!', 'https://example.com')
        mock_open.assert_called_once_with("ProductReviews.csv", mode='w', newline="", encoding='utf-8')

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_log_data_existing_file(self, mock_open, mock_exists):
        mock_exists.return_value = True
        with patch("csv.reader") as mock_csv_reader:
            mock_csv_reader.return_value = [["header"], ["review1"]]
            log_data('product1', 'Product Name', 'review1', 'Type A', '4.5', '4', '100', 'Great product!', 'https://example.com')
        mock_open.assert_called_once_with("ProductReviews.csv", mode='a', newline="", encoding='utf-8')

    @patch("os.path.exists")
    @patch("pandas.read_csv")
    def test_get_links_from_existing_file(self, mock_read_csv, mock_exists):
        mock_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({'link': ['https://example.com']})
        driver = MagicMock()
        links = get_links(driver, 'https://amazon.com')
        self.assertEqual(links, ['https://example.com'])

    @patch("os.path.exists")
    @patch("pandas.read_csv")
    def test_get_links_from_new_file(self, mock_read_csv, mock_exists):
        mock_exists.return_value = False
        driver = MagicMock()
        driver.page_source = '<div class="s-result-item"><a href="/some-url">Link</a></div>'
        links = get_links(driver, 'https://amazon.com')
        self.assertEqual(links, ['https://www.amazon.com/some-url'])
    
    @patch("selenium.webdriver.Firefox")
    @patch("selenium.webdriver.support.ui.WebDriverWait")
    def test_click_dropdown(self, mock_wait, mock_driver):
        driver = MagicMock()
        mock_wait.return_value.until.return_value = MagicMock()
        result = click_dropdown(driver, 'star-count-dropdown_7')
        self.assertIsNotNone(result)

    @patch("time.sleep", return_value=None)  # Mock time.sleep to avoid delays
    @patch("selenium.webdriver.Firefox")
    def test_scrape(self, mock_driver):
        mock_driver.get.return_value = None
        mock_driver.page_source = '<html><div id="cm_cr-review_list"><div data-hook="review" id="review1">Review 1</div></div></html>'
        mock_driver.execute_script.return_value = None
        links = ['https://amazon.com/product1']
        
        with patch("builtins.open", mock_open()) as mock_open:
            scrape(links, mock_driver)
            mock_open.assert_called()

    @patch("selenium.webdriver.Firefox")
    def test_setup(self, mock_driver):
        driver = setup("fake_user_agent")
        self.assertIsNotNone(driver)

    @patch("os.path.exists")
    @patch("pandas.read_csv")
    def test_remove_link(self, mock_read_csv, mock_exists):
        mock_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({'link': ['https://example.com']})
        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            remove_link('https://example.com')
            mock_to_csv.assert_called_once()

if __name__ == "__main__":
    unittest.main()
