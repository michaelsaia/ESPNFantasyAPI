from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
import json
import pandas as pd
from datetime import datetime
import math
import os
from pathlib import Path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

chrome_options = Options()
chrome_options.add_argument("--headless")
#chrome_options.add_argument("window-size=1280,1024")
chrome_options.add_experimental_option("detach", True)
#chrome_options.add_argument('--blink-settings=imagesEnabled=false')
#Unfortunately if you don't load images it breaks the whole site

start = datetime.now()
print(f'the start time was {start}')

directory = Path.cwd()
chromedriver = str((directory / 'chromedriver_win32/chromedriver.exe').resolve())

driver = webdriver.Chrome(chromedriver, options = chrome_options)

driver.get("https://fantasy.espn.com/football/players/projections?leagueFormatId=1")

#need to reset player and xpath every 50 players as we perform pagination and move to the next page

c = 1

pg = 1

res = []

for i in range(300):

	player = {}

	rank = driver.find_element_by_xpath(f'//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[1]/div/div/div[2]/table/tbody/tr/td[1]/div').text

	player['Rank'] = rank

	name = driver.find_element_by_xpath(f'//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[1]/span/a').text

	print(name)

	player['Name'] = name

	lst4idx = len(name)-4
	if name[lst4idx:] == "D/ST":
		player['Team'] = name.split(' ')[0]
		player['Position'] = "D/ST"
		pos = "D/ST"

	else:

		team = driver.find_element_by_xpath(f'//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[2]/span[2]').text

		player['Team'] = team

		pos = driver.find_element_by_xpath(f'//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[2]/span[3]').text

		player['Position'] = pos

	#next thing is adding 6 stats for kicker, 7 stats for defense (defense has no team listed and no pos)

	stats_2021 = {}
	proj_2022 = {}

	if (pos == 'RB') or (pos == 'QB'):
		sc = 8

	elif (pos == 'TE') or (pos == 'WR'):
		sc = 9

	elif (pos == 'K'):
		sc = 6

	else:
		sc = 7

	for j in range(sc):
			statElement2021 = driver.find_element_by_xpath(f'//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td[{j+2}]/div')
			statName2021 = statElement2021.get_attribute('title')
			stat2021 = statElement2021.text
			stats_2021[statName2021] = stat2021

			statElement2022 = driver.find_element_by_xpath(f'//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[2]/td[{j+2}]/div')
			statName2022 = statElement2022.get_attribute('title')
			stat2022 = statElement2022.text
			proj_2022[statName2022] = stat2022

	player['2021_Stats'] = stats_2021
	player['2022_Projections'] = proj_2022

	res.append(player)

	if c==50:
		c=1
		pg += 1

		driver.find_element_by_id(str(pg)).click()

		wait = WebDriverWait(driver, 50)
		element = wait.until(EC.staleness_of(statElement2022))

	else:
		c += 1

driver.close()
driver.quit()

response = json.dumps(res, indent=2)




'''
Just some sample wait stuff

#wait = WebDriverWait(driver, 50)
		#element = wait.until(EC.element_to_be_clickable((By.ID, str(pg))))

		#wait = WebDriverWait(driver, 50)
		#element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#fitt-analytics > div > div.jsx-3010562182.shell-container > div.page-container.cf > div.layout.is-full > div > div > div > div > div:nth-child(50) > div > div.ResponsiveTable.full-projection-player > div > div > div.Table__Scroller > table > tbody > tr > td.playerInfo__player.Table__TD > div > div > div.jsx-2144864361.player-info > div.jsx-2144864361.player-name > span > a")))
		#driver.refresh() issue here is that it restarts us to page 1

element = wait.until(EC.element_to_be_clickable((By.ID, 'SUB_Football_NFL_0')))
driver.find_element_by_id('SUB_Football_NFL_0').click()

time.sleep(10)

element = wait.until(EC.element_to_be_clickable((By.ID, 'btn-continue')))
#driver.find_element_by_xpath('/html/body/nolink/nolink/nolink/nolink/nolink/app-root/app-main-layout/div[1]/div/app-toolbar/div/div[2]/div[1]/button').click()
'''


'''
Button Pagination has id equal to its page
i.e. button for page 1 has an id of 1

URL Inspection

Player Rank xpath
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[1]/div/div/div[2]/table/tbody/tr/td[1]/div
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/table/tbody/tr/td[1]/div

#checking if it differs on the next page
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[1]/div/div[1]/div/div/div[2]/table/tbody/tr/td[1]/div
#does not differ on the next page

Player Name
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[1]/span/a
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[1]/span/a

Player Team
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[2]/span[2]
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[2]/span[2]

Player Position
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[2]/span[3]
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div[2]/span[3]

Header 1
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[2]/div[1]/div/div/div/div[2]/table/thead/tr/th[{j}]/div/span
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/table/thead/tr/th[2]/div/span

Header 2
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[2]/div[1]/div/div/div/div[2]/table/thead/tr/th[3]/div/span
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/table/thead/tr/th[3]/div/span


2021 stat 1
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td[{j}}]/div
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td[2]/div
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[20]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td[9]/div

the title of the div storing the data is also the name of the stat

2021 stat 2
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td[3]/div
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[1]/td[3]/div


2022 stat 1
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[2]/td[2]/div
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[2]/td[2]/div


2022 stat 2
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[{c}]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[2]/td[3]/div
//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/table/tbody/tr[2]/td[3]/div



All stats

carries, rushyds, rushavg(RBonly), rushTD, receptions, targets(WRonly), recYards, recAvg(WRonly), recTD, fantasyPts

QB Only: completion/attempts, passyds, passTD, Int, Car, Yds, Td
'''