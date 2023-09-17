import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings("ignore")
from datetime import date

def get_numel(string):
	try:
		return int(re.sub(r'[^0-9]', '', string))
	except:
		return -1

def get_info(link):
	url = f'https://www.edmunds.com{link}'
	resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
	soup = BeautifulSoup(resp.text, "lxml")
	price = soup.find_all("span", {"data-test": "vdp-price-row"})[0].text
	price = get_numel(price)
	info = link.split('/')
	make, model, year, vin = info[1], info[2], int(info[3]), info[5]
	
	summary = soup.find_all("section", {"class": "vehicle-summary mb-0_5 text-gray-darker"})[0]
	summary = summary.find_all("div", {"class": "col"})

	millege = get_numel(summary[0].text)
	city_mpg, hwy_mpg = -1, -1
	for element in summary:
		if 'city' in element.text and 'hwy' in element.text:
			city_mpg = get_numel(element.text.split('/')[0].split()[0])
			hwy_mpg = get_numel(element.text.split('/')[1].split()[0])
	
	return vin, make, model, year, price, millege, city_mpg, hwy_mpg
	
def collect_data(URL):
	df = pd.DataFrame(data=None, columns=['vin', 'make', 'model', 'year', 'millege', 'city_mpg', 'hwy_mpg', 'price'])

	resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
	soup = BeautifulSoup(resp.text, "lxml")

	inventory_count = soup.find_all('span', {'class': "inventory-count"})
	inventory_count = inventory_count[0].text
	inventory_count = get_numel(inventory_count)
	for pg in range(1, inventory_count//21 + 2):
		url = URL + f'&pagenumber={pg}'
		resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
		if resp.status_code != 200:
			continue
		soup = BeautifulSoup(resp.text, "lxml")
		car_links = soup.find_all("a", {"class": "usurp-inventory-card-vdp-link"})
		links = set([link.get('href') for link in car_links])
		for link in links:
			try:
				vin, make, model, year, price, millege, city_mpg, hwy_mpg = get_info(link)
				df = df.append({
					"vin": vin,
					"make": make,
					"model": model,
					"year": year,
					"millege": millege,
					"city_mpg": city_mpg,
					"hwy_mpg": hwy_mpg,
					"price": price
				}, ignore_index=True)
			except:
				pass

	return df

if __name__ == '__main__':
	url_dict = {
		'miata-rf': 'https://www.edmunds.com/inventory/srp.html?deliverytype=local&inventorytype=used&make=mazda&model=mx-5-miata-rf&historyinfo=noAccidents',
		'miata': 'https://www.edmunds.com/inventory/srp.html?deliverytype=local&inventorytype=used&make=mazda&model=mx-5-miata&historyinfo=noAccidents',
		'WRX': 'https://www.edmunds.com/inventory/srp.html?deliverytype=local&inventorytype=used&make=subaru&model=wrx&historyinfo=noAccidents',
		'focus': 'https://www.edmunds.com/inventory/srp.html?deliverytype=local&inventorytype=used&make=ford&model=focus&historyinfo=noAccidents',
		'focus-ST': 'https://www.edmunds.com/inventory/srp.html?deliverytype=local&inventorytype=used&make=ford&model=focus-st&historyinfo=noAccidents',
		'mustang': 'https://www.edmunds.com/inventory/srp.html?deliverytype=local&inventorytype=used&make=ford&model=mustang&historyinfo=noAccidents',
		'GTI': 'https://www.edmunds.com/inventory/srp.html?deliverytype=local&inventorytype=used&make=volkswagen&model=golf-gti&historyinfo=noAccidents',
		'all': 'https://www.edmunds.com/inventory/srp.html?deliverytype=local&inventorytype=used%2Ccpo&historyinfo=noAccidents'
	}
	save_folder = './data'

	today = date.today()
	today = today.strftime("%Y-%m-%d")
	for model, url in url_dict.items():
		if not os.path.exists(f'{save_folder}/{model}'):
			os.mkdir(f'{save_folder}/{model}')
		df = collect_data(url)
		df.set_index('vin', inplace=True)
		df.to_csv(f'{save_folder}/{model}/{today}.csv')
		print(df)
