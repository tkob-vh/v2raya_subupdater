import argparse
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import logging
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# Set up logging
def setup_logging():
    log_dir = Path.home() / '.local' / 'log' / 'v2ray-updater'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'v2ray_updater.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('v2ray_updater')

def load_config():
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def parse_args():
    parser = argparse.ArgumentParser(description='Update V2Ray subscription with login credentials')
    parser.add_argument('-u', '--username', required=True, help='Username for login')
    parser.add_argument('-p', '--password', required=True, help='Password for login')
    return parser.parse_args()

def update_subscription():
    logger = logging.getLogger('v2ray_updater')
    args = parse_args()
    config = load_config()
    logger.info("Starting subscription update process")
    
    options = Options()
    options.add_argument("--headless")
    options.set_preference("network.proxy.type", 0)

    try:
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
            
            time.sleep(0.5)

            # Check if on the correct servers page
            current_page = driver.find_element(By.XPATH, "//nav//li[@role='tab' and @aria-selected='true']//span").text
            if current_page != config['subscription']:
                logger.info("Switching to {} page".format(config['subscription']))
                server_tab = driver.find_element(By.XPATH, f"//nav//li[contains(., '{config['subscription']}')]")
                server_tab.click()
                time.sleep(0.5)

            logger.info("Checking for active connections")
            active_connections = driver.find_elements(By.XPATH, "//tr[contains(@class, 'is-connected-running')]")

            if active_connections:
                logger.info("Disconnecting current active server")
                for connection in active_connections:
                    connection_id = connection.find_element(By.XPATH, ".//td[2]").text
                    disconnect_button = WebDriverWait(connection, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class, 'button is-small is-warning')]"))
                    )
                    disconnect_button.click()
                    logger.info(f"Disconnected server with ID: {connection_id}")
            else:
                logger.info("No active connections found")


            # Switch to SUBSCRIPTION page
            subscription_tab = driver.find_element(By.XPATH, "//nav//li[contains(., 'SUBSCRIPTION')]")
            if not subscription_tab.get_attribute("aria-selected") == "true":
                logger.info("Switching to SUBSCRIPTION tab")
                subscription_tab.click()

            time.sleep(0.5)  # Wait for the tab to switch


            logger.info("Updating all subscriptions on the page")
            # Locate all rows in the subscription table
            subscription_rows = driver.find_elements(By.XPATH, "/html/body/div[1]/section/div/div[2]/section/div[1]/div/div/div[2]/table//tbody/tr")

            for row in subscription_rows:
                update_button = row.find_element(By.XPATH, ".//button[contains(@class, 'button is-small is-warning is-outlined')]")
                update_button.click()
                logger.info("Clicked update button for subscription row")
                time.sleep(0.5)  # Wait for the update to process



            # Check if on the correct servers page
            current_page = driver.find_element(By.XPATH, "//nav//li[@role='tab' and @aria-selected='true']//span").text
            if current_page != config['subscription']:
                logger.info("Switching to JMSSUB.NET page")
                server_tab = driver.find_element(By.XPATH, f"//nav//li[contains(., '{config['subscription']}')]")
                server_tab.click()
                time.sleep(0.5)  # Wait for the tab to switch


            logger.info(f"Connecting to server: {config['server_name']}")
            time.sleep(1)
            select_button = driver.find_element(By.XPATH, f"//td[contains(text(), '{config['server_name']}')]//ancestor::tr//button[contains(@class, 'button is-small is-warning is-outlined')]")
            select_button.click()
            logger.info("Server connection initiated")

            # Click the Start button to start the service
            start_button = driver.find_element(By.ID, value="statusTag")
            start_button.click()
            logger.info("Service started successfully")

            logger.info("Subscription update completed successfully")
            
        except NoSuchElementException as e:
            logger.error(f"Element not found: {str(e)}")
            raise
        except WebDriverException as e:
            logger.error(f"WebDriver error: {str(e)}")
            raise
        finally:
            logger.info("Closing browser")
            driver.quit()
            
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        raise

def main():
    global logger
    logger = setup_logging()
    logger.info("Starting V2Ray updater service")
    
    # Run the update_subscription function once
    update_subscription()

if __name__ == '__main__':
    main()
