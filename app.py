import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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

def download_manga_images(url, output_folder=folder, driver_path=driver_path):
    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Initialize Selenium WebDriver with options to avoid detection
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass some anti-bot protections
    options.add_argument("--disable-extensions")  # Disable extensions to avoid detection
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    options.add_argument("start-maximized")  # Start maximized
    options.add_argument("disable-infobars")  # Disable the "Chrome is being controlled" info bar
    options.add_argument(f"user-agent={user_agent}")  # Set random user-agent
    options.add_argument("--no-sandbox")  # Disable sandbox for enhanced performance
    options.add_argument("--disable-dev-shm-usage")  # Optimize for Docker environments
    options.add_argument("--remote-debugging-port=9222")  # Debugging purposes
    driver = webdriver.Chrome(service=service, options=options)

    # Load the webpage
    try:
        driver.get(url)
        time.sleep(5)  # Allow time for the page to fully load
    except Exception as e:
        print(f"Error loading the website: {e}")
        driver.quit()
        return

    # Scroll to the bottom of the page to load all images
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))  # Wait for new content to load with random delay
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # Stop when no more content is loaded
            break
        last_height = new_height

    # Find all image elements
    img_elements = driver.find_elements(By.TAG_NAME, "img")
    if not img_elements:
        print("No images found on the webpage.")
        driver.quit()
        return

    print(f"Found {len(img_elements)} images. Starting download...")

    for i, img_element in enumerate(img_elements):
        try:
            # Get the image URL
            img_url = img_element.get_attribute("src")
            if not img_url:
                continue

            # Resolve relative URLs to absolute URLs
            img_url = urljoin(url, img_url)

            # Try to download the image
            try:
                headers = {
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": url,
                    "Connection": "keep-alive"
                }
                img_data = requests.get(img_url, headers=headers).content
                img_name = os.path.join(output_folder, f"image_{i+1}.jpg")

                # Save the image
                with open(img_name, "wb") as img_file:
                    img_file.write(img_data)
                print(f"Downloaded: {img_name}")
                time.sleep(random.uniform(2, 4))  # Add random delay between downloads

            except Exception as e:
                print(f"Failed to download image {i+1} from {img_url}: {e}")
                # Save the failed URL to a text file for reference
                with open(os.path.join(output_folder, "failed_images.txt"), "a") as f:
                    f.write(f"Image {i+1} URL: {img_url}\n")

        except Exception as e:
            print(f"Error processing image {i+1}: {e}")

    # Close the Selenium browser
    driver.quit()
    print("All images have been processed!")

# Example usage
if __name__ == "__main__":
    website_url = input("Enter the website URL: ")
    download_manga_images(website_url, driver_path=driver_path)
