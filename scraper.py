#all the required module
from selenium import webdriver
import bs4, time, csv, os
from datetime import datetime

# Variable to keep checks
drivers = {}
scores = {}
statistic = {}
oddsDict = {}

# url = input("Enter the URL to scrap: ")		
url = 'https://www.marathonbet.co.uk/en/live/22723'

# for getting the driver instant
def getDriver():
	# python3
	try:
		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		return webdriver.Chrome('./chromedriver',chrome_options=options)
	except:
		# python2
		try:
			options = webdriver.ChromeOptions()
			options.add_argument('headless')
			return webdriver.Chrome(chrome_options=options)
			# return webdriver.Chrome()
		except Exception as e:
			raise e


#Starting the main window and getting the url.
print('Getting the window\n\n')
driver = getDriver()
try:
	driver.get(url)
except Exception as e:
	raise 'Internet issue connect and try again'
print('\nGot the window\n\n')


#clicking on the the fraction button on the settings
driver.find_element_by_id('settingsDropdown').click()
driver.find_element_by_xpath('//*[@id="settingsDropdown"]/div[2]/div[1]/table/tbody/tr[1]/td[1]').click()
driver.find_element_by_xpath('//*[@id="settingsDropdown"]/div[2]/div[5]/button').click()


#for checking does the file exist and getting its filePath
def getFile(fileName, eventTitle):
	# checks if a folder with the event name exists or not
	if not os.path.exists(eventTitle):
		os.makedirs(eventTitle)
	# returning the file path and boolean value that is the files ex in ths folder
	filePath = eventTitle + '/' + fileName
	return os.path.exists(filePath), filePath


# appendind data to csv file 
def appendInCsv(playerName, odds, score,  leftData, rightData , eventTitle, fields, , indicator):
	print("Appening in CSV File\n\n\n")
	# Creating the file inside the folder 
	fileName = ' and '.join(playerName[0].split('/')) + ' vs ' + ' and '.join(playerName[1].split('/')) + '.csv'
	isFileExists , filePath = getFile(fileName, eventTitle)


	csvFile = open(filePath, 'a+') 
	# Different csv writer to write the file down	
	csvWriter = csv.writer(csvFile)
	csvDictWriter = csv.DictWriter(csvFile,fieldnames =fields)
	
	# writing the the data if the file doesn't exists
	if not isFileExists:
		#writing for the writer



		csvWriter.writerow(['Event Detail : ', eventTitle])

		# dots indicator
		if indicator == 1:
			csvWriter.writerow(['Players Name : ', playerName[0] + ' (dot) ', playerName[1]])
		elif indicator == 2:
			csvWriter.writerow(['Players Name : ', playerName[0], playerName[1] + ' (dot) '])
		else:
			csvWriter.writerow(['Players Name : ', playerName[0], playerName[1]])


		csvWriter.writerow([''])
		csvWriter.writerow([''])

		csvWriter.writerow(['Time : ', datetime.now().strftime('%d-%m-%Y : %H-%M-%S')])
		csvWriter.writerow(['Scores : ', score])
		try:
			if odds!=None:
				csvWriter.writerow(['Odds : ', odds[0], odds[1]])
		except:
			csvWriter.writerow(['Odds : ', odds])
		csvWriter.writerow([''])

		#writing for the dictwriter
		csvDictWriter.writeheader()
		csvDictWriter.writerow(leftData)
		csvDictWriter.writerow(rightData)

		csvWriter.writerow([''])
		csvWriter.writerow([''])

	# if the file exists write this function
	else:
		#writing for the writer
		csvWriter.writerow(['Time : ', datetime.now().strftime('%d-%m-%Y : %H-%M-%S')])
		csvWriter.writerow(['Scores : ', score])
		try:
			if odds!=None:
				csvWriter.writerow(['Odds : ', odds[0], odds[1]])
		except:
			csvWriter.writerow(['Odds : ', odds])
		csvWriter.writerow([''])

		#writing for the dictwriter
		csvDictWriter.writeheader()
		csvDictWriter.writerow(leftData)
		csvDictWriter.writerow(rightData)

		csvWriter.writerow([''])
		csvWriter.writerow([''])

	csvFile.close()

