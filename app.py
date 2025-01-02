import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urljoin
from fake_useragent import UserAgent
import base64
from io import BytesIO
from PIL import Image

# Function to generate random user-agent
ua = UserAgent()
user_agent = ua.random  # Generate a random user-agent string

driver_path = "C:/Users/sushil/Desktop/python/imgweb/chromedriver/chromedriver.exe"

def download_images_from_scroll(url, output_folder="manga_images", driver_path=driver_path):
    # Get user input for manga name and chapter
    manga_name = input("Enter the manga name: ").strip()
    chapter_name = input("Enter the chapter name: ").strip()

    # Create folder structure: Manga Name -> Chapter Name -> Images
    manga_folder = os.path.join(output_folder, manga_name)
    chapter_folder = os.path.join(manga_folder, f"Chapter_{chapter_name}")

    # Create the folder if it doesn't exist
    if not os.path.exists(chapter_folder):
        os.makedirs(chapter_folder)
        print(f"Created folder: {chapter_folder}")

    # Initialize Selenium WebDriver with options to avoid detection
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass some anti-bot protections
    options.add_argument(f"user-agent={user_agent}")  # Set random user-agent
    driver = webdriver.Chrome(service=service, options=options)

    # Load the webpage
    try:
        driver.get(url)
        print("Page loaded, please scroll to load images...")
        time.sleep(5)  # Allow time for the page to fully load
    except Exception as e:
        print(f"Error loading the website: {e}")
        driver.quit()
        return

    # Ask for manual or automatic scrolling
    scroll_mode = input("Do you want to scroll manually or automatically? (manual/automatic): ").strip().lower()

    # Keep checking for new images as the user scrolls
    already_downloaded_images = set()  # Set to track already downloaded images

    try:
        while True:
            # Find all image elements on the page
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            print(f"Found {len(img_elements)} images.")

            # Process images and download them
            for img_element in img_elements:
                img_url = img_element.get_attribute("src")
                if not img_url:
                    continue
                
                # Skip images that have already been downloaded
                if img_url in already_downloaded_images:
                    continue

                # Handle blob URLs or direct image links
                try:
                    if img_url.startswith('blob:'):
                        # Handle blob URLs (could potentially involve extracting base64 data)
                        img_data = driver.execute_script("return arguments[0].src;", img_element)
                        if img_data.startswith('data:image'):
                            # It's a base64 encoded image, decode it
                            img_data = img_data.split(',')[1]
                            img_data = base64.b64decode(img_data)
                            img = Image.open(BytesIO(img_data))
                            img_name = os.path.join(chapter_folder, f"image_{len(already_downloaded_images)+1}.png")
                            img.save(img_name)
                            print(f"Downloaded (base64): {img_name}")
                        else:
                            # Blob URL, attempt to download
                            print(f"Skipping blob URL: {img_url}")
                    else:
                        # Regular image URL, download it
                        headers = {
                            "User-Agent": user_agent,
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Referer": url,
                            "Connection": "keep-alive"
                        }
                        img_data = requests.get(img_url, headers=headers).content
                        img_name = os.path.join(chapter_folder, f"image_{len(already_downloaded_images)+1}.jpg")

                        # Save the image
                        with open(img_name, "wb") as img_file:
                            img_file.write(img_data)
                        print(f"Downloaded: {img_name}")
                    already_downloaded_images.add(img_url)  # Mark image as downloaded

                except Exception as e:
                    print(f"Failed to download image from {img_url}: {e}")

            # If automatic scrolling is chosen, scroll the page down
            if scroll_mode == "automatic":
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(3)  # Wait for new images to load

            # If manual scrolling is chosen, ask the user to scroll and press Enter
            elif scroll_mode == "manual":
                input("Press Enter after scrolling down to load more images...")

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    finally:
        # Close the Selenium browser
        driver.quit()
        print("All images have been processed!")

# Example usage
if __name__ == "__main__":
    website_url = input("Enter the website URL: ")
    download_images_from_scroll(website_url, driver_path=driver_path)
