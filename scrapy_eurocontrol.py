# coding=utf-8


import pickle
import requests
import time
from lxml import html
import sys, json
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

reload(sys)
sys.setdefaultencoding('utf-8')


visitadas = {}
lista_geral = []
rede = {}


################################################################################################

def clear_atm(category):


	category = [i.replace('\n','') for i in category]
	
	category = [i.strip(' ') for i in category if len(i) > 3 and not None]

	return filter(None,category)

################################################################################################
def get_atm(tree):

	data = {}

	# 	
	try:
		x = tree.xpath('//div/div[1]/div/div/div[2]/div/text()')

		data['actCategory'] = clear_atm(x)
	except:
		data['actCategory'] = None		
		print 'except','ATM activity category'

	#ATM data category
	try:
		x = tree.xpath('//div/div[3]/div/div/div[2]/div/text()')
	
		data['dataCategory'] = clear_atm(x)

	except:
		data['dataCategory'] = None
		print 'except', 'ATM data category'

	#Atm stakeholders Precisa afunilar tem a consulta xtree (tem que retirar 'Ready for consumption')
	try:

		x = tree.xpath('//div/div[5]/div/div/div[2]/div/text()')
	
		data['dataStakeholder'] = clear_atm(x[1:])
	except:
		data['dataStakeholder'] = None
		print 'except', 'Atm stakeholders'

	#atm regions Também precisa afunilar (tem que retirar 'Current and Supported')
	
	try:

		x = tree.xpath('//div/div[7]/div/div/div[2]/div/text()')

		data['regions'] = clear_atm(x[1:])

	except:
		data['regions'] = None
		print 'Except','Regioes'  

	#atm flight phases
	
	try:
		x = tree.xpath('//div/div[9]/div/div/div[2]/div/text()')

		data['flightPhases'] = clear_atm(x)
	except:
		data['flightPhases'] = None
		print 'Except','atm flight phases'

	return data


################################################################################################

def get_header(tree):
	
	data = {}

	try:

		name = tree.xpath('//*[@id="content"]/div/div[1]/h1/text()')

		name = [i.replace('\t','') for i in name]

		data['nameService'] = clear_atm(name)[0]

		per_describe = tree.xpath('//div[@class="percent-complete"]/text()')

		data['percentPrescribe'] =  per_describe[0]

		
	except:
		data['percentPrescribe'] = None
		print 'Exception', 'NOME SERVICO'

	try:
	
		version = tree.xpath('//*[@id="block-system-main"]/div/div/div/div[1]/div/div[2]/div/div[1]/div/div/div/div[1]/div/div/div[2]/div/text()')

		data['version'] = version[0]

		implementStatus = tree.xpath('//*[@id="block-system-main"]/div/div/div/div[1]/div/div[2]/div/div[1]/div/div/div/div[5]/div/div/div[2]/div/text()')

		data['implementStatus'] = implementStatus[0]

		

	except:
		print 'Exception', 'VERSAO Servico'
		data['implementStatus'] = None

	try:

		versionCategory  = tree.xpath('//*[@id="block-system-main"]/div/div/div/div[1]/div/div[2]/div/div[1]/div/div/div/div[7]/div/div/div[2]/div/text()')

		data['versionCategory'] = versionCategory[0]

	except:
		data['versionCategory'] =None
		print 'Exception', 'Categoria Versao'

	return data

################################################################################################

def get_registrationProcess(tree):
	
	data = {}

	#Service Description
	try:
	
		serviceDescription = tree.xpath('//div/div[@class="pane-content"]/p/text()')

		data['serviceDescription'] = serviceDescription
	except:
		data['serviceDescription'] = None
		print 'Except', 'Service Description'

	# Service Tecnical Interface
	try:
		serviceTecnicalInterface = tree.xpath('//div/div/div/div/div[3]/div/div[1]/div/div[2]/div/div/div/div[3]/div/div/div/div/div/div[2]/div/span[1]/span/a/text()')

		data['serviceTecnicalInterface'] = serviceTecnicalInterface[0]
	except:
		data['serviceTecnicalInterface'] = None
		print 'Except', 'Service Tecnical Interface'
	

	# Service Tecnical Interface 
	try:	
		sti_description1 = tree.xpath('//div/div/div/div/div[3]/div/div[2]/div/div[1]/div/div/div/div[3]/div/div/div/div/div/div[2]/div/span/span/a/text()')

		sti_description2 = tree.xpath('//div/div/div/div/div[3]/div/div[2]/div/div[1]/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div/span/text()')
		
		data['serviceTecnicalInterface'] = sti_description1[0] +':'+ sti_description2[0]	
	except:
		data['serviceTecnicalInterface'] = None
		print 'Except', 'Service Tecnical Interface '

	return data
################################################################################################

baseurl  ='https://eur-registry.swim.aero'


driver  = webdriver.Firefox()

driver.get('https://eur-registry.swim.aero/user/login')

username = driver.find_element_by_id("edit-name")
password = driver.find_element_by_id("edit-pass")

username.send_keys("camilacb@icea.gov.br")
password.send_keys("Camil@01")

driver.find_element_by_id("edit-submit").click()

time.sleep(5)

pages = '/service-implementations?sid=All&field_version_category_tid=All&title=&body_value=&&&&&&&&page='

data_json = {}

j = 0
	
for k in xrange(0,3):
	
	driver.get(baseurl+pages+str(k))

	time.sleep(5)

	tree = html.fromstring(driver.page_source)

	s = tree.xpath('//a/@href')

	ss = [x for x in s if '/services/' in x]

	services = []
	for i in ss:
		if i not in services:
			services.append(i)

	print services, len(services)

	for i in services:

		driver.get(baseurl+i)
	
		time.sleep(5)

		tree = html.fromstring(driver.page_source)

		data_json[j] = {'header':get_header(tree), 'atm':get_atm(tree),'registrationProcess':get_registrationProcess(tree)}

		j+=1

		print j

with open('resultado.json','w') as out:
	json.dump(data_json,out)
	
#with open('Output.txt' ,'w') as te:
#	te.write(driver.page_source)



#with open('Output.txt','w') as text_file:
#	text_file.write(page.text)

