#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 18:41:04 2020

@author: jr-magnus
"""
from bs4 import BeautifulSoup
import requests
from time import mktime, strptime, strftime, localtime
import easygui
import re


GUI_TITLE = 'LIN Scraper jr-magnus@github.com'
SECONDS_IN_DAY = 60*60*24
LOGIN_UNSUCCESSFUL = 'Username or password incorrect, please try again'
EXCEPTION_MESSAGE = """
This program has encountered a critical error and will now terminate. 
Please report this problem at github.com/jr-magnus/lin-scraper.\n\n\n
"""


def get_credentials():
    return easygui.multpasswordbox(
        msg='Log in to BBO',
        title=GUI_TITLE,
        fields=['Username', 'Password']
    )


def login_to_bbo():
    session = requests.session()

    while True:
        credentials = get_credentials()
        if credentials is None:
            exit()
        response = session.post(
            f'https://www.bridgebase.com/myhands/myhands_login.php?t=%2Fmyhands%2Findex.php%3F&offset=0',
            data={'username': credentials[0], 'password': credentials[1]}
        )
        if response.text.find(LOGIN_UNSUCCESSFUL) == -1:
            break
        else:
            easygui.msgbox(msg=LOGIN_UNSUCCESSFUL, title=GUI_TITLE)

    return session, credentials[0]


def get_myhands_details(username_default, start_default, end_default):
    return easygui.multenterbox(
        msg='Get hands played by a user between two dates',
        title=GUI_TITLE,
        fields=['Username', 'Start date', 'End date'],
        values=[username_default, start_default, end_default]
    )


def prompt_for_myhands_details(username_default):
    start_default = strftime("%d.%m.%Y", localtime(mktime(localtime()) - SECONDS_IN_DAY))
    end_default = strftime("%d.%m.%Y", localtime())
    while True:
        try:
            details = get_myhands_details(username_default, start_default, end_default)
            if details is None:
                exit()
            username, start_input, end_input = details
            start_time = int(mktime(strptime(start_input, "%d.%m.%Y")))
            end_time = int(mktime(strptime(end_input, "%d.%m.%Y"))) + SECONDS_IN_DAY
            return username, start_time, end_time
        except ValueError as e:
            easygui.msgbox(msg=e, title=GUI_TITLE)


def download_myhands_page(session, username):
    username, start_time, end_time = prompt_for_myhands_details(username)
    return session.get(
        f"https://www.bridgebase.com/myhands/hands.php?offset=0&username={username}&start_time={start_time}&end_time={end_time}"
    ).text.strip()


def prompts_for_included_tourneys(soup):
    choices = [tr.text for tr in soup.find_all(class_="tourneyName")]
    if len(choices) == 1:
        choices.append('')
    elif len(choices) == 0:
        return None

    chosen = easygui.multchoicebox(
        msg='Pick tournaments/matches to download',
        title=GUI_TITLE,
        choices=choices
    )

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
                    flag = True
                else:
                    flag = False
            if (row.get("class", []) == ["team"] or row.get("class", []) == ["tourney"]) and flag:
                lin_url = row.find(class_="movie").find_all("a")[1]["href"]
                if lin_url.startswith("fetchlin"):
                    lin_url = f"https://www.bridgebase.com/myhands/{lin_url}"
                lin_map[tourneyName].append(lin_url)

        return lin_map
    except Exception as e:
        easygui.exceptionbox(msg=EXCEPTION_MESSAGE, title=GUI_TITLE)
        exit()


def create_safe_filename(filename):
    safe_name = "".join(c if c.isalnum() else "_" for c in filename)
    return re.sub(r"_+", r"_", safe_name).strip("_")


def download_lins(session, lin_map):
    dir_path = easygui.diropenbox(title=GUI_TITLE)
    easygui.msgbox(msg="Downloading has started in the background. You will be informed by a popup window when it has finished.", title=GUI_TITLE)
    try:
        for tourneyName, urls in lin_map.items():
            for num, url in enumerate(urls, start=1):
                path_to_lin = "{}/{}_{:0>2d}.lin".format(dir_path, create_safe_filename(tourneyName), num)
                with open(path_to_lin, "w", encoding="utf-8") as f:
                    f.write(session.get(url).text.strip())
    except Exception as e:
        easygui.exceptionbox(msg=EXCEPTION_MESSAGE, title=GUI_TITLE)
        exit()
    easygui.msgbox(msg=f"Downloading has finished successfully. Your LIN files are ready in {dir_path}", title=GUI_TITLE)


if __name__ == '__main__':
    bbo_session, bbo_username = login_to_bbo()

    while True:
        myhands_soup = BeautifulSoup(download_myhands_page(bbo_session, bbo_username), 'html.parser')
        included_tourneys = prompts_for_included_tourneys(myhands_soup)

        if included_tourneys is None:
            easygui.msgbox(msg="No tournaments found, try different date range or user", title=GUI_TITLE)
            continue

        if len(included_tourneys) < 1:
            easygui.msgbox(msg="No tournaments chosen. If you didn't find what you were looking for, try different date range or user", title=GUI_TITLE)
            continue

        break

    download_lins(bbo_session, extract_lin_links(myhands_soup, included_tourneys))
