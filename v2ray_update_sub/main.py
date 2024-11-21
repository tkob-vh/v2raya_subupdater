import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time

def parse_args():
    parser = argparse.ArgumentParser(description='Update V2Ray subscription with login credentials')
    parser.add_argument('-u', '--username', required=True, help='Username for login')
    parser.add_argument('-p', '--password', required=True, help='Password for login')
    return parser.parse_args()

def main():
    args = parse_args()
    
    options = Options()
    # options.add_argument("--headless")
    options.set_preference("network.proxy.type", 0)
    
    driver = webdriver.Firefox(options=options)
    driver.get("http://127.0.0.1:2017")

    # Add login functionality
    username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

    # Use credentials from command line arguments
    username_input.send_keys(args.username)
    password_input.send_keys(args.password)

    # Find and click the login button using the correct selector
    login_button = driver.find_element(By.CSS_SELECTOR, "button.button.is-primary")
    login_button.click()

    # Add a small delay to allow the login to complete
    time.sleep(2)

    target_row = driver.find_element(
        By.XPATH, "/html/body/div[1]/section/div/div[2]/section/div[3]/div/div/div[2]/table/tbody/tr[3]/td[7]/div/button[1]")


    # Cancel the connection.
    cancel_button = target_row.find_element(
        By.XPATH, "/html/body/div[1]/section/div/div[2]/section/div[3]/div/div/div[2]/table/tbody/tr[3]/td[7]/div/button[1]")
    cancel_button.click()

    # Switch to the subscription page
    subscription_buttion = driver.find_element(
        By.XPATH, "//*[@id='114-label']")
    subscription_buttion.click()


    # Update the subscription
    update_button = driver.find_element(
        By.XPATH, "/html/body/div[1]/section/div/div[2]/section/div[1]/div/div/div[2]/table/tbody/tr/td[7]/div/button[1]")
    update_button.click()

    time.sleep(2)

    # Switch back to the servers page
    servers_button = driver.find_element(By.XPATH, "//*[@id='136-label']")
    servers_button.click()

    time.sleep(2)

    # After switching back to servers page, we need to re-fetch the target row
    time.sleep(2)  # Ensure the page has loaded
    target_row = driver.find_element(
        By.XPATH, "/html/body/div[1]/section/div/div[2]/section/div[3]/div/div/div[2]/table/tbody/tr[3]/td[7]/div/button[1]")

    # Select the connection (now using the fresh element reference)
    select_button = target_row
    select_button.click()

    # Start running
    status_tag = driver.find_element(By.ID, value="statusTag")
    status_tag.click()

if __name__ == '__main__':
    main()
