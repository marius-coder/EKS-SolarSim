# -*- coding: latin-1 -*-
import dateutil.parser as parser
from math import sin,cos,tan,atan2,atan,degrees,radians,asin, acos
from collections import Counter
import pandas as pd
import requests
import urllib.parse
import datetime
import timezonefinder, pytz


class Sonne:
	JD_Base = 2451545 #Julianisches Datum
	def __init__(self):
		self.x = 0
		self.y = 0
		self.z = 0


	def FromAddress(self, address_string="Stephansplatz, Wien, Österreich"):
		parsed_address = urllib.parse.quote(address_string)
		url = 'https://nominatim.openstreetmap.org/search/' + parsed_address +'?format=json'
		response = requests.get(url).json()
		self.lat = float(response[0]["lat"])
		self.lon = float(response[0]["lon"])

	def ElevationFunction(self):
		url = 'https://api.opentopodata.org/v1/aster30m?locations=' + str(self.lat) + ','+ str(self.lon)
		response = requests.get(url).json()
		self.elevation = response['results'][0]['elevation'] / 1000


	def GetHorizon(self):
		url = 'https://re.jrc.ec.europa.eu/api/v5_1/printhorizon?lat=' + str(self.lat) + '&lon=' + str(self.lon) + '&outputformat=json'
		response = requests.get(url).json()
		self.horizonData = response["outputs"]["horizon_profile"]
		self.horizonList = []
		self.AzimuthList = []
		for i in range(len(self.horizonData)):
			self.horizonList.append(float(self.horizonData[i]["H_hor"]))
			self.AzimuthList.append(float(self.horizonData[i]["A"]))

		return

	def SetTimezone(self, date):
		tf = timezonefinder.TimezoneFinder()
		# From the lat/long, get the tz-database-style time zone name (e.g. 'America/Vancouver') or None
		timezone_str = tf.certain_timezone_at(lat=self.lat, lng=self.lon)

		if timezone_str is None:
			print("Could not determine the time zone")
		else:
			# Display the current timezone
			tz = pytz.timezone(timezone_str)
			dt = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
			self.timezone = (tz.utcoffset(dt) - tz.dst(dt)).seconds/3600

	def Init(self,address):
		self.FromAddress(address)
		self.ElevationFunction()
		self.GetHorizon()
		

	def CalcJulianischesDatum(self,date):
		year = parser.parse(date).year
		month = parser.parse(date).month
		day = parser.parse(date).day
		hour = parser.parse(date).hour
		minute = parser.parse(date).minute
		second = parser.parse(date).second
		ts = pd.Timestamp(year = year,  month = month, day = day,  
                  hour = hour, minute = minute, second = second)
		return ts.to_julian_date()

	def CalcSonnenstand(self, date, debug = False):
		self.SetTimezone(date)
		JD_Base = 2451545 #Julianisches Datum
		#Julian Day
		JD = self.CalcJulianischesDatum(date)
		
		#Julian Century
		JC = (JD - JD_Base) / 36525

		#Geom Mean Long Sun (deg)
		gMeanLongSun = (280.46646 + JC * (36000.76983 + JC * 0.0003032)) % 360

		#Geom Mean Anom Sun (deg)
		gMeanAnomSun = 357.52911 + JC * (35999.05029 - 0.0001537 * JC)

		#Eccent Earth Orbit
		eccEarthOrbit = 0.016708634 - JC * (0.000042037 + 0.0000001267 * JC)

		#Sun Eq of Ctr
		sunCtr = sin(radians(gMeanAnomSun)) * (1.914602 - JC * (0.004817 + 0.000014 * JC)) + \
					sin(radians(2*gMeanAnomSun)) * (0.019993 - 0.000101 * JC) + sin(radians(3 * gMeanAnomSun))*0.000289

		#Sun True Long (deg)
		sunTrueLong = gMeanLongSun + sunCtr

		#Sun True Anom (deg)
		sunTrueAnom = gMeanAnomSun + sunCtr
		
		#Sun Rad Vector (AUs)
		sunRadVec = (1.000001018 * (1 - eccEarthOrbit * eccEarthOrbit)) / (1 + eccEarthOrbit * cos(radians(sunTrueAnom)))

		#Sun App Long (deg)
		sunAppLong = sunTrueLong - 0.00569 - 0.00478 * sin(radians(125.04 - 1934.136 * JC))

		#Mean Obliq Ecliptic (deg)
		meanObliqEc = 23 + (26 + ((21.448 - JC * (46.815 + JC * (0.00059 - JC * 0.001813))))/60)/60

		#Obliq Corr (deg)
		obliqCorr = meanObliqEc + 0.00256 * cos(radians(125.04-1934.136*JC))

		#Sun Rt Ascenscion (deg)
		sunRtAsc = degrees(atan2(cos(radians(obliqCorr)) * sin(radians(sunAppLong)),cos(radians(sunAppLong))))
																		 
		#Sun Declination (deg)
		sunDecAng  = degrees(asin(sin(radians(obliqCorr))*sin(radians(sunAppLong))))

		#var y
		var_y = tan(radians(obliqCorr/2)) * tan(radians(obliqCorr/2))

		#Eq of Time (minutes)
		eqTime = 4 * degrees(var_y * sin(2 * radians(gMeanLongSun)) - 2 * eccEarthOrbit * sin(radians(gMeanAnomSun)) + \
					  4 * eccEarthOrbit * var_y * sin(radians(gMeanAnomSun)) * cos(2 * radians(gMeanLongSun)) - 0.5 * var_y * \
					  var_y * sin(4 * radians(gMeanLongSun)) - 1.25 * eccEarthOrbit * eccEarthOrbit * \
					  sin(2 * radians(gMeanAnomSun)))

		#HA Sunrise (deg)
		HASunrise = degrees(acos(cos(radians(90.833))/(cos(radians(self.lat)) * cos(radians(sunDecAng))) - \
						  tan(radians(self.lat)) * tan(radians(sunDecAng))))

		#Solar Noon (LST)
		solarNoon = (720 - 4 * self.lon - eqTime + self.timezone * 60) / 1440

		#Sunrise Time (LST)
		sunriseTime = solarNoon - HASunrise * 4 / 1440

		#Sunset Time (LST)
		sunsetTime = solarNoon + HASunrise * 4 / 1440

		#Sunlight Duration (minutes)
		sunDuration = HASunrise * 8

		#True Solar Time (min)
		hour = (parser.parse(date).hour + 1) / 24
		trueSolarTime = (hour * 1440 + eqTime + 4 * self.lon - 60 * self.timezone) % 1440

		#Hour Angle (deg)
		if trueSolarTime / 4 < 0:
			hourAngle = trueSolarTime / 4 + 180
		else:
			hourAngle = trueSolarTime / 4 - 180

		#Solar Zenith Angle (deg)
		solarZenAng = degrees(acos(sin(radians(self.lat)) * sin(radians(sunDecAng)) + cos(radians(self.lat)) * \
							 cos(radians(sunDecAng)) * cos(radians(hourAngle))))

		#Solar Elevation Angle (deg)
		solarElevationAng = 90 - solarZenAng
		
		#Approx Atmospheric Refraction (deg)
		if solarElevationAng > 85:
			refractionFactor = 0
		elif solarElevationAng > 5:
			refractionFactor = 58.1 / tan(radians(solarElevationAng)) - 0.07/pow(tan(radians(solarElevationAng)),3) + \
								0.000086 / pow(tan(radians(solarElevationAng)),5)
		elif solarElevationAng > -0.575:
			refractionFactor = 1735 + solarElevationAng * (-518.2 + solarElevationAng * (103.4 + solarElevationAng * \
								(-12.79 + solarElevationAng * 0.711)))
		else:
			refractionFactor = -20.772 / tan(radians(solarElevationAng))

		refractionFactor = refractionFactor / 3600

		#Solar Elevation corrected for atm refraction (deg)
		solarElevationAngCorr = solarElevationAng + refractionFactor

		#Solar Azimuth Angle (deg cw from N)
		#hourAngle = 10
		if hourAngle > 0:
			solarAzimuth = (degrees(acos(((sin(radians(self.lat)) * cos(radians(solarZenAng))) - sin(radians(sunDecAng))) / (cos(radians(self.lat)) * sin(radians(solarZenAng))))) + 180) % 360
		else:
			solarAzimuth = (540 - degrees(acos(((sin(radians(self.lat)) * cos(radians(solarZenAng))) - sin(radians(sunDecAng))) / (cos(radians(self.lat)) * sin(radians(solarZenAng)))))) % 360

		if debug == True:
			print(f"Julian Day: {JD}")
			print(f"Julian Century: {JC}")
			print(f"Geom Mean Long Sun (deg): {gMeanLongSun}")
			print(f"Geom Mean Anom Sun (deg): {gMeanAnomSun}")
			print(f"Eccent Earth Orbit: {eccEarthOrbit}")
			print(f"Sun Eq of Ctr: {sunCtr}")
			print(f"Sun True Long (deg): {sunTrueLong}")
			print(f"Sun True Anom (deg): {sunTrueAnom}")
			print(f"Sun Rad Vector (AUs): {sunRadVec}")
			print(f"Sun App Long (deg): {sunAppLong}")
			print(f"Mean Obliq Ecliptic (deg): {meanObliqEc}")
			print(f"Obliq Corr (deg): {obliqCorr}")
			print(f"Sun Rt Ascen (deg): {sunRtAsc}")
			print(f"Sun Declination (deg): {sunDecAng}")
			print(f"var y: {var_y}")
			print(f"Eq of Time (minutes): {eqTime}")
			print(f"HA Sunrise (deg): {HASunrise}")
			print(f"Solar Noon (LST): {solarNoon}")
			print(f"Sunrise Time (LST): {sunriseTime}")
			print(f"Sunset Time (LST): {sunsetTime}")
			print(f"Sunlight Duration (minutes): {sunDuration}")
			print(f"True Solar Time (min): {trueSolarTime}")
			print(f"Hour Angle (deg): {hourAngle}")
			print(f"Solar Zenith Angle (deg): {solarZenAng}")
			print(f"Solar Elevation Angle (deg): {solarElevationAng}")
			print(f"Approx Atmospheric Refraction (deg): {refractionFactor}")
			print(f"Solar Elevation corrected for atm refraction (deg): {solarElevationAngCorr}")
			print(f"Solar Azimuth Angle (deg cw from N): {solarAzimuth}")
			
		inter = {"Azimuth" : solarAzimuth,
			"Hohenwinkel" : solarElevationAngCorr
		}
		return inter

	def CalcGlobalstrahlung(self, hohenwinkel, debug = False):
		sConst = 1.367 #kW/m²
		#Airmass
		airMass = 1/sin(radians(hohenwinkel))
		
		#Direkte Sonnenstrahlung in kW/m²
		dSolarRadiation = sConst * ((1-0.14*self.elevation)*0.7**(airMass**0.678)+0.14*self.elevation)
		
		#Annahme dass die diffuse Strahlung 10% der direkten ausmacht
		dGlobalSolarRadiation = dSolarRadiation * 1.1
		
		
		if debug == True:
			print(f"AirMass {airMass}")
			print(f"Direkte Solare Strahlung {dSolarRadiation} kW/m²")
			print(f"Globale Solare Strahlung {dGlobalSolarRadiation} kW/m²")
		return dGlobalSolarRadiation


	def AddOrientationandTilt(self, obj, face, angles, dGlobalSolarRadiation):
		inter = []
		inter.append(list(obj.vertices[face[0][0]-1]))
		inter.append(list(obj.vertices[face[0][1]-1]))
		inter.append(list(obj.vertices[face[0][2]-1]))
		inter.append(list(obj.vertices[face[0][3]-1]))

		P1 = obj.vertices[face[0][0]-1]
		P2 = obj.vertices[face[0][1]-1]
		P3 = obj.vertices[face[0][2]-1]
		P4 = obj.vertices[face[0][3]-1]

		X = set([P1[0],P2[0],P3[0],P4[0]])
		Y = set([P1[1],P2[1],P3[1],P4[1]])
		Z = set([P1[2],P2[2],P3[2],P4[2]])
		
		if len(Z) == 2:
			moduleTilt = 180
		else:
			moduleTilt = 90

		X_diff = max(X) - min(X)
		Y_diff = max(Y) - min(Y)

		moduleOrientation = degrees(atan(min([X_diff,Y_diff])/max([X_diff,Y_diff])))

		print(f"Wand Azimuth {moduleOrientation}°")
		print(f"Wand Tilt {moduleTilt}°")
		#inter = [item for sublist in inter for item in sublist]
		#max_key = max(Counter(inter), key=Counter(inter).get)
		#index = list(obj.vertices[face[0][0]-1]).index(max_key)
		#print(obj.vertices[face[0][0]-1][index])
		#test = Counter(inter)
		
		hohenwinkel = radians(angles["Hohenwinkel"])
		azimuth = radians(angles["Azimuth"])
		moduleTilt = radians(moduleTilt) #Pitch
		moduleOrientation = radians(moduleOrientation) #Yaw


		reductionFactor = ((cos(hohenwinkel)*sin(moduleTilt)*\
			cos(moduleOrientation-azimuth))+sin(hohenwinkel)*cos(moduleTilt))
		reducedGlobalSolarRadiation = dGlobalSolarRadiation * reductionFactor
		print(f"Reduzierte Globalstrahlung {reducedGlobalSolarRadiation}kW/m²")
		return
sun = Sonne()
date = "2006-06-21 14:00:00"
sun.Init("Berlin")
test = sun.CalcSonnenstand(date, debug = False)
sun.CalcGlobalstrahlung(hohenwinkel = test["Hohenwinkel"], debug = False)
