#!/usr/bin/env python3

import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

def get_forms(url):
    # This will return all user input forms from The HTML content
    soup = bs(requests.get(url).content, 'html.parser')
    return soup.find_all('form')

def get_form_details(form):
    # This will extract all possible useful info about a HTML form

    details = {}

    # Get the form action
    action = form.attrs.get('action').lower()

    # Get the form method
    method = form.attrs.get('method', 'get').lower()

    # Get all input details
    inputs = []
    for input_tag in form.find_all('input'):
        input_type = input_tag.attrs.get('type', 'text')
        input_name = input_tag.attrs.get('name')
        inputs.append({'type':input_type, 'name':input_name})

    # Putting everything in the dictionary
    details['action'] = action
    details['method'] = method
    details['inputs'] = inputs

    return details

def submit_forms(form_details, url, value):
    """
    Submits a form given in `form_details`
    Params:
        form_details (list): a dictionary that contain form information
        url (str): the original URL that contain that form
        value (str): this will be replaced to all text and search inputs
    Returns the HTTP Response after form submission
    """

    # Construct the full url if the url provided in action is relative
    target_url = urljoin(url, form_details['action'])
    
    # Get inputs
    inputs = form_details['inputs']
    data = {}
    for input in inputs:
        # replace all text and search values with "value"
        if input['type'] == 'text' or input['type'] == 'search':
            input['value'] = 'value'
        input_name = input.get('name')
        input_value = input.get('value')
        if input_name and input_value:
            # If input name and value are not None, add them to the data of form submission
            data[input_name] = input_value
    
    if form_details['method'] == 'post':
        return requests.post(target_url. data==data)
    elif form_details['method'] == 'get':
        return requests.get(target_url, params=data)

def xss_scan(url):
    """
    Given a `url`, it prints all XSS vulnerable forms and 
    returns True if any is vulnerable, False otherwise
    """

    # Get all the forms from the url
    forms = get_forms(url)
    print(f'[+] Detected {len(forms)} forms on {url}')
    js_script = '<script>alert("pwn")</script>'

    # Returning value
    is_vuln = False

    # Iterate over all forms
    for form in forms:
        form_details = get_form_details(form)
        content = submit_forms(form_details, url, js_script).content.decode()
        if js_script in content:
            print(f'[+] XSS detectedon {url}')
            print(f'[*] Form details: ')
            pprint(form_details)
            is_vuln = True
    
    return is_vuln


if __name__ == '__main__':
    url = input('Please enter a URL to scan: ')
    print(xss_scan(url))