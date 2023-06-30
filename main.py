import math
import requests
import bs4
import pandas as pd


def get_request_list(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    return resp


def soupify_response(resp):
    soup = bs4.BeautifulSoup(resp.text, 'html.parser')
    profiles = soup.find_all("a", {"class": "ProfileAnchor"})
    links = get_links_from_soup(profiles)
    names = get_names_from_soup(profiles)
    df = pd.DataFrame(data=[links, names]).transpose()
    return df


def get_links_from_soup(soup):
    return [link.get('href') for link in soup]


def get_names_from_soup(soup):
    names = [profile.contents[0].contents[0].split(" ") for profile in soup]
    skips = ['jr', 'sr', 'iii', 'iv', 'v', 'vi', "acnp", "cna", "crna", "pa-c", "np", "pmhnp", "fnp", "ccp"]
    parsed_names = list()
    for name in names:
        tmp = name[0] + " "
        if name[-1].lower() in skips:
            tmp += name[-2]
        else:
            tmp += name[-1]
        parsed_names.append(tmp)
    return parsed_names


def main():
    df = pd.DataFrame()
    page_n = 1
    base_url = f'https://www.forresthealth.org/app/doctors/results.aspx?searchId=efb922ce-4916-ee11-a85a-000d3a611ea2&sort=7&page={page_n}'
    resp = get_request_list(base_url)
    idx = resp.text.find("TotalRecords") + len("TotalRecords") + 2
    max_pages = math.ceil(int(resp.text[idx:idx + 10].split(",")[0]) / 10)
    for page_n in range(1, max_pages+1):
        resp = get_request_list(base_url)
        if resp.status_code != 200:
            break
        found_df = soupify_response(resp)
        df = pd.concat([df, found_df], axis=0)
        base_url = base_url[:-len(str(page_n - 1))] + str(page_n)


if __name__ == '__main__':
    main()
