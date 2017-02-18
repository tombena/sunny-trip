import json, time, requests, urllib2, json, sys, os
from datetime import datetime, timedelta
import numpy as np

# Calculate highest and lowest temperature for given destination
# Store every day weather for this city
# 3 day forecast
def get_weather_high_low(key, city, country):
	api_url = 'http://api.wunderground.com/api/' + key + '/geolookup/conditions/forecast/q/' + country + '/' + city + '.json'
	f = urllib2.urlopen(api_url)
	json_string = f.read()
	parsed_json = json.loads(json_string)
	high = 0
	low = 40
	
	temp_list=[]
	icon_list=[]
	for i in range(0, 8):
		temp = -50
		# Get temperature for day i (Today i=0, Tonight i=1, Tomorrow i=2, Tomorrow Night i=3)
		today_w = parsed_json['forecast']['txt_forecast']['forecastday'][i]['fcttext_metric'].split('.', 3)

		#Get temperature in Celsius from a sentence (ex: "High around 10C", "High -5C" ...)
		if 'High' in today_w[1] or 'Low' in today_w[1]:
			tokens = today_w[1].split()
			for j in range(0, len(tokens)):
				# Get temperature
				if "C" in tokens[j]:
					# Check if temperature is negative
					if "-" in tokens[j]:
						temp = - [int(s) for s in tokens[j][1:-1].split() if s.isdigit()][0]
					else:
						temp = [int(s) for s in tokens[j][0:-1].split() if s.isdigit()][0]

		if temp > high:
			high = temp
		if temp < low and temp !=-50:
			low = temp				
		temp_list.append(temp)

	f.close()

	print 'Temperature averages between %sC and %sC in %s, %s for the next 3 days' % (high, low, city, country)
	return high, low

# returns flight details between origin and destination for a 2 day stay starting tomorrow
def get_flights_between(origin, destination):
	date_departure =  datetime.now().date() +  timedelta(days=1) # tomorrow
	date_arrival = date_departure +  timedelta(days=2)			# delta days later
	departure_t = "0"
	payload = {
	 "request": {
	  "passengers": {
	   "adultCount": 1,
	   "infantInLapCount": 0,
	   "infantInSeatCount": 0,
	   "childCount": 0,
	   "seniorCount": 0
	  },
	  "slice": [
	   {
	    "date": date_departure.strftime('%Y-%m-%d'),
	    "origin": origin,
	    "destination": destination
	   },
	   {
	    "date": date_arrival.strftime('%Y-%m-%d'),
	    "origin": destination,
	    "destination": origin
	   }
	  ],
	  "refundable": "false",
	  "solutions": 10
	 }
	}
	# Call to QPX API
	r = requests.post('https://www.googleapis.com/qpxExpress/v1/trips/search?key=' + qpx_key, json = payload)
	rep = json.loads(r.text)

	# Get the 5 cheapest flights
	for i in range(0, 5):
		print "Price %s " % rep['trips']['tripOption'][i]['pricing'][0]['saleTotal']

		for j in range(0,2):
			if j == 0:
				print "%s -> %s" % (origin, destination)
			elif j == 1:
				print "%s -> %s" % (destination, origin)

			carrier = rep['trips']['tripOption'][i]['slice'][j]['segment'][0]['flight']['carrier']
			flight_number = rep['trips']['tripOption'][i]['slice'][j]['segment'][0]['flight']['number']
			print "Flight %s %s" % (carrier, flight_number)

			departure_t = rep['trips']['tripOption'][i]['slice'][j]['segment'][0]['leg'][0]['departureTime']
			arrival_t = rep['trips']['tripOption'][i]['slice'][j]['segment'][0]['leg'][0]['arrivalTime']
			print "Departure time %s" % departure_t

			duration = int(rep['trips']['tripOption'][i]['slice'][j]['duration'])
			print "Duration %d min" % duration


# Get API keys from textfile
file = open('API-keys.txt', 'r')
wu_key = file.readline().split(':', 1)[1][0:-1]
qpx_key = file.readline().split(':', 1)[1][0:-1]
file.close()
print wu_key
print qpx_key

cities = ['Paris', 'London', 'Barcelona', 'Rome', 'Berlin', 'Lisbon', 'Prague', 'Venice', 'Amsterdam', 'Madrid', 'Vienna', 'Florence', 'Athens', 'Nice']
countries = ['France', 'UK', 'Spain', 'Italy', 'Germany', 'Portugal', 'CZ', 'Italy', 'NL', 'Spain', 'Austria', 'Italy', 'Greece', 'France']
codes = ['PAR', 'LON', 'BCN', 'ROM', 'BER', 'LIS', 'PRG', 'VCE', 'AMS', 'MAD', 'VIE', 'FLR', 'ATH', 'NCE']
high = np.zeros(len(cities))
low = np.zeros(len(cities))

# Get highest/lowest temperatures for all given destinations
for i in range(len(cities)):
	high[i], low[i] = get_weather_high_low(wu_key, cities[i], countries[i])
	# /!\ Wunderground API free plan only allows 10 call per minute
	time.sleep(6)

# Find highest temperature among all cities
max_high = 0
max_ind = 0
for i in range(len(high)):
	if high[i] > max_high:
		max_high = high[i]
		max_ind = i

print 'Best weather is %s, %s with temperature between %s and %sC' % (cities[max_ind], countries[max_ind], high[max_ind], low[max_ind])

# Get flights from Paris leaving tomorrow for a 2 day-stay to the warmest destination
get_flights_between("PAR", codes[max_ind])