# Getting the statistic o each match when ever there is a change
def getStats(matchId, eventTitle, matchTitle):
 	# Url for getting th stats
	print("\n\nGetting the stats....\n\n")
	statsUrl = "https://www.marathonbet.co.uk/en/live/animation/statistic.htm?treeId=" + matchId
	

	#getting the a window fromm where we can scrape the stats 
	driverStats = drivers.get(eventTitle, None)

	# if there is no driver open for the event then create one with saving to a variable for later use
	if not driverStats:
		driverStats = getDriver()
		# drivers[eventTitle]['driver'] = driverStats
		drivers.update({eventTitle:{'driver':driverStats}})
		#Opening a new window to get statistics
		driverStats.get(statsUrl)
		windowAddress = driverStats.current_window_handle
		drivers[eventTitle].update({'tabs':{matchTitle:windowAddress}})

	else:	
		# if the driver exists but hadn't open a tab for the match opens and save the location to visit later
		tab = drivers[eventTitle]['tabs'].get(matchTitle, None)
		if not tab:
			drivers[eventTitle]['driver'].execute_script("window.open('"+statsUrl+"')")
			drivers[eventTitle]['driver'].switch_to_window(drivers[eventTitle]['driver'].window_handles[-1])
			drivers[eventTitle]['driver'].refresh()
			drivers[eventTitle]['tabs'].update({matchTitle:drivers[eventTitle]['driver'].current_window_handle})
		else:
			# switches to the required location to get driver activated
			drivers[eventTitle]['driver'].switch_to_window(tab)



	# Gets the bs4 object or the scarpping the stats 	
	stats = bs4.BeautifulSoup(drivers[eventTitle]['driver'].page_source,'html.parser')

	# trying to getthe data ofthe player
	#Getting the playerNames
	try:
		leftPlayer = stats.find(class_='left ellipsis-simple').get_text()
		rightPlayer =  stats.find(class_='right ellipsis-simple').get_text()
	except:
		drivers[eventTitle]['driver'].refresh()
		stats = bs4.BeautifulSoup(drivers[eventTitle]['driver'].page_source,'html.parser')
		leftPlayer = stats.find(class_='left ellipsis-simple').get_text()
		rightPlayer =  stats.find(class_='right ellipsis-simple').get_text()

	#Getting all the data in the row
	rows = stats.find('tbody').find_all('tr')

	#Getting the name of the fields
	fields = []

	#Getting the data of the both players seprately
	leftData = {}
	rightData = {}

	leftData['teams-member']= leftPlayer
	rightData['teams-member']= rightPlayer

	fields.append('teams-member')
	

	#Getting the statsitic of both the player 
	for row in rows:
		center = row.find(class_='center').get_text()
		fields.append(center)
		left = row.find(class_='left').get_text()
		right = row.find(class_='right').get_text()
		leftData[center] = left
		rightData[center]= right

	#checking if the stats has changed or not.
	isStatsChange= False
	event = statistic.get(eventTitle,None)

	if not event: 
		statistic.update({eventTitle:{matchTitle:{'leftData':leftData,'rightData':rightData}}})
		isStatsChange = True
	else:
		if not event.get(matchTitle, None):
			statistic[eventTitle].update({matchTitle:{'leftData':leftData,'rightData':rightData}})
			isStatsChange = True
		else:
			data = event[matchTitle]
			if data['leftData'] != leftData or data['rightData'] != rightData:
				isStatsChange = True
				statistic[eventTitle][matchTitle]['leftData'] = leftData
				statistic[eventTitle][matchTitle]['rightData'] = rightData

	return fields,leftData,rightData, isStatsChange



