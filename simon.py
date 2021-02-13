from selenium import webdriver
from lxml import html
import time
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import pandas as pd
from tqdm import tqdm

url="https://www.cmegroup.com/trading/energy/natural-gas/\
natural-gas_quotes_globex_options.html#optionProductId=1352&strikeRange=ALL"

def initWebdriver(mode):
    options = webdriver.ChromeOptions()
    #print("Headless Mode",cfg.defaults['headless'])
    if(mode):
        options.add_argument('headless')
    else:
    	print("Running in Normal Mode")
    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),options=options)
    #webdriver.Chrome(executable_path=chromedriver, options=options)
    return driver

columns=['CALLS UPDATED','CALLS VOLUME','CALLS HIGH','CALLS LOW',\
'CALLS PRIOR SETTLE','CALLS CHANGE','CALLS LAST',\
 'PUTS LAST','PUTS CHANGE','PUTS PRIOR SETTLE',\
 'PUTS LOW','PUTS HIGH','PUTS VOLUME','PUTS UPDATED','STRIKE PRICE','Date']

def getthetable(index,date):
	final=[]
	ele=Select(driver.find_element_by_id('cmeOptionExpiration'))
	ele.select_by_index(index)
	tree=html.fromstring(driver.page_source)
	for idx,row in enumerate(tree.xpath('//*[@id="optionQuotesProductTable1"]/tbody/tr')):
		rowdata=[]
		for i in row.xpath('./td'):
		    rowdata.append(i.text_content())
		rowdata.append(''.join(row.xpath('./th/text()')))
		rowdata.append(date)
		final.append(rowdata)
	#df=pd.DataFrame(final,columns=columns)
	return final

driver=initWebdriver(True)
driver.get(url)
time.sleep(5)

tree=html.fromstring(driver.page_source)


finaldf=pd.DataFrame()
for index,date in enumerate(tqdm(driver.find_element_by_id('cmeOptionExpiration').text.split('\n'))):
	try:
		data=getthetable(index,date)
		df=pd.DataFrame(data,columns=columns)
		#print("type",type(data))
		#print(df)
	except Exception as e:
		print("Error occured",e)
	time.sleep(1)
	finaldf=pd.concat([df,finaldf])


finaldf['Date']=pd.to_datetime(finaldf.Date)
finaldf=finaldf.sort_values(by=['Date'],ascending=True)


finaldf.replace('-',0,inplace=True)

for idx,data in tqdm(finaldf.iterrows()):
    #print(data)
    if(data['CALLS LAST']==0):
        data['CALLS LAST']=(data['CALLS LOW']+data['CALLS HIGH'])/2
    if(data['PUTS LAST']==0):
        data['PUTS LAST']=(data['PUTS LOW']+data['PUTS HIGH'])/2

finaldf.to_csv("Output.csv",index=False)

## Close the webdriver
driver.close()