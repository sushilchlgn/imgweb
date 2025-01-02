import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from urllib.parse import urljoin

def download_images_with_selenium(url, output_folder="downloaded_images", driver_path="chromedriver"):
    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Initialize Selenium WebDriver
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    driver = webdriver.Chrome(service=service, options=options)

    # Load the webpage
    try:
        driver.get(url)
        time.sleep(5)  # Allow time for the page to fully load
    except Exception as e:
        print(f"Error loading the website: {e}")
        driver.quit()
        return

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

            # Download the image
            img_data = requests.get(img_url).content
            img_name = os.path.join(output_folder, f"image_{i+1}.jpg")

            # Save the image
            with open(img_name, "wb") as img_file:
                img_file.write(img_data)
            print(f"Downloaded: {img_name}")
        except Exception as e:
            print(f"Failed to download image {i+1}: {e}")

    # Close the Selenium browser
    driver.quit()
    print("All images have been downloaded!")

# Example usage
if __name__ == "__main__":
    website_url = input("Enter the website URL: ")
    driver_path = input("Enter the path to your ChromeDriver (or press Enter for 'chromedriver'): ") or "chromedriver"
    download_images_with_selenium(website_url, driver_path=driver_path)
