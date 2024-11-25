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
    '''
    options = Options()
    options.add_argument(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")
    driver = webdriver.Firefox(options=options)
    return driver

def get_links(driver, url):
    
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
    df = pd.read_csv('links.csv')
    df.drop(df[df['link'] == link].index, inplace=True, axis=0)
    df.to_csv('links.csv', index=False)

def click_dropdown(driver, ID):
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

    for link in links:
        res = link.split('/')
        driver.get(link)
        scraped = check_url(driver.current_url)
        
        time.sleep(random.randint(2,6))
        
        driver.execute_script(f"window.scrollBy(0, {random.randint(5, 500)});")
        time.sleep(random.randint(1, 10))
        driver.execute_script(f"window.scrollBy(0, {random.randint(200, 1100)});")
        time.sleep(random.randint(5, 8))

        if scraped:
            print('continuing...')
            continue
        time.sleep(random.randint(1,10))
        if BeautifulSoup(str(driver.page_source), 'html.parser').find('a', string='See more reviews') == None:
            continue
        review_link = BeautifulSoup(str(driver.page_source), 'html.parser').find('a', string='See more reviews')['href']

        driver.get('https://www.amazon.com' + review_link)
        scraped = check_url(driver.current_url)
        if scraped:
            print('continuing...')
            continue
        driver = click_dropdown(driver, 'star-count-dropdown_7')

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

        driver = click_dropdown(driver, 'star-count-dropdown_6')

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