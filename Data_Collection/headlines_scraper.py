# Libraries and Dependencies
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def cleanup(line):
    cleaned_text = str.maketrans('', '', r"-()\"#/@;:<>{}-=~|.?,")
    return str(line.translate(cleaned_text)).lower()


def get_soup(request, element, class_value):
    html_page = requests.get(request).text
    soup = BeautifulSoup(html_page, 'lxml')
    return soup.find_all(element, class_=class_value)


def create_headlines_array(headlines_list):
    list_of_headlines = []
    for li in headlines_list:
        if li.text != "":
            list_of_headlines.append(' '.join(li.text.split()))  # Removes tabs, newlines, and gets text from HTML

    return list_of_headlines


def format_to_table(headlines, stock):
    title = 'Recent headlines for ' + stock
    headlines_table = pd.DataFrame(columns=[title])

    for line in headlines:
        headlines_table = headlines_table.append({title: cleanup(line)}, ignore_index=True)

    return headlines_table


def get_morningstar_headlines(stock):
    request = 'https://www.morningstar.com/stocks/xnas/' + stock.lower() + '/news'
    headlines_list = get_soup(request, 'a', 'mdc-link mdc-news-module__headline mds-link mds-link--no-underline')
    return create_headlines_array(headlines_list)


def get_usa_today_headlines(stock):
    request = 'https://www.usatoday.com/search/?q=' + stock
    headlines_list = get_soup(request, 'a', 'gnt_se_a gnt_se_a__hd gnt_se_a__hi')
    return create_headlines_array(headlines_list)


def get_reuters_headlines(stock):
    request = 'https://www.reuters.com/search/news?blob=' + stock
    headlines_list = get_soup(request, 'h3', 'search-result-title')
    return create_headlines_array(headlines_list)


def get_cnbc_headlines(stock):
    request = 'https://www.cnbc.com/quotes/?symbol=' + stock.lower() + '&qsearchterm=' + stock.lower() + '&tab=news'
    li_list = get_soup(request, 'div', 'assets')

    list_of_headlines = []
    for li in li_list:
        headline = li.select_one("span")
        if headline.text != "":
            list_of_headlines.append(headline.text)

    return list_of_headlines


def main():
    # Stock Ticker
    stock = 'AAPL'
    title = 'Recent headlines for ' + stock
    print("\nFetching headlines for " + stock + "...\n")

    # List of sources
    source_1 = np.array(get_cnbc_headlines(stock))
    source_2 = np.array(get_reuters_headlines(stock))
    source_3 = np.array(get_morningstar_headlines(stock))
    source_4 = np.array(get_usa_today_headlines(stock))

    # Combining all sources, initializing data frame
    overall_headlines = np.concatenate((source_1, source_2, source_3, source_4), axis=None)
    overall_headlines = list(overall_headlines)
    headlines_table = pd.DataFrame(columns=[title])

    # Formatting to a table
    if len(overall_headlines) != 0:
        headlines_table = format_to_table(overall_headlines, stock)
    else:
        print("Invalid ticker or no headlines available.")

    # Printing out formatted table of headlines
    headlines_table.drop_duplicates(subset=title, keep=False, inplace=True)
    print(headlines_table)


if __name__ == "__main__":
    main()
