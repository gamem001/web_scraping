#dependencies
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import time


from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars


app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/craigslist_app'
mongo = PyMongo(app)

@app.route('/scrape')
def scraper():

#initialize the browser object
executable_path = {'executable_path': 'chromedriver.exe'}
browser = Browser('chrome', **executable_path, headless=False)

#use splinter to visit the nasa website
url = 'https://mars.nasa.gov/news/'
browser.visit(url)

# NASA Mars News --------------------------

#Create html object
html = browser.html

#Create BeautifulSoup object; parse with 'html.parser'
soup = bs(html, 'html.parser')

#use 'list_text' followed by 'content_title' otherwise the first return is "Mars Now" (a hyperlink in the dropdown menu)
news_title = soup.find('div', class_='list_text').find('div', class_='content_title').text
print(f'The most current article on NASA.gov is "{news_title}." ')

#extract the teaser paragraph for the first article
news_p = soup.find('div', class_='article_teaser_body').text
print(f'The article, "{news_title}," is about {news_p}')

# JPL Mars Space Images - Featured Image -----------------------

#use splinter to visit the space images website
featured_url = 'https://www.jpl.nasa.gov/spaceimages'
browser.visit(featured_url)

image_html = browser.html
soup = bs(image_html, 'html.parser')

#use splinter to click on 'full image' button
featured_image_link = browser.find_by_id("full_image")
featured_image_link.click()

#allow execution to be suspended for 2 seconds
time.sleep(2)
full_image = browser.links.find_by_partial_text('more info')
full_image.click()

#create html object again, create bs object, parse with html.parser
image_html = browser.html
soup = bs(image_html, 'html.parser')

#identify url using 'parent' figure, 'child' a, then pulling href
link = soup.find('figure').find('a').get('href')
# print(link)

#combine original url with image url to create image link
landing_url = 'https://www.jpl.nasa.gov'
featured_image_url = landing_url + link
print (featured_image_url)

# Mars Facts -------------

import pandas as pd

#identify link for next scrape
facts_url = 'https://space-facts.com/mars/' 

#use pandas to read the table from the webpage above
tables = pd.read_html(facts_url)

#print table from website
# tables[0]

mars_info_df = tables[0]

#change column headers
mars_info_df.columns = ['Description', 'Value']
# mars_info_df.head()

#save table and info, along with headers, to files
mars_facts_table = mars_info_df.to_html('mars_facts_table.html')

mars_info_df

# Mars Hemispheres ------------------------------

#use splinter to visit the space images website
hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
browser.visit(hemisphere_url)

image_html = browser.html
soup = bs(image_html, 'html.parser')

hemispheres = soup.find_all('div', class_='item')

hemisphere_urls = []
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
    soup = bs(images_html, 'html.parser')
    #pull link for full image
    img_url = main_link + soup.find('img', class_='wide-image').get('src')
    # Append the retreived information into a list of dictionaries 
    hemisphere_urls.append({"title" : title, "img_url" : img_url})
    
hemisphere_urls

if __name__ == "__main__":
    app.run(debug=True)