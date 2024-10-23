from Dataset import Europa
import time
import os
import requests
from urllib.parse import urlparse

#total results Time iteration
def total_results_for_period(year, period=50):
    #tentative check for total results in each year
    for i in range(period):
        x = Europa(f"""query=NOT+where:("Sweden")+AND+when:("{year+i}")""")
        num = x.get_total_number()
        print(f"The total number of images for year {year+i}: {num}")

#url getter Time iteration
def total_urls_for_period(year, period=50, random=False):
    urls = []
    for i in range(period):
       x = Europa(f"""query=NOT+where:("Sweden")+AND+when:("{year+i}")""")    
       urls_subset = x.get_photo_urls()
       urls.extend(urls_subset)
       #print(f"There resulting url list is empty. Revise the query formation!")
    print(f"URL parsing complete. Total results for year {year+i}: {len(urls)}")
    return urls

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
    
    print(f"Total images: {total}")

#Actual execution

year = 1902
period = 1
urls = total_urls_for_period(year, period)
#download the specified images-should I keep this in main?
download_images(urls, f"all_{year}")
