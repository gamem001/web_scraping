# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import time

def scrape_all():
    #initialize the browser object
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    
    # Stop browswer and return data
    browser.quit()
    return data

def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    featured_url = 'https://mars.nasa.gov/news/'
    browser.visit(featured_url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    # Create html object, create bs object, parse with html
    img_html = browser.html
    news_soup = soup(img_html, 'html.parser')
    # Add try/except for error handling
    try:
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = news_soup.find('div', class_='list_text').find('div', class_='content_title').text
        news_p = news_soup.find('div', class_='article_teaser_body').text        
    except AttributeError:
        return None, None
    return news_title, news_p
    
def featured_image(browser):
    # Visit URL
    featured_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(featured_url)
    #use splinter to click on 'full image' button
    featured_image_link = browser.find_by_id("full_image")
    featured_image_link.click()
    #allow a wait time for a few seconds to allow browser to catch up
    time.sleep(2)
    #use splinter to click on 'more info' button for image url
    full_image = browser.links.find_by_partial_text('more info')
    full_image.click()
    # Parse the resulting html with soup
    img_html = browser.html
    img_soup = soup(img_html, 'html.parser')
    # Add try/except for error handling
    try:
        #identify image url using 'parent' figure, 'child' a, then pulling href
        link = img_soup.find('figure').find('a').get('href')
    except AttributeError:
        return None
    # Use the base url to create a full link
    img_url = f'https://www.jpl.nasa.gov{link}'
    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        mars_info_df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    # Assign columns and set index of dataframe
    mars_info_df.columns=['Description', 'Values']
    mars_info_df.set_index('Description', inplace=True)
    # Convert dataframe into HTML format, add bootstrap
    return mars_info_df.to_html(classes="table table-striped")

def mars_hemispheres(browser):
    #identify url and visit using browser.visit
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    #Create html object, create bs object, parse with html
    image_html = browser.html
    soup_html = soup(image_html, 'html.parser')
    #pull the information in div class item
    hemispheres = soup_html.find_all('div', class_='item')
    #create dictionary for image link storage
    hemisphere_urls = []
    #identify beginning of link for image links
    main_link = 'https://astrogeology.usgs.gov'

    for h in hemispheres:
        #get the title of each image
        title = h.find('h3').text.strip('Enhanced')
        #pull links for images
        end_link = h.find("a").get("href")
        #combine main and end links for new browser visit
        browser.visit(main_link + end_link)
        #html object for images
        images_html = browser.html
        #Parse HTML with Beautiful Soup for every individual hemisphere information website
        soup_img = soup(images_html, 'html.parser')
        #pull link for full image
        img_url = main_link + soup_img.find('img', class_='wide-image').get('src')
        # Append the retreived information into a list of dictionaries 
        hemisphere_urls.append({"title" : title, "img_url" : img_url})
    return hemisphere_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
