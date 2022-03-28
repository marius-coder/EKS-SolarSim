# -*- coding: latin-1 -*-
import dateutil.parser as parser
from math import sin,cos,tan,atan2,atan,degrees,radians,asin
import pandas as pd


class Sonne:
	JD_Base = 2451545 #Julianisches Datum

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
	def CalcSonnenstand(self,date, geoBreite, geoLange):
		JD = self.CalcJulianischesDatum(date)
		#Zeitvariable
		n = JD - self.JD_Base
		print(f"n: {n}")
		#Position der Sonne auf der Ekliptik
		L = (280.46 + 0.9856474 * n) % 360
		print(f"L: {L}")
		#Einfluss der Bahnelliptizität
		g = (357.528 + 0.9856003 * n) % 360
		print(f"g: {g}")
		#ekliptikale Länge der Sonne
		Lambda = L + 1.915 * sin(radians(g)) + 0.01997 * sin(radians(2*g))
		print(f"Lambda: {Lambda}")
		#Äquatorialkoordinaten der Sonne
		e = 23.439 - 0.0000004 * n
		print(f"e: {e}")
		if cos(radians(Lambda)) > 0:
			alpha = degrees(atan(cos(radians(e)) * tan(radians(Lambda))))
		elif cos(radians(Lambda)) < 0:
			alpha = degrees(atan(cos(radians(e)) * tan(radians(Lambda))) + 4 * atan(1))
		print(f"alpha: {alpha}")
		#senkrecht zum Himmelsäquator gezählte Deklination
		d = degrees(asin(sin(radians(e))*sin(radians(Lambda))))
		print(f"Deklination: {d}")
		#T0 in julianischen Jahrhunderten
		year = parser.parse(date).year
		month = parser.parse(date).month
		day = parser.parse(date).day
		hour = parser.parse(date).hour
		minute = parser.parse(date).minute
		second = parser.parse(date).second
		ts = pd.Timestamp(year = year,  month = month, day = day,  
                  hour = 0)
		print(f"JD0: {ts.to_julian_date()}")
		T0 = (ts.to_julian_date() - self.JD_Base) / 36525
		print(f"T0: {T0}")
		#mittlere Sternzeit Theta in Greenwich für den gesuchten Zeitpunkt T 
		T = hour + minute / 60 + second / 3600
		Theta_Null = (6.697376 + 2400.05134 * T0 + 1.002738 * T) % 24
		print(f"Theta_Null: {Theta_Null}")
		#Stundenwinkel des Frühlingspunkts
		Theta = Theta_Null * 15 + geoLange
		print(f"Theta: {Theta}")
		#Stundenwinkel tau  der Sonne für jenen Ort:
		tau = radians(Theta - alpha)
		#Azimuth der Sonne
		links = cos(tau)*sin(radians(geoBreite))
		rechts = tan(radians(d)) * cos(radians(geoBreite))
		Azimuth = degrees(atan((sin(tau)/(links-rechts))))
		if links-rechts < 0:
			Azimuth += 180
			Azimuth = Azimuth - 360
		print(f"Azimuth: {Azimuth}")
		#Hohenwinkel
		h = degrees(asin(cos(radians(d))*cos(tau)*cos(radians(geoBreite))+sin(radians(d))*sin(radians(geoBreite))))
		print(f"Hohenwinkel: {h}")
		#Korrektur des Hohenwinkel wegen Refraktion
		#10.3/(radians(h)+5.11)
		R = 1.02/tan(radians(h)+radians(10.3/(h+5.11)))
		hr = h + R / 60
		print(f"Hohenwinkel Korrektiert: {hr}")
		inter = {"Azimuth" : Azimuth,
				"Höhenwinkel" : hr
			}
		return inter

	def CalcGlobalstrahlung(self, hohenwinkel, seehohe):
		sConst = 1.367 #kW/m²
		#Airmass
		airMass = 1/sin(radians(hohenwinkel))
		print(f"AirMass {airMass}")
		dSolarRadiation = sConst * ((1-0.14*seehohe)*0.7**(airMass**0.678)+0.14*seehohe)
		print(f"Direkte Solare Strahlung {dSolarRadiation}")
		#Annahme dass die diffuse Strahlung 10% der direkten ausmacht
		dSolarRadiation = dSolarRadiation * 1.1
		print(f"Direkte Solare Strahlung {dSolarRadiation}")

sun = Sonne()
test = sun.CalcSonnenstand("2006-06-22 12:00:00", geoBreite = 52.31, geoLange = 13.24)
sun.CalcGlobalstrahlung(hohenwinkel = test["Höhenwinkel"], seehohe = 0.5)