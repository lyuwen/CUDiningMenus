#!/usr/bin/env python3
import json
import datetime
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_menu_list(url):
  soup = BeautifulSoup(requests.get(url).content, "html.parser")
  return [s.find("a", {"title": "Full Node View"}).getText() for s in soup.find_all("div", {"class": "field-item"})]

url_base = "http://dining.columbia.edu/"

url_menu = url_base + "menus"

header = {
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:36.0) Gecko/20100101 Firefox/36.0",
}

session = requests.session()

soup = BeautifulSoup(session.get(url_menu).content, 'html.parser')
form = soup.find("form", {"id": "future-menus-form"})
form_build_id = soup.find("input", {"id": "edit-future-menus-form"}).attrs["value"]

menus = {}

for ddate in range(6):
  date = datetime.now() + timedelta(ddate)

  payload = {
    "menu_date[month]": str(date.month),
    "menu_date[day]": str(date.day),
    "menu_date[year]": str(date.year),
    "form_id": "future_menus_form",
    "form_build_id": form_build_id,
    "future_menu_search": "Find",
  }

  respond = session.post(url=url_base + "/future-menu-search/js", data=payload)

  soup = BeautifulSoup(respond.content.decode("unicode_escape"), 'html.parser')

  menu = dict([(location.find_all("td")[0].getText(), \
      dict([(meal.getText(), get_menu_list("http://dining.columbia.edu{}".format(meal.attrs["href"]))) \
      for meal in location.find_all("td")[1].find_all("a")])) \
      for location in soup.find_all("tr")[1:]])

  menus[date.strftime("%Y%m%d")] = menu.copy()

print(json.dumps(menus, indent=2))
