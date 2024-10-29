from Dataset import Europa
import time
import os
import random
import requests
import json
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from urllib.parse import urlparse

#total results Time iteration
def total_results_for_period(year, period=50):
    for i in range(period):
        x = Europa(f"""query=NOT+where:("Sweden")+AND+when:("{year+i}")""")
        num = x.get_total_number()
        print(f"The total number of images for year {year+i}: {num}")

#url getter Time iteration
def total_urls_for_period(year, period=50, save=False, total_per_year=0):
    urls = []
    for i in range(period):
       x = Europa(f"""query=NOT+where:("Sweden")+AND+when:("{year+i}")""")
       yearly_urls = x.get_photo_urls(total_per_year)
       print(f"URL parsing complete. Total results for year {year+i}: {len(yearly_urls)}")
       urls.extend(yearly_urls)
       if save:
           with open(f"{year+i}.json", 'w') as file:
               json.dump(yearly_urls, file)
    return urls

#randomizer function returing a random subset from a file containing a list of links
def randomize_urls(filename, n=1000):
    with open(filename, 'r') as file:
        urls = json.load(file)
    print(f"The overall list contains {len(urls)} elements.")
    random.shuffle(urls)
    return urls[:n]

#download all images regardless of the input
def download_images(urls, download="images"):
    """Downloads images from a list of URLs.
    
    Args:
    urls: A list of urls containing a single image each.
    download: The directory to save the images. (Defaults to images)
    """
    
    os.makedirs(download, exist_ok=True)
        
    for url in urls:
        time.sleep(0.2)
        #only take the pages which expose jpgs 
        if url.lower().endswith(".jpg"):
            try:
                #get requests and bad status exception
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                #validate the content of the image
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image'):
                    print(f"Skipped {url}: Content-Type {content_type} is not an image")
                    continue

                #get the image
                image_data = response.content
                #handle the unidentified formats
                try:
                    image = Image.open(BytesIO(image_data))
                    width, height = image.size
                    print(f"Image dimensions for {url}: {width}x{height}")
                except UnidentifiedImageError:
                    print(f"Cannot identify image from {url}. Skipping this file.")
                    continue
                #check for dimensions
                image = Image.open(BytesIO(image_data))
                width, height = image.size
                print(f"Image dimensions for {url}: {width}x{height}")
                if width>999 and height>500 and (height/width)<1:
                   #parse the url and get default file names 
                   parsed_url = urlparse(url)
                   #keep the original filename as on the server
                   filename = os.path.basename(parsed_url.path)
                   filepath = os.path.join(download, filename)
        
                   with open(filepath, 'wb') as f:
                      for chunk in response.iter_content(chunk_size=8192):
                         f.write(chunk)
 
                   print(f"Downloaded: {url} to {filepath}")
                time.sleep(0.1)
        
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {url}: {e}")    

#actual execution for a specific time period
year = 1984
#period is for the total amount of years, so the final year in execution would be year+period-1
period = 1
#send initial requests by considering the total amount of results first
total_results_for_period(year, period)
#get all links for a period specified above. last boolean is for saving the files in individual year .json format
urls = total_urls_for_period(year, period, True)

#randomize the resulting list and only get a subset of links before downloading
#iterate through the yearly urls:
total_urls = []
for i in range(period):
    yearly_urls = randomize_urls(f"{year+i}.json", 2500)
    total_urls.extend(yearly_urls)
print(len(total_urls))

#download the specified images
download_images(total_urls, f"all_{year}")
