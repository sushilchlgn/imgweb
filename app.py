import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from urllib.parse import urljoin
from datetime import datetime

# Dynamic folder name based on the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
folder = f"manga_images_{timestamp}"
driver_path = "C:/Users/sushil/Desktop/python/imgweb/chromedriver/chromedriver.exe"

def download_manga_images(url, output_folder=folder, driver_path=driver_path):
    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Initialize Selenium WebDriver
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass some anti-bot protections
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
        time.sleep(2)  # Wait for new content to load
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
                img_data = requests.get(img_url).content
                img_name = os.path.join(output_folder, f"image_{i+1}.jpg")

                # Save the image
                with open(img_name, "wb") as img_file:
                    img_file.write(img_data)
                print(f"Downloaded: {img_name}")
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
