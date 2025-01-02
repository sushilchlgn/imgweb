import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from datetime import datetime
from fake_useragent import UserAgent

# Dynamic folder name based on the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
folder = f"manga_images_{timestamp}"
driver_path = "C:/Users/sushil/Desktop/python/imgweb/chromedriver/chromedriver.exe"

# Function to generate random user-agent
ua = UserAgent()
user_agent = ua.random  # Generate a random user-agent string

def download_images_from_scroll(url, output_folder=folder, driver_path=driver_path):
    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Initialize Selenium WebDriver with options to avoid detection
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    # Remove headless mode for a visible browser
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass some anti-bot protections
    options.add_argument(f"user-agent={user_agent}")  # Set random user-agent
    driver = webdriver.Chrome(service=service, options=options)

    # Load the webpage
    try:
        driver.get(url)
        print("Page loaded, please scroll to load images...")
        time.sleep(25)  # Allow time for the page to fully load
    except Exception as e:
        print(f"Error loading the website: {e}")
        driver.quit()
        return

    # Keep checking for new images as the user scrolls
    already_downloaded_images = set()  # Set to track already downloaded images

    try:
        while True:
            # Find all image elements on the page
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            print(f"Found {len(img_elements)} images.")

            # Process images and download them
            for i, img_element in enumerate(img_elements):
                img_url = img_element.get_attribute("src") or img_element.get_attribute("data-src")
                if not img_url:
                    continue
                
                # Resolve relative URLs to absolute URLs
                img_url = urljoin(url, img_url)

                # Skip images that have already been downloaded
                if img_url in already_downloaded_images:
                    continue

                try:
                    # Download the image
                    headers = {
                        "User-Agent": user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Referer": url,
                        "Connection": "keep-alive"
                    }
                    img_data = requests.get(img_url, headers=headers).content
                    img_name = os.path.join(output_folder, f"image_{len(already_downloaded_images)+1}.jpg")

                    # Save the image
                    with open(img_name, "wb") as img_file:
                        img_file.write(img_data)
                    print(f"Downloaded: {img_name}")
                    already_downloaded_images.add(img_url)  # Mark image as downloaded
                except Exception as e:
                    print(f"Failed to download image from {img_url}: {e}")

            # Ask the user to scroll down
            input("Press Enter after scrolling down to load more images...")

    except KeyboardInterrupt:
        print("Stopped by the user.")
    finally:
        # Close the Selenium browser
        driver.quit()
        print("All images have been processed!")

# Example usage
if __name__ == "__main__":
    website_url = input("Enter the website URL: ")
    download_images_from_scroll(website_url, driver_path=driver_path)
