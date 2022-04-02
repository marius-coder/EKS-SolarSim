# -*- coding: latin-1 -*-
import dateutil.parser as parser
from math import sin,cos,tan,atan2,atan,degrees,radians,asin
from collections import Counter
import pandas as pd
import requests
import urllib.parse

class Sonne:
	JD_Base = 2451545 #Julianisches Datum

	def from_address(self, address_string="Stephansplatz, Wien, Österreich"):
		parsed_address = urllib.parse.quote(address_string)
		url = 'https://nominatim.openstreetmap.org/search/' + parsed_address +'?format=json'
		response = requests.get(url).json()
		self.lat = float(response[0]["lat"])
		self.lon = float(response[0]["lon"])

	def elevation_function(self):
		url = 'https://api.opentopodata.org/v1/aster30m?locations=' + str(self.lat) + ','+ str(self.lon)
		response = requests.get(url).json()
		self.elevation = response['results'][0]['elevation'] / 1000

	def Init(self,address):
		self.from_address(address)
		self.elevation_function()

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
		JD = self.CalcJulianischesDatum(date)
		#Zeitvariable
		n = JD - self.JD_Base
		
		#Position der Sonne auf der Ekliptik
		L = (280.46 + 0.9856474 * n) % 360
		
		#Einfluss der Bahnelliptizität
		g = (357.528 + 0.9856003 * n) % 360
		
		#ekliptikale Länge der Sonne
		Lambda = L + 1.915 * sin(radians(g)) + 0.01997 * sin(radians(2*g))
		
		#Äquatorialkoordinaten der Sonne
		e = 23.439 - 0.0000004 * n
		
		if cos(radians(Lambda)) > 0:
			alpha = degrees(atan(cos(radians(e)) * tan(radians(Lambda))))
		elif cos(radians(Lambda)) < 0:
			alpha = degrees(atan(cos(radians(e)) * tan(radians(Lambda))) + 4 * atan(1))
		
		#senkrecht zum Himmelsäquator gezählte Deklination
		d = degrees(asin(sin(radians(e))*sin(radians(Lambda))))
		
		#T0 in julianischen Jahrhunderten
		year = parser.parse(date).year
		month = parser.parse(date).month
		day = parser.parse(date).day
		hour = parser.parse(date).hour
		minute = parser.parse(date).minute
		second = parser.parse(date).second
		ts = pd.Timestamp(year = year,  month = month, day = day,  
                  hour = 0)
		
		T0 = (ts.to_julian_date() - self.JD_Base) / 36525
		
		#mittlere Sternzeit Theta in Greenwich für den gesuchten Zeitpunkt T 
		T = hour + minute / 60 + second / 3600
		Theta_Null = (6.697376 + 2400.05134 * T0 + 1.002738 * T) % 24
		
		#Stundenwinkel des Frühlingspunkts
		Theta = Theta_Null * 15 + self.lon
		
		#Stundenwinkel tau  der Sonne für jenen Ort:
		tau = radians(Theta - alpha)
		#Azimuth der Sonne
		links = cos(tau)*sin(radians(self.lat))
		rechts = tan(radians(d)) * cos(radians(self.lat))
		Azimuth = degrees(atan((sin(tau)/(links-rechts))))
		if links-rechts < 0:
			Azimuth += 180
			Azimuth = Azimuth - 360
		
		#Hohenwinkel
		h = degrees(asin(cos(radians(d))*cos(tau)*cos(radians(self.lat))+sin(radians(d))*sin(radians(self.lat))))
		
		#Korrektur des Hohenwinkel wegen Refraktion
		R = 1.02/tan(radians(h)+radians(10.3/(h+5.11)))
		hr = h + R / 60
		
		inter = {"Azimuth" : Azimuth,
				"Hohenwinkel" : hr
			}
		if debug == True:
			print(f"n: {n}")
			print(f"L: {L}")
			print(f"g: {g}")
			print(f"Lambda: {Lambda}")
			print(f"e: {e}")
			print(f"alpha: {alpha}")
			print(f"Deklination: {d}")
			print(f"JD0: {ts.to_julian_date()}")
			print(f"T0: {T0}")
			print(f"Theta_Null: {Theta_Null}")
			print(f"Theta: {Theta}")
			print(f"Azimuth: {Azimuth}")
			print(f"Hohenwinkel: {h}")
			print(f"Hohenwinkel Korrektiert: {hr}")
			print(f"Latitude: {self.lat}")
			print(f"Longitude: {self.lon}")			
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
sun.Init("Berlin")
test = sun.CalcSonnenstand("2006-06-22 12:00:00", debug = True)
sun.CalcGlobalstrahlung(hohenwinkel = test["Hohenwinkel"], debug = True)