from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from fake_useragent import UserAgent
import csv
import os
import pandas as pd


csv_file = './ProductReviews.csv'
data = dict()

def check_url(link):
    '''
    This function checks if the current URL has already been scraped 
    by checking the last row of the ProductReviews.csv file as product
    links are stored.

    Parameters:
    link (str): URL to be checked

    Returns:
    scraped (bool): Whether or not the link has been scraped
    
    '''
    if (os.path.exists(csv_file)) == False:
        return
    with open("ProductReviews.csv", mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        scraped = False
        for row in reader:
            if row[-1] == link:
                scraped = True
                print("already scraped link")
                break
        return scraped

def check_review_id(review_id):
    '''
    This function checks if the current Review has already been scraped 
    by checking the ReviewID of the ProductReviews.csv file as each Review ID
    is stored in the dataset

    Parameters:
    review_id (str): Review ID to be checked

    Returns:
    exists (bool): Whether or not the review has been scraped
    
    '''
    with open("ProductReviews.csv", mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        exists = False
        for row in reader:
            if row[1] == review_id:
                exists = True
                break
        return exists



def log_data(product_id, name, review_id, review_type, product_rating, review_rating, rating_count, description, url):
    '''
    This function inserts a row of the collected data into the ProductReviews.csv file

    Parameters:
    product_id (str): ID of a product
    name (str): Text name of the product
    review_id (str): ID of the review to be inserted
    review_type (str): Whether the review is "Positive" or "Critical"
    product_rating (str): Overall product rating out of 5 stars
    review_rating (str): Rating of this particular review out of 5 stars
    rating_count (str): Number of ratings for the product
    description (str): Text description of the review
    url (str): URL on where the review can be found

    Returns:
    scraped (bool): Whether or not the link has been scraped
    
    '''
    data['product_id'] = product_id
    data['review_id'] = review_id
    data['review_type'] = review_type
    data['product_name'] = name
    data['product_rating'] = product_rating
    data['review_rating'] = review_rating
    data['rating_count'] = rating_count
    data['description'] = description
    data['url'] = url

    if (os.path.exists(csv_file)) == False:
        with open("ProductReviews.csv", mode='w', newline="", encoding='utf-8') as f:
            w = csv.DictWriter(f, data.keys())
            w.writeheader()
            w.writerow(data)
    else:
        exists = check_review_id(review_id)
        if exists:
            print("already scraped review")
            return
        else:
            with open("ProductReviews.csv", mode='a', newline="", encoding='utf-8') as f:
                w = csv.DictWriter(f, data.keys())
                w.writerow(data)


def setup(user_agent):
    '''
    This function instantiates a simulated User Agent so that the browser can recognize
    the scraper as a user opening up a browser.

    Parameters:
    user_agent (UserAgent): Instance of the UserAgent class which is used to simulate user behaviour

    Returns:
    driver (webdriver): The Selenium webdriver that is actually used to traverse websites
    
    '''
    options = Options()
    options.add_argument(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")
    driver = webdriver.Firefox(options=options)
    return driver

def get_links(driver, url):
    '''
    This function retrieves the links on the current page of Amazon's electronics department and stores them in the links.csv
    file in order for the scraper to pick up where it left off in the event of an interruption

    Parameters:
    driver (webdriver): Instance of the Selenium webdriver that is used to traverse websites
    url (str): The current URL that shows a single page containing a list of products so that the links of each product on the page can be extracted

    Returns:
    links (list): The list of links that were added to the links.csv file and now the list can be used to traverse through each element in the list.

    '''
    
    if (os.path.exists('links.csv')) == False:
        driver.get(url)
        soup = BeautifulSoup(str(driver.page_source), 'html.parser').select('div.sg-col-20-of-24.s-result-item.s-asin.sg-col-0-of-12.sg-col-16-of-20.sg-col.s-widget-spacing-small.gsx-ies-anchor.sg-col-12-of-16')
        links = []
        for elem in soup:
            links.append('https://www.amazon.com' + elem.find('a')['href'])
        df = pd.DataFrame({'link': links})
        df.to_csv('links.csv', index=False)   
    else:
        df = pd.read_csv('links.csv') 
        links = df['link'].to_list()
        if len(links) < 1:
            os.remove('links.csv')
            get_links(driver, url)
    return links

def remove_link(link):
    '''
    Once a link has been scraped, remove the link from the file.

    Parameters:
    link (str): Link to be removed from the links.csv file

    '''
    df = pd.read_csv('links.csv')
    df.drop(df[df['link'] == link].index, inplace=True, axis=0)
    df.to_csv('links.csv', index=False)

def click_dropdown(driver, ID):
    '''
    This function performs the click for selecting the "Positive" and "Critical" review types on each product page

    Parameters:
    driver (webdriver): Instance of the Selenium webdriver that is used to traverse websites
    ID (str): The HTML element ID to be selected

    '''
    count = 5
    while count >= 0:
        try:
            dropdown = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'star-count-dropdown'))
            )
            
            driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
            driver.execute_script("arguments[0].click();", dropdown)

            option = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, ID))
            )
            driver.execute_script("arguments[0].click();", option)
        except Exception as e:
            print(e)
        count -= 1

    return driver

def scrape(links, driver):
    '''
    This is the primary function that contains all the logic for navigating each page in the scraper

    Parameters:
    links (list): The array of all the links that were on the current page in the Amazon department
    driver (webdriver): Instance of the Selenium webdriver that is used to traverse websites    
    '''

    for link in links:
        res = link.split('/')
        driver.get(link)

        # Check if the current link has been scraped
        scraped = check_url(driver.current_url)
        
        # Random waiting periods and scrolling on the page to introduce basic randomness in scraper behavior 
        # (Note: Amazon has been able to figure out the pattern in this code so more randomness would have to be added)
        time.sleep(random.randint(2,6))
        driver.execute_script(f"window.scrollBy(0, {random.randint(5, 500)});")
        time.sleep(random.randint(1, 10))
        driver.execute_script(f"window.scrollBy(0, {random.randint(200, 1100)});")
        time.sleep(random.randint(5, 8))

        # Continue if this link was visited
        if scraped:
            print('continuing...')
            continue
        # More random sleep
        time.sleep(random.randint(1,10))

        # Find the "See More Reviews" HTML element to get to all the reviews
        if BeautifulSoup(str(driver.page_source), 'html.parser').find('a', string='See more reviews') == None:
            continue
        review_link = BeautifulSoup(str(driver.page_source), 'html.parser').find('a', string='See more reviews')['href']
        
        # Go to the reviews page to see all reviews for this product
        driver.get('https://www.amazon.com' + review_link)

        # Check if the product has been scraped
        scraped = check_url(driver.current_url)
        if scraped:
            print('continuing...')
            continue
        # Click the dropdown to filter reviews by Positive sentiment
        driver = click_dropdown(driver, 'star-count-dropdown_7')

        # Retrieve all necessary review parameters in order to log to the file for Positive reviews
        soup = BeautifulSoup(str(driver.page_source), 'html.parser') 
        for item in res:
            if item == 'dp':
                idx = res.index(item)
                product_id = res[idx+1]   
                break
            else:     
                product_id = 'Unknown'
                break

        name = soup.find('a', {'data-hook': 'product-link'}).text
        product_rating = soup.find(attrs={'data-hook': 'rating-out-of-text'}).text.split(" ")[0]
        rating_count = soup.find(attrs={'data-hook': 'total-review-count'}).find_next('span').text.split(" ")[0]
        review_type = soup.find('div', {'class': 'star-rating-select'}).find_next('span').find_next('span').find_next('span').find_next('span').find_next('span').text.split(" ")[0]
        reviews = soup.find('div', {'id': 'cm_cr-review_list'}).find_all(attrs={'data-hook': 'review'})

        for review in reviews:
            review_id = review['id']
            review_rating = review.find_next('i').find_next('span').text.split(" ")[0]
            description = review.find_next(attrs={'data-hook': 'review-body'}).find_next('span').text

            print(review_id)

            log_data(product_id=product_id, 
                    name=name, 
                    review_id=review_id, 
                    review_type=review_type,
                    product_rating=product_rating, 
                    review_rating=review_rating, 
                    rating_count=rating_count, 
                    description=description,
                    url=driver.current_url)
        time.sleep(random.randint(1,10))

        # Click the dropdown to filter reviews by Critical sentiment
        driver = click_dropdown(driver, 'star-count-dropdown_6')

        # Retrieve all necessary review parameters in order to log to the file for Critical reviews
        soup = BeautifulSoup(str(driver.page_source), 'html.parser') 
        
        review_type = soup.find('div', {'class': 'star-rating-select'}).find_next('span').find_next('span').find_next('span').find_next('span').find_next('span').text.split(" ")[0]
        reviews = soup.find('div', {'id': 'cm_cr-review_list'}).find_all(attrs={'data-hook': 'review'})

        for review in reviews:
            review_id = review['id']
            review_rating = review.find_next('i').find_next('span').text.split(" ")[0]
            description = review.find_next(attrs={'data-hook': 'review-body'}).find_next('span').text

            print(review_id)

            log_data(product_id=product_id, 
                    name=name, 
                    review_id=review_id, 
                    review_type=review_type,
                    product_rating=product_rating, 
                    review_rating=review_rating, 
                    rating_count=rating_count, 
                    description=description,
                    url=driver.current_url)
        remove_link(link)


def main():
    '''
    This is the main function that performs necessary initializations and sets up a count for the pages to traverse through.
    Note: The count value has to be manually updated as a page is scraped (i.e. if count is 1 the first page will be scraped, but once
    it has been scraped count should be updated to 2 so that the links of the second page are retrieved instead of starting from the first page)
    '''
    count = 7
    ua = UserAgent()
    while count < 30:
        driver = setup(ua)
        url = f'https://www.amazon.com/s?k=electronics&i=electronics&page={count}'
        links = get_links(driver, url)
        scrape(links, driver)
        driver.quit()
        count += 1
        time.sleep(random.randint(1,10))

if __name__ == '__main__':
    main()