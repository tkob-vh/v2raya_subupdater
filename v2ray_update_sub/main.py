import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import schedule
import logging
from datetime import datetime
import os
from pathlib import Path

# Set up logging
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path.home() / '.cache' / 'v2ray-updater' / 'log'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    log_file = log_dir / f'v2ray_updater.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )
    return logging.getLogger('v2ray_updater')

def parse_args():
    parser = argparse.ArgumentParser(description='Update V2Ray subscription with login credentials')
    parser.add_argument('-u', '--username', required=True, help='Username for login')
    parser.add_argument('-p', '--password', required=True, help='Password for login')
    return parser.parse_args()

def update_subscription():
    logger = logging.getLogger('v2ray_updater')
    try:
        args = parse_args()
        logger.info("Starting subscription update process")
        
        options = Options()
        options.add_argument("--headless")
        options.set_preference("network.proxy.type", 0)
        
        logger.info("Initializing Firefox webdriver")
        driver = webdriver.Firefox(options=options)
        
        try:
            logger.info("Accessing web interface")
            driver.get("http://127.0.0.1:2017")

            logger.info("Attempting login")
            username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            username_input.send_keys(args.username)
            password_input.send_keys(args.password)

            login_button = driver.find_element(By.CSS_SELECTOR, "button.button.is-primary")
            login_button.click()
            logger.info("Login completed")

            time.sleep(2)

            logger.info("Finding and canceling existing connection")
            target_row = driver.find_element(
                By.XPATH, "/html/body/div[1]/section/div/div[2]/section/div[3]/div/div/div[2]/table/tbody/tr[3]/td[7]/div/button[1]")
            cancel_button = target_row
            cancel_button.click()
            logger.info("Connection canceled")

            logger.info("Switching to subscription page")
            subscription_button = driver.find_element(By.XPATH, "//*[@id='114-label']")
            subscription_button.click()

            logger.info("Updating subscription")
            update_button = driver.find_element(
                By.XPATH, "/html/body/div[1]/section/div/div[2]/section/div[1]/div/div/div[2]/table/tbody/tr/td[7]/div/button[1]")
            update_button.click()
            time.sleep(2)

            logger.info("Switching back to servers page")
            servers_button = driver.find_element(By.XPATH, "//*[@id='136-label']")
            servers_button.click()
            time.sleep(2)

            logger.info("Selecting new connection")
            target_row = driver.find_element(
                By.XPATH, "/html/body/div[1]/section/div/div[2]/section/div[3]/div/div/div[2]/table/tbody/tr[3]/td[7]/div/button[1]")
            select_button = target_row
            select_button.click()

            logger.info("Starting connection")
            status_tag = driver.find_element(By.ID, value="statusTag")
            status_tag.click()
            
            logger.info("Subscription update completed successfully")
            
        except Exception as e:
            logger.error(f"Error during subscription update: {str(e)}")
            raise
        finally:
            logger.info("Closing browser")
            driver.quit()
            
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        raise

def main():
    logger = setup_logging()
    logger.info("Starting V2Ray updater service")
    
    # Schedule the job
    schedule.every(2).hours.do(update_subscription)
    logger.info("Scheduled update_subscription to run every 2 hours")
    
    # Run immediately on start
    try:
        logger.info("Running initial update")
        update_subscription()
    except Exception as e:
        logger.error(f"Initial update failed: {str(e)}")
    
    # Keep the script running
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == '__main__':
    main()
