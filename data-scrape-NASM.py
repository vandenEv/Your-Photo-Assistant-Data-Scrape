import requests
from bs4 import BeautifulSoup
import csv
import re
from selenium import webdriver  


def scrape_company_data(base_url, num_pages):
    data = []  

    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')

        company_blocks = soup.find_all('li', class_='smm-block') 
        process_company_blocks(company_blocks, data)

        pagination_links = soup.find_all('a', class_='a.page_link')  
        for link in pagination_links:
            page_url = link['href']
            response = requests.get(page_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                company_blocks = soup.find_all('div', class_='smm-block') 
                process_company_blocks(company_blocks, data)

        
        next_page_link = soup.find('a', class_='a.next_link')  
        driver = webdriver.Chrome() 
        
        for _ in range(1, num_pages): 
            if not next_page_link:
                break

            driver.get(base_url)  
            next_page_link_element = driver.find_element_by_class_name(
                'a.next_link')  
            next_page_link_element.click()

            soup = BeautifulSoup(driver.page_source, 'lxml')
            company_blocks = soup.find_all('div', class_='smm-block')  
            process_company_blocks(company_blocks, data)

            next_page_link = soup.find('a', class_='a.next_link')  

        driver.quit()  

        with open('company_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['Company Name', 'Personal Name', 'Phone Number', 'Alternative Phone Number', 'Service Area',
                          'Email Address', 'Company Website']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print("Data scraped and saved to company_data.csv")
    else:
        print("Request failed with status code:", response.status_code)


def process_company_blocks(company_blocks, data):

    for company_block in company_blocks:
        company_name = company_block.find('h5').text.strip()
        left_column = company_block.find('div', class_='col-md-4')  
        right_column = company_block.find('div', class_='col-md-5')  

        personal_name = left_column.find('h5').text.strip() 

        phone_number_element = left_column.find('b', string="Phone:")
        if phone_number_element:
            phone_number_text = phone_number_element.next_sibling.strip()
            phone_number_search = re.search(r"\d{3}-\d{3}-\d{4}", phone_number_text)
            if phone_number_search: 
                phone_number = phone_number_search.group()
            else:
                
                phone_number = "N/A" 
        else:
            phone_number = "N/A"  

        alternative_phone_element = left_column.find('b', string="Alternative Phone Number:")
        if alternative_phone_element:
            alternative_phone_text = alternative_phone_element.next_sibling.strip()
            alternative_phone_search = re.search(r"\d{3}-\d{3}-\d{4}", alternative_phone_text)
            if alternative_phone_search:  
                alternative_phone_number = alternative_phone_search.group()
            else:
                
                alternative_phone_number = "N/A"  
        else:
            alternative_phone_number = "N/A" 

        service_area_element = right_column.find('b', string="Service Area:")
        if service_area_element:
            service_area_text = service_area_element.next_sibling.strip()
            service_area = re.search(r"[\w\s]+", service_area_text).group() 
        else:
            service_area = "N/A"  

        email_address_element = right_column.find('a', href=lambda href: href and href.startswith('mailto:'))
        if email_address_element:
            email_address = email_address_element.text.strip()
        else:
            email_address = "N/A"  

        company_website = right_column.find('a', href=lambda href: href.startswith(
            'http')).text.strip()  

        data.append({
            'Company Name': company_name,
            'Personal Name': personal_name,
            'Phone Number': phone_number,
            'Alternative Phone Number': alternative_phone_number,
            'Service Area': service_area,
            'Email Address': email_address,
            'Company Website': company_website,
        })



num_pages = 5
url = "https://www.nasmm.org/find-a-move-manager/list/?zip=11215&radius=50&submit=Search"
scrape_company_data(url, num_pages)
