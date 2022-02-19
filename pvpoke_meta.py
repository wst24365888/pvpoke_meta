from multiprocessing import cpu_count
import time
from typing import List
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ProcessPoolExecutor, as_completed
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class Pokemon:
    def __init__(self, name: str, score: str):
        self.name = name
        self.score = score

def get_new_driver(headless: bool = True) -> WebDriver:
    chrome_options = webdriver.ChromeOptions()
    if headless:        
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
    service = Service('./chromedriver.exe')
    service.start()

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('https://pvpoketw.com/battle/')

    time.sleep(2)
    wait = WebDriverWait(driver, 2)

    muilti_battle: WebElement = wait.until(EC.element_to_be_clickable(driver.find_element(By.CSS_SELECTOR, "#main > div.section.league-select-container.white > div > a:nth-child(2)")))
    muilti_battle.click()
    
    return driver

def get_score(pokemon: Pokemon) -> Pokemon:
    driver = get_new_driver()
    wait = WebDriverWait(driver, 2)

    try:
        pokemon_selector_el: WebElement = wait.until(EC.element_to_be_clickable(driver.find_element(By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(1) > select")))
        pokemon_selector: Select = Select(pokemon_selector_el)

        pokemon_selector.select_by_visible_text(pokemon.name)

        battle_button: WebElement = wait.until(EC.element_to_be_clickable(driver.find_element(By.CSS_SELECTOR, "#main > div.section.battle > button.battle-btn.button")))
        battle_button.click()

        time.sleep(0.5)

        url = driver.current_url
        driver.get(url)

        time.sleep(1.5)

        score_el: WebElement = wait.until(EC.element_to_be_clickable(driver.find_element(By.CSS_SELECTOR, "#main > div.section.battle > div:nth-child(6) > div > div > div > div > div.label.rating.star > span")))
        pokemon.score = score_el.text
    except:
        pass

    driver.quit()

    print(f'{pokemon.name}: {pokemon.score}')

    return pokemon


if __name__ == '__main__':
    driver = get_new_driver()
    wait = WebDriverWait(driver, 2)

    pokemon_selector_el: WebElement = wait.until(EC.element_to_be_clickable(driver.find_element(By.CSS_SELECTOR, "#main > div.section.poke-select-container.multi > div:nth-child(1) > select")))
    pokemon_list: List[str] = pokemon_selector_el.text.split('\n')

    print("Length of pokemon list: {}".format(len(pokemon_list)))

    driver.quit()

    results: List[Pokemon] = []

    with ProcessPoolExecutor(cpu_count() - 1) as executor:
        futures = [executor.submit(get_score, Pokemon(pokemon.strip(), -1)) for pokemon in pokemon_list[1:]]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda x: int(x.score), reverse=True)

    with open(f'pvpoke_meta_{int(time.time())}.csv', 'w') as f:
        f.write('name,score\n')
        for pokemon in results:
            f.write(f'{pokemon.name},{pokemon.score}\n')
    