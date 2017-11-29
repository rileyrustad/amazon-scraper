from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from bs4 import BeautifulSoup
import requests
import re
from collections import defaultdict
import time
import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql_init import Review, Base, Category, Product


def check_category(category, session):
    categories = session.query(Category).filter_by(category_name=category.text).all()
    if len(categories) == 0:
        new_category = Category(category_name=category.text, completed=False)
        session.add(new_category)
        session.commit()
        return False
    elif len(categories) >= 1:
        return categories[0].completed


def check_product(product, session):
    product_id = re.search('/dp/[\w]+/', product.find_element_by_xpath('..').get_attribute('href')).group(0)[4:-1]
    products = session.query(Product).filter_by(product_ASIN=product_id).all()
    if len(products) == 0:
        new_product = Product(product_ASIN=product_id, completed=False)
        session.add(new_product)
        session.commit()
        return False
    elif len(products) >= 1:
        return products[0].completed

def scrape_reviews(link, driver, session, product_id):
    link.send_keys(Keys.CONTROL + Keys.SHIFT + Keys.RETURN)
    driver.switch_to.window(driver.window_handles[3])
    while True:
        time.sleep(1)
        reviews = driver.find_elements_by_xpath('*//i[@data-hook="review-star-rating"]')
        try:
            for review in reviews:
                star_rating = review.find_element_by_class_name('a-icon-alt').get_attribute('innerHTML')[0]
                e = review.find_element_by_xpath('../../../..')
                if len(session.query(Review).filter_by(review_id=e.get_attribute('id')).all()) == 0:
                    new_review = Review(review_id=e.get_attribute('id'),
                                        star_rating=int(star_rating),
                                        review_title=e.find_element_by_class_name('review-title').text,
                                        review_date=e.find_element_by_class_name('review-date').text[3:],
                                        text=e.find_element_by_class_name('review-text').text,
                                        product_ASIN = product_id)
                    session.add(new_review)
                    session.commit()
                else:
                    pass
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 10000)")
            next_ = driver.find_element_by_class_name('a-last')
            next_link = next_.find_element_by_tag_name('a')
            next_link.click()
        except NoSuchElementException:
            driver.close()
            driver.switch_to.window(driver.window_handles[2])
            break


def scrape_product(product, driver, session):
    if not check_product(product, session):
        product_ASID = re.search('/dp/[\w]+/', product.find_element_by_xpath('..').get_attribute('href')).group(0)[4:-1]
        product.find_element_by_xpath('..').send_keys(Keys.CONTROL + Keys.SHIFT + Keys.RETURN)
        driver.switch_to.window(driver.window_handles[2])

        links = driver.find_elements_by_tag_name('a')
        for link in links:
            if re.search('See all [0-9,.]* customer reviews', link.text):
                scrape_reviews(link, driver, session, product_ASID)
                break

        new_product = session.query(Product).filter_by(product_ASIN=product_ASID).first()
        new_product.completed = True
        session.commit()
        driver.close()
        driver.switch_to.window(driver.window_handles[1])


def scrape_category(category, driver, session):
    category_text = category.text

    if not check_category(category, session):
        category.send_keys(Keys.CONTROL + Keys.SHIFT + Keys.RETURN)
        driver.switch_to.window(driver.window_handles[1])
        while True:
            try:
                for i, product in enumerate(driver.find_elements_by_class_name("s-access-title")):
                    driver.find_elements_by_class_name("s-access-title")[i]
                    scrape_product(product, driver, session)
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, 10000)")
                next_products = driver.find_element_by_id('pagnNextLink')
                next_products.click()

            except NoSuchElementException:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                break

            cat = session.query(Category).filter_by(category_name=category_text).first()
            cat.completed = True
            session.commit()

if __name__ == "__main__":
    # Open sqlite connection/session
    engine = create_engine('sqlite:///reviews.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    # Open a new browser window
    driver = webdriver.Chrome(executable_path="./chromedriver")
    driver.implicitly_wait(1.5)

    # Prompt the user for
    url = raw_input("What amazon reviews would you like to scrape?:")
    if url == '':
        url = 'https://www.amazon.com/s/gp/search/ref=sr_nr_p_89_0?fst=as%3Aoff&rh=i%3Aaps%2Ck%3Aadidas%2Cp_89%3Aadidas&keywords=adidas&ie=UTF8&qid=1511382355&rnid=2528832011'
    driver.get(url)

    main_window = driver.current_window_handle

    # Expand all of the "see more" elements
    for i in driver.find_elements_by_class_name("a-expander-prompt"):
        i.find_element_by_xpath('..').click()

    # Iterate through the categories
    categories = []
    for i, category in enumerate(driver.find_elements_by_class_name("s-ref-text-link")):
        category = driver.find_elements_by_class_name("s-ref-text-link")[i]
        scrape_category(category, driver, session)