#getting the details of the match like score and name of the player
def getMatchDetails(match):
	print("\nGetting Match Details... \n\n\n")
	matchId = match.get_attribute('data-event-treeid')
	playerName = [name.text for name in match.find_elements_by_class_name('live-today-member-name')]
	score = match.find_element_by_class_name('result-row').text
	matchTitle = playerName[0]+' vs ' + playerName[1]
	

	# ****************dot indicator******************
	indicator = None
	allIndicatorTags = match.find_elements_by_class_name('sport-indicator')
	try:
		allIndicatorTags[0].find_element_by_tag_name('img')
		indicator=1
	except:
		allIndicatorTags[1].find_element_by_tag_name('img')
		indicator=2
	else:
		pass
	# *************************************************


	#Getting the last score to check if the score has changed or not
	isOddChange = False
	isScoreChange = False
		#Getting all The Odds
	try:
		odds =  [' '.join(odd.text.split('\n')) or odd.text for odd in match.find_elements_by_class_name('height-column-with-price')[:2]]
	except Exception as e:
		odds = None
		pass

	#Checks if the score and odds have changed

	lastScore = scores.get(matchTitle, None)
	if lastScore == None:
		scores.update({matchTitle:score})

	lastOdds = oddsDict.get(matchTitle, None)
	if not lastOdds and not odds:
		oddsDict.update({matchTitle:odds})

	if lastScore != score or lastScore == None:
		isScoreChange = True

	if lastOdds != odds or lastOdds == None:
		isOddChange = True


	return matchId, playerName, score,  odds, isOddChange, isScoreChange, indicator


def start():
	#Initiating the program.
	checktime = datetime.now()
	while True:
		eventTitles = []
		matchTitles = []
		#Scrapping
		try:
			allEvents = driver.find_elements_by_class_name('category-container')	
		except Exception as e:
			driver.refresh()
			allEvents = driver.find_elements_by_class_name('category-container')	
		else:
			print("Can't find any match\nSleeping for 30 sec! till any match starts...")
			time.sleep(30)
			continue

	

		#Scrapping the data of eacch Tournament
		for event in allEvents:
			try:
				eventTitle = event.find_element_by_class_name('category-label-td').text
				eventId = event.find_element_by_class_name('category-content').get_attribute('id')
				allMatches = event.find_elements_by_xpath('//*[@id="{}"]/div/table/tbody'.format(eventId))
			
				eventTitles.append(eventTitle)
				#Gettinhg the data of each match
				for match in allMatches:
					#scraping the details
					try:
						matchId, playerName, score,  odds, isOddChange, isScoreChange, indicator = getMatchDetails(match)
					except:
						continue
					matchTitle = playerName[0]+' vs ' + playerName[1]
				
					print(matchId)
					print(playerName)
					print(odds)
					print(score)

					matchTitles.append(matchTitle)


					#Trying to get the stats of the match if the score has changed
					fields, leftData, rightData, isStatsChange = getStats(matchId, eventTitle, matchTitle)
					
					#checking if statistic or score or odd any of them has change or not.
					if isStatsChange or isScoreChange or isOddChange:
						#Saving the data in CSV
						appendInCsv(playerName, odds, score, leftData, rightData, eventTitle, fields, indicator)
					#Updating the last score
					scores[matchTitle] = score
					oddsDict[matchTitle] = odds
					# time.sleep(1)
			except:
				continue
		
		#Checks if any match has ended after every one hour so if can close the tab bor window for it.
		if (datetime.now() - checktime).seconds > 1800:
			print("Checking to kill")

			for event in drivers.keys():
				try:
					if not event in eventTitles:
						driverClose = drivers[event].get('driver', None)
						if driverClose:
							for match in drivers[event]['tabs'].keys():
								tab = drivers[event]['tabs'].get(match,None)
								if tab:
									driverClose.switch_to_window(tab)
									print('Closing a tab')
									driverClose.close()
									del oddsDict[match]
									del scores[match]
							del drivers[event]
							del statistic[event]	
							
					else:
						for match in drivers[event]['tabs'].keys():
							if not match in matchTitles:
								driverClose = drivers[event].get('driver', None)
								tab = drivers[event]['tabs'].get(match,None)
								if tab and driverClose:
									driverClose.switch_to_window(tab)
									print('Closing a tab')
									driverClose.close()
									del drivers[event]['tabs'][match]
									del statistic[event][match]
									del oddsDict[match]
									del scores[match]
				except Exception as e:
					print('Some error')
					continue 
				
			checktime = datetime.now()
start()
