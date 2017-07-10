from search import SearchManager
import time
import random
import datetime
import subprocess
import os
import sys
import json

class WeChargeEventHandler():
    report = {}
    def __init__(self):
        self.events = {
            'click_next_before_click': lambda x, y: self.before_click_next(),
            'set_google_search_preferences_click_slider' : lambda x, y: time.sleep(100000),
            'click_link_domain_contains_finished' : self.finished_query
        }

    def before_click_next(self):
        secs = random.randint(1, 6)
        print 'sleep {0} seconds to prevent google from flagging as robot'.format(secs)
        time.sleep(secs)

    def set_query_info(self, site, query):
        self.query = query
        self.site = site
        if not site in self.report:
            self.report[site] = {}

    def finished_query(self, event_name, event_details):
        self.report[self.site][self.query] = event_details

    def handle_event(self, event_name, event_details=None):
        print "{0}: {1}".format(event_name, event_details)
        if event_name in self.events:
            self.events[event_name](event_name, event_details)

event_handler = WeChargeEventHandler()

search = SearchManager(event_handler)

try:
    sites = {}
    results_per_page = 10
    number_of_pages = 1

    # load sites and preferences
    use_json = False
    if use_json:
        with open('configuration.txt') as sites_file:
            sites = json.load(sites_file)
    else:
        with open('configuration.txt') as sites_file:
            lines = sites_file.readlines()
            line_index = 0
            while(line_index < len(lines)):
                line = lines[line_index]
                if(line[0] == '#' or line.strip() == ''):
                    pass
                elif(line.startswith('site:')):
                    site_name = line.split('site:')[1].strip()
                    sites[site_name] = sites[site_name] if site_name in sites else []
                    while(True):
                        line_index = line_index + 1
                        line = lines[line_index]
                        if line.strip() == '' or line[0] == '#':
                            pass
                        elif line.startswith('site:'):
                            break
                        else:
                            sites[site_name].append(line.strip())
                        line_index = line_index + 1
                elif(line.startswith('results per page:')):
                    results_per_page = int(line.split('results per page:')[1].strip())
                elif(line.startswith('number of pages:')):
                    number_of_pages = int(line.split('number of pages:')[1].strip())
                line_index = line_index + 1

    print sites
    sys.exit()
    search_preferences = {
        'results_per_page' : results_per_page
    }

    search.set_google_search_preferences(search_preferences)

    click_options = {
        'number_of_nexts' : number_of_pages - 1
    }

    def query(search_query, site_name):
        event_handler.set_query_info(site_name, search_query)
        search.search_query(search_query)
        search.click_link_domain_contains(site_name, click_options)

    # start time
    start_time_string = datetime.datetime.now().strftime('%Y-%m-%d %Hh%Mm%Ss')

    # execute
    for site_name, search_terms in sites.items():
        [query(search_term, site_name) for search_term_idx, search_term in enumerate(search_terms)]

    # end time
    end_time_string = datetime.datetime.now().strftime('%Y-%m-%d %Hh%Mm%Ss')

    query_report = event_handler.report

    # write output to text file
    from bottle import SimpleTemplate

    def stringify_query_report(query_results):
        f = open('query_report.stpl', 'r')
        template_string = f.read()
        template = SimpleTemplate(template_string)
        return template.render({'query_report' : query_report})

    stringed = stringify_query_report(query_report)
    output_file_name = 'report {0} to {1}.txt'.format(start_time_string, end_time_string)
    f = open(output_file_name, 'w')
    f.write(stringed)
    f.close()

    # open text file https://stackoverflow.com/questions/434597/open-document-with-default-application-in-python
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', output_file_name))
    elif os.name == 'nt':
        os.startfile(output_file_name)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', output_file_name))



except Exception as e:
    print e
    search.quit()
