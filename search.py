from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from urlparse import urlparse
import time
import urllib

class SearchManager():
    def __init__(self, event_handler):
        self.driver = webdriver.Chrome()
        self.event_handler = event_handler

    def set_google_search_preferences(self, options={}):
        # need to go google search first to init cookies
        url = "https://www.google.com.sg/search?q=preferences"
        self.driver.get(url)

        url = "https://www.google.com.sg/preferences"
        self.driver.get(url)

        if 'results_per_page' in options:
            self.handle_event('set_google_search_preferences_set_results_per_page', options['results_per_page'])

            # don't show instant results
            radio_css = "#instant-radio .jfk-radiobutton[data-value='2']"

            never_show_instant_results_radio_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, radio_css))
            )
            never_show_instant_results_radio_button.click()
            self.handle_event('set_google_search_preferences_click_dont_show_instant_results', radio_css)

            # 100%
            # cannot click slider, click form instead
            # slider_css = "#resnum .slmarker:last-child"
            # slider_button = WebDriverWait(self.driver, 5).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, slider_css))
            # )
            # slider_button.click()
            # self.handle_event('set_google_search_preferences_click_slider', slider_css)

            # webdriver aims to automate user input, set_attribute does not exist
            # percentage_field_css = "#resnum input[name='num']"
            # percentage_field = WebDriverWait(self.driver, 5).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, percentage_field_css))
            # )
            results_per_page = options['results_per_page']
            # percentage_field.set_attribute('value', percentage)

            self.driver.execute_script('document.querySelector("#resnum input[name=\'num\']").value = ' + str(results_per_page))
            self.handle_event('set_google_search_preferences_results_per_page', results_per_page)

            # save
            save_button_css = "#form-buttons [role=button]"
            save_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, save_button_css))
            )
            save_button.click()
            self.handle_event('set_google_search_preferences_click_save', save_button_css)

            self.driver.switch_to_alert().accept()
            self.handle_event('set_google_search_preferences_accept_save', save_button_css)

    def search_query(self, query, options={}):
        self.handle_event('search_query', query)
        query_params = {
            'q' : query
        }
        query_string = urllib.urlencode(query_params)
        url = 'https://www.google.com.sg/search?{0}'.format(query_string)
        self.driver.get(url)

        # self.driver.get('https://www.google.com.sg')
        # input_css = "input.gsfi:not([disabled])"
        # try:
        #     inputElement = WebDriverWait(self.driver, 5).until(
        #         EC.presence_of_element_located((By.CSS_SELECTOR, input_css))
        #     )
        #     inputElement.send_keys(query)
        #     time.sleep(2)
        #     inputElement.send_keys(Keys.ENTER)
        #     time.sleep(2)
        # finally:
        #     pass

    # google search at times recommends spelling corrections, this ensures original search term is searched
    def assert_original_spelling(self):
        spell_orig_css = '.spell_orig a'
        try:
            spell_orig = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, spell_orig_css))
            )
            self.handle_event('search_query_click_original')
            spell_orig.click()
        except NoSuchElementException:
            pass
        except Exception as e:
            print e

    def click_link_domain_contains(self, domain, options={}):
        number_of_nexts = options['number_of_nexts'] if 'number_of_nexts' in options else 0
        click_results = []
        results_tab_name = self.driver.window_handles[0]

        for page_number in range(number_of_nexts):
            self.assert_original_spelling()
            page_results = {
                'page_number' : page_number + 1, # 1-based for readability
                'clicked_addresses' : []
            }
            click_results.append(page_results)
            self.handle_event('search_links_in_page', {'page_number' : page_number})
            search_results = self.driver.find_elements_by_css_selector('.g')
            for search_result_index, search_result in enumerate(search_results):
                try:
                    link = search_result.find_element_by_css_selector('h3.r a')
                    actions = ActionChains(self.driver)
                    actions.move_to_element(link).perform()
                    link_address = link.get_attribute('href')
                    domain_and_address = {'domain' : domain, 'address' : link_address}
                    self.handle_event('click_link_domain_contains_compare', domain_and_address)
                    if domain in urlparse(link_address).netloc:
                        self.handle_event('click_link_domain_contains_compare_found', domain_and_address)
                        # open in new tab
                        open_in_new_tab = ActionChains(self.driver)
                        open_in_new_tab.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
                        # switch back to tab
                        #self.driver.switch_to.window(window_name=results_tab_name)
                        page_results['clicked_addresses'].append({
                            'search_result_index' : search_result_index,
                            'link_address' : link_address
                        })
                    else:
                        self.handle_event('click_link_domain_contains_compare_not_match', domain_and_address)
                except NoSuchElementException:
                    self.handle_event('click_link_domain_contains_error', '<a> element not found')
                except Exception as e:
                    self.handle_event('click_link_domain_contains_error', e)
            self.click_next()
            time.sleep(3)

        self.handle_event('click_link_domain_contains_finished', click_results)
        time.sleep(3)

    def click_next(self):
        self.handle_event('click_next')
        # ensure clicked
        time.sleep(1)
        try:
            next_button = self.driver.find_element_by_css_selector('a#pnnext.pn')
            actions = ActionChains(self.driver)
            actions.move_to_element(next_button).click(next_button)
            self.handle_event('click_next_before_click')
            actions.perform()
        except NoSuchElementException:
            self.handle_event('click_next_button_not_found')
        except StaleElementReferenceException:
            self.handle_event('click_next_button_removed_from_dom')
            self.click_next()
        except Exception as e:
            self.handle_event('click_next_button_error', e)
            self.click_next()

    def handle_event(self, event_name, event_details=None):
        self.event_handler.handle_event(event_name, event_details)

    def quit(self):
        self.driver.quit()
