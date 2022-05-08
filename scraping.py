#!/usr/bin/env python
# coding: utf-8


# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere_images": hemisphere_data(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        
        # Use the parent element to find the first <a> tag and save it as  `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

# ### Featured Images




def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)
    
    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere_data(browser):
    #  Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Convert the browser html to a soup object
    html = browser.html
    hemisphere_img = soup(html, 'html.parser')

    #Create list of items with each image / link information
    hemisphere_img_info = hemisphere_img.find_all('div', class_ = 'item')

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.

    for img_item in hemisphere_img_info:
    
        hemispheres = {}

        #Get image title text    
        img_title = img_item.find('h3').get_text() 
        #Use image title to click on the link that takes you to each full resolution image
        browser.click_link_by_partial_text(img_title)

        #Convert new website into beautiful soup item 
        html = browser.html
        img_info = soup(html,'html.parser')
        
        #Find tags to lead you to the full resolution image URL
        img = img_info.find('div', class_= 'downloads')
        img_url_tag = img.find('a')
        img_url = img.a['href']

        # Use partial URL to create full URL
        img_url_full = url + img_url

        #Create a dictionary that holds image title and full URL
        hemispheres = {'Title':img_title, 'Img_url': img_url_full}
    
        #Append dictionary to a list to store the information for all images
        hemisphere_image_urls.append(hemispheres)
    
        #Go back to the main page 
        browser.back()

    # Quit the browser
    browser.quit()
    #Return list of dictionaries from scrapped data
    return hemisphere_image_urls 

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())