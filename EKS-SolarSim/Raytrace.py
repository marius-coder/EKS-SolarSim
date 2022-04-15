# -*- coding: latin-1 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
import GJK
from scipy.spatial import ConvexHull


def DrawLine(v1, v2):
	"""Zeichnet eine Linie zwischen zwei gegebenen Koordinaten
	Input: v1, v2 als Liste mit X,Y,Z als Koordinaten
	"""
	glBegin(GL_LINES)
	glVertex3f(v1[0], v1[1], v1[2])
	glVertex3f(v2[0], v2[1], v2[2])
	glEnd()

def DrawSunRay(obj_Sunray,v1, v2, mode):
	glPushMatrix()
	x1 = mode[0][0]
	x2 = mode[1][0]
	y1 = mode[0][1]
	y2 = mode[1][1]	

	obj_Sunray.vertices[0] = tuple(list([x1 ,y1, v2[2]+1]))
	obj_Sunray.vertices[1] = tuple(list([x1, y1, v2[2]-1]))
	obj_Sunray.vertices[2] = tuple(list([v2[0], v2[1], v2[2]+1]))

	obj_Sunray.vertices[3] = tuple(list([v1[0], v1[1], v1[2]]))

	obj_Sunray.generate()
	obj_Sunray.render()
	glPopMatrix()

def GetCoordinates(obj_Sunray, v2, obj, face, angles, r, sun):
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
		
	print(f"V1 Before {inter[0]}")
	print(f"V1 Before {inter[1]}")
	print(f"V1 Before {inter[2]}")
	print(f"V1 Before {inter[3]}")

	x1 = r * math.cos(math.radians(angles["Hohenwinkel"])) * math.cos(math.radians(angles["Azimuth"]+1))        
	y1 = r * math.cos(math.radians(angles["Hohenwinkel"])) * math.sin(math.radians(angles["Azimuth"]+1))

	x2 = r * math.cos(math.radians(angles["Hohenwinkel"])) * math.cos(math.radians(angles["Azimuth"]-1))        
	y2 = r * math.cos(math.radians(angles["Hohenwinkel"])) * math.sin(math.radians(angles["Azimuth"]-1))

	mode = [[x1,y1],[x2,y2]]
	DrawSunRay(obj_Sunray,v2 = v2, v1 = P1, mode = mode)



def CreateConvexPolygon(obj):
	"""Diese Funktion nimmt ein Gebaude welches nur aus Quadern bestehen darf, und teilt 
	dieses in Konvexe Quader.
	Diese Funktion ist sehr ineffizient. Gehört refactort. Aber Sie funktioniert also fasse ich da nix an"""

	#Zuerst werden alle horizontalen Flachen herausgefunden
	z_levels = []
	dic_Coords = {}
	dic_result = {}
	for face in obj.faces:
		P1 = obj.vertices[face[0][0]-1]
		P2 = obj.vertices[face[0][1]-1]
		P3 = obj.vertices[face[0][2]-1]
		P4 = obj.vertices[face[0][3]-1]
		points = [P1, P2, P3, P4]
		if len(set([P1[2],P2[2],P3[2],P4[2]])) == 1:
			P1 = [P1[0],P1[1],round(P1[2],0)]
			P1[2] = round(P1[2],0)
			if P1[2] not in z_levels:
				z_levels.append(P1[2])
				dic_Coords[str(P1[2])] = [[999999999,-999999999],[999999999,-999999999],P1[2]]
				
			for P in points:
				if P[0] < dic_Coords[str(P1[2])][0][0]:
					dic_Coords[str(P1[2])][0][0] = P[0]
					edge1 = [P[0],P[1],P1[2]]
				if P[0] > dic_Coords[str(P1[2])][0][1]:
					dic_Coords[str(P1[2])][0][1] = P[0]
					edge2 = [P[0],P[1],P1[2]]
				if P[1] < dic_Coords[str(P1[2])][1][0]:
					dic_Coords[str(P1[2])][1][0] = P[1]
					edge3 = [P[0],P[1],P1[2]]
				if P[1] > dic_Coords[str(P1[2])][1][1]:
					dic_Coords[str(P1[2])][1][1] = P[1]
					edge4 = [P[0],P[1],P1[2]]
				dic_result[str(P1[2])] = [edge1, edge2, edge3, edge4]
	del dic_result["0.0"]
	return dic_result


def DrawQuad(obj):
	glBegin(GL_LINE_LOOP)
	for ver in obj:
		for ver2 in obj:
			glVertex3f(ver[0],ver[1],ver[2])
			glVertex3f(ver2[0],ver2[1],ver2[2])
	glEnd()

def MinkowskiDifference(obj, sunRay):
	#TODO Für alle Konvexen Objekte eines Gebaudes siehe Line vertObj = list(obj.values())[0]
	"""Diese Funktion berechnet die Minkowsky Differenz für zwei Objekte
	Falls gewollt wird das Ergebnis gezeichnet"""
	def CreateCoords(arg, height1, height2 = 0):
		"""Nimmt die Bounding Koordinaten des Konvexen Quaders und erstellt vector Koordinaten daraus"""
		vec1 = [arg[0][0], arg[0][1], height2]
		vec2 = [arg[1][0], arg[1][1], height2]
		vec3 = [arg[2][0], arg[2][1], height2]
		vec4 = [arg[3][0], arg[3][1], height2]
		vec5 = [arg[0][0], arg[0][1], height1]
		vec6 = [arg[1][0], arg[1][1], height1]
		vec7 = [arg[2][0], arg[2][1], height1]
		vec8 = [arg[3][0], arg[3][1], height1]
		return [vec1, vec2, vec3, vec4, vec5, vec6, vec7, vec8]
	#vertObj = list(obj.values())[0] #Bounding Koordinaten extrahieren
	#vecObj = CreateCoords(vertObj,0) #Vector Koordinaten erstellen
	#glColor4f(0, 0, 1, 1)
	#DrawQuad(vecObj)
	

	#vertObj = list(obj.values())[2] #Bounding Koordinaten extrahieren
	#vecObj1 = CreateCoords(vertObj,7) #Vector Koordinaten erstellen
	#glColor4f(0, 1, 0, 1)
	#DrawQuad(vecObj1)
	#print(f"Kollision [{vecObj[0][2]}]: {ContainsOrigin(vecObj, vecObj1)}")
	anzCol = 0
	for key,vertObj in obj.items():#Bounding Koordinaten extrahieren
		vecObj = CreateCoords(vertObj, height1 = float(key)) #Vector Koordinaten erstellen
		print(f"Kollision [{vecObj[4][2]}]: {GJK.CheckCollision(vecObj, sunRay)}")
		if GJK.CheckCollision(vecObj, sunRay):
			anzCol += 1
	if anzCol > 1:
		print(f"Kollision gefunden")
	else:
		print(f"Keine Kollision")
	return



