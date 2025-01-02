import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_images_from_website(url, output_folder="downloaded_images"):
    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Fetch the website content
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all image tags
    img_tags = soup.find_all("img")
    if not img_tags:
        print("No images found on the webpage.")
        return

    print(f"Found {len(img_tags)} images. Starting download...")

    for i, img in enumerate(img_tags):
        # Get the image URL
        img_url = img.get("src")
        if not img_url:
            continue
        
        # Resolve relative URLs to absolute URLs
        img_url = urljoin(url, img_url)

        # Get the image content
        try:
            img_data = requests.get(img_url).content
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {img_url}: {e}")
            continue

        # Save the image
        img_name = os.path.join(output_folder, f"image_{i+1}.jpg")
        with open(img_name, "wb") as img_file:
            img_file.write(img_data)
        print(f"Downloaded: {img_name}")
    
    print("All images have been downloaded!")

# Example usage
if __name__ == "__main__":
    website_url = input("Enter the website URL: ")
    download_images_from_website(website_url)
