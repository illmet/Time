import requests
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import os
import re

class Europa():
    def __init__(self, query):
        """
            This sets up the full access link. Parameters for photographs specifically.
            
            Args:
                query: String, formatted for filtering.
        """
        base = "https://api.europeana.eu/record/v2/search.json"

        self.url = f"{base}?{query}&theme=photography&wskey={str(os.environ.get("europa"))}&rows=100&media=true"

    def get_url(self, cursor):
        """
            Constructs a custom url for either getting the full list of valus or sending intermidiate requests (such as to get total number of items)
            Args:
                cursor: Boolean for whether the cursor (True, full iteration) or start (False, only 1000 initial results outputted) is used.
        """
        if cursor:
            iteration = "&cursor=*"
        else:
            iteration = "&start=1"

        return self.url + iteration
    
    def send_request(self, url):
        response = requests.get(url)
        result = response.json()
        if result['success']==True:
            return response.json()
        elif result['success']==False:
            error_msg = result['message']
            error_code = result['error']
            print(f"{error_msg}. Error Code: {error_code}")
            return None
        else:
            print("Unknown error occured.")
            return None

    def get_total_number(self):
        url = self.get_url(False)
        result = self.send_request(url)
        if result:
            return result['totalResults']
        else:
            return None

    def get_photo_urls(self):
        total = self.get_total_number()
        url = self.get_url(True)
        interim = self.send_request(url)
        if total and interim:
            url_list = []
            for _ in range(0, (total // 100)+1):
                response = requests.get(url)
                interim = response.json()
                
                for item in interim['items']:
                    url_list.append(item['edmIsShownBy'][0])
    
                #get the cursor values
                new_cursor = interim['nextCursor']
                #parse the url
                parsed_url = urlparse(url)
                #set the query parameters
                query_params = parse_qs(parsed_url.query)
                query_params['cursor'] = [new_cursor]
                #rebuild the string
                encoded_query_string = urlencode(query_params, doseq=True)
                #rebuild the complete URL
                updated_url_tuple = (parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                                   parsed_url.params, encoded_query_string, parsed_url.fragment)
                url = urlunparse(updated_url_tuple)
                time.sleep(0.2)
            return url_list

    def download_images(self, urls, download="images"):
        """Downloads images from a list of URLs.
    
        Args:
            urls: A list of urls containing a single image each.
            download: The directory to save the images. (Defaults to images)
        """
    
        os.makedirs(download, exist_ok=True)
        total = 0
        
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
                    total+=1
                    time.sleep(0.1)
        
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {url}: {e}")
    
        print(f"Total images: {total}")