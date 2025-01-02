import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from urllib.parse import urljoin
from fake_useragent import UserAgent

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
        print("Page loaded, starting to scroll and load images...")
        time.sleep(5)  # Allow time for the page to fully load
    except Exception as e:
        print(f"Error loading the website: {e}")
        driver.quit()
        return

    # Keep checking for new images as the user scrolls
    already_downloaded_images = set()  # Set to track already downloaded images

    try:
        while True:
            # Check if the browser window is still open
            if not driver.window_handles:
                print("Browser window closed. Exiting the program.")
                break

            # Execute JavaScript to get valid image URLs (not blob URLs)
            img_urls = driver.execute_script("""
                let images = [];
                document.querySelectorAll('img').forEach(img => {
                    let imgSrc = img.src || img.getAttribute('data-src');
                    if (imgSrc && !imgSrc.startsWith('blob:')) {
                        images.push(imgSrc);
                    }
                });
                return images;
            """)

            print(f"Found {len(img_urls)} valid image URLs.")

            # Process images and download them
            for i, img_url in enumerate(img_urls):
                if img_url in already_downloaded_images:
                    continue
                
                try:
                    # Resolve relative URLs to absolute URLs
                    img_url = urljoin(url, img_url)

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
                    img_name = os.path.join(chapter_folder, f"image_{len(already_downloaded_images) + 1}.jpg")

                    # Save the image
                    with open(img_name, "wb") as img_file:
                        img_file.write(img_data)
                    print(f"Downloaded: {img_name}")
                    already_downloaded_images.add(img_url)  # Mark image as downloaded

                except Exception as e:
                    print(f"Failed to download image {i+1} from {img_url}: {e}")

            # Ask the user to scroll down
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
