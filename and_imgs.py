from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# URL to access
url = sys.argv[1]
password = sys.argv[2]
endstring = "user.php"
finished = False
a = urlparse(url)

# Create a folder based on the URL path
folder_name = os.path.basename(a.path)

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Create a requests session
session = requests.Session()

# Set headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
}

# Function to extract cookies from Selenium to requests session
def set_cookies_to_requests(driver, session):
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])
    
# Main loop for downloading images
while not finished:
    result = session.get(url, headers=headers)
    
    # Check for the warning page
    if "warn.php" in result.url:
        # Set up Selenium
        chrome_options = Options()
        chrome_options.add_argument(f'user-agent={headers["User-Agent"]}')
        chrome_service = Service("/data/data/com.termux/files/home/chromedriver")  # Path to chromedriver on Android
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # Open the warning page
        driver.get(result.url)

        try:
            # Wait for the button to be clickable and click it
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='Нажми, чтобы подтвердить и продолжить']"))
            )
            button.click()
            print("Confirmed and continued to the main page.")

            # Update the URL to the main page after clicking the button
            url = driver.current_url  # Use the new URL from Selenium
            
            # Extract cookies from Selenium and set them in the requests session
            set_cookies_to_requests(driver, session)

            if "passchk.php" in url:
                try:
                    password_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "pwd"))  # Name of the password input field
                    )
                    password_field.send_keys(password)  # Send the password

                    # Locate and click the submit button
                    submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
                    submit_button.click()

                    print("Password submitted, proceeding to the main page.")
                    
                    # Update the URL to the main page after submitting the password
                    url = driver.current_url  # Use the new URL from Selenium

                    # Extract cookies from Selenium and set them in the requests session
                    set_cookies_to_requests(driver, session)

                except Exception as e:
                    print(f"Error submitting password: {e}")

        except Exception as e:
            print(f"Error clicking the button: {e}")
            driver.quit()
            break
        finally:
            driver.quit()  # Close the Selenium session
        
    else:   
        soup = BeautifulSoup(result.content, "html.parser")
        element_by_id = soup.find("a", {"id": "next_url"})

        if element_by_id:
            next_image = element_by_id.get("href")
            find_image = element_by_id.find("img")
            current_image = find_image.get("src")
            
            # Extract the image URL
            image_source = element_by_id.find("source", {"type": "image/jpeg"})
            if image_source:
                image_url = image_source['srcset']
                dl_image = "https:" + image_url

                # Download the image
                image_name = dl_image.split("/")[-1]
                response = session.get(dl_image, headers=headers)
                image_path = os.path.join(folder_name, image_name)

                # Save the image locally
                if response.status_code == 200:
                    with open(image_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Image '{image_name}' downloaded successfully.")

                # Prepare for the next URL
                url = "https://imgsrc.ru" + next_image  # Update the URL for the next image

            else:
                print("No image source found.")
                finished = True
        else:
            print("No next_url found, finishing.")
            finished = True
