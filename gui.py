#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: jr-magnus
"""
import easygui
from time import strftime, localtime, mktime


GUI_TITLE = 'LIN Scraper jr-magnus@github.com'
EXCEPTION_MESSAGE = """
This program has encountered a critical error and will now terminate. 
Please report this problem at github.com/jr-magnus/lin-scraper.\n\n\n
"""


def bbo_credentials():
    return easygui.multpasswordbox(
        msg='Log in to BBO',
        title=GUI_TITLE,
        fields=['Username', 'Password']
    )


def specify_search_window(username_default):
    start_default = strftime("%d.%m.%Y", localtime(mktime(localtime()) - 60*60*24))
    end_default = strftime("%d.%m.%Y", localtime())
    return easygui.multenterbox(
        msg='Get hands played by a user between two dates',
        title=GUI_TITLE,
        fields=['Username', 'Start date', 'End date'],
        values=[username_default, start_default, end_default]
    )


def tournament_picker(choices):
    return easygui.multchoicebox(
        msg='Pick tournaments/matches to download',
        title=GUI_TITLE,
        choices=choices
    )


def exception(e):
    return easygui.exceptionbox(msg=EXCEPTION_MESSAGE + str(e), title=GUI_TITLE)


def directory():
    return easygui.diropenbox(title=GUI_TITLE)


def msgbox_generic(msg):
    return easygui.msgbox(msg=msg, title=GUI_TITLE)


def myhands_value_error(msg):
    return msgbox_generic(msg)


def login_unsuccessful():
    return msgbox_generic('Username or password incorrect, please try again')


def download_started():
    return msgbox_generic(
        'Downloading has started in the background. You will be informed by a popup window when it has finished.'
    )


def download_finished(dir_path):
    return msgbox_generic(f"Downloading has finished successfully. Your LIN files are ready in {dir_path}")


def no_tournaments_found():
    return msgbox_generic("No tournaments found, try different date range or user")


def no_tournaments_chosen():
    return msgbox_generic(
        "No tournaments chosen. If you didn't find what you were looking for, try different date range or user"
    )
