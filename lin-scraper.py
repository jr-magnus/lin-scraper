#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 18:41:04 2020

@author: jr-magnus
"""
from bs4 import BeautifulSoup
from time import mktime, strptime
import requests
import gui
import re


def login_to_bbo():
    session = requests.session()

    while True:
        credentials = gui.bbo_credentials()
        if credentials is None:
            exit()
        response = session.post(
            f'https://www.bridgebase.com/myhands/myhands_login.php?t=%2Fmyhands%2Findex.php%3F&offset=0',
            data={'username': credentials[0], 'password': credentials[1]}
        )
        if response.text.find('Username or password incorrect, please try again') == -1:
            break
        else:
            gui.login_unsuccessful()

    return session, credentials[0]


def search_window(username_default):
    while True:
        try:
            details = gui.specify_search_window(username_default)
            if details is None:
                exit()
            username, start_input, end_input = details
            start_time = int(mktime(strptime(start_input, "%d.%m.%Y")))
            end_time = int(mktime(strptime(end_input, "%d.%m.%Y"))) + 60*60*24
            return username, start_time, end_time
        except ValueError as e:
            gui.myhands_value_error(e)


def download_myhands_page(session, username):
    username, start_time, end_time = search_window(username)
    return session.get(
        f"https://www.bridgebase.com/myhands/hands.php?offset=0&username={username}&start_time={start_time}&end_time={end_time}"
    ).text.strip()


def pick_tournaments(soup):
    choices = [tr.text for tr in soup.find_all(class_="tourneyName")]
    if len(choices) == 1:
        choices.append('')
    elif len(choices) == 0:
        return None
    chosen = gui.tournament_picker(choices)
    if chosen is None:
        return []
    return [t for t in chosen if t != '']


def extract_lin_links(soup, tourneys):
    try:
        lin_map = {}
        trs = soup.find_all("tr")
        del trs[0:4]

        for row in trs:
            if row.get("class", []) == ["tourneySummary"]:
                tourneyName = row.find(class_="tourneyName").text
                if tourneyName in tourneys:
                    lin_map[tourneyName] = []
                    included = True
                else:
                    included = False
            if (row.get("class", []) == ["team"] or row.get("class", []) == ["tourney"]) and included:
                lin_url = row.find(class_="movie").find_all("a")[1]["href"]
                if lin_url.startswith("fetchlin"):
                    lin_url = f"https://www.bridgebase.com/myhands/{lin_url}"
                lin_map[tourneyName].append(lin_url)

        return lin_map
    except Exception as e:
        gui.exception(e)
        exit()


def create_safe_filename(filename):
    safe_name = "".join(c if c.isalnum() else "_" for c in filename)
    return re.sub(r"_+", r"_", safe_name).strip("_")


def download_lins(session, lin_map):
    dir_path = gui.directory()
    gui.download_started()
    try:
        for tourneyName, urls in lin_map.items():
            for num, url in enumerate(urls, start=1):
                path_to_lin = "{}/{}_{:0>2d}.lin".format(dir_path, create_safe_filename(tourneyName), num)
                with open(path_to_lin, "w", encoding="utf-8") as f:
                    f.write(session.get(url).text.strip())
    except Exception as e:
        gui.exception(e)
        exit()
    gui.download_finished(dir_path)


if __name__ == '__main__':
    bbo_session, bbo_username = login_to_bbo()

    while True:
        myhands_soup = BeautifulSoup(download_myhands_page(bbo_session, bbo_username), 'html.parser')
        included_tourneys = pick_tournaments(myhands_soup)

        if included_tourneys is None:
            gui.no_tournaments_found()
            continue

        if len(included_tourneys) < 1:
            gui.no_tournaments_chosen()
            continue

        break

    download_lins(bbo_session, extract_lin_links(myhands_soup, included_tourneys))
