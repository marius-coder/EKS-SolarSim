from OpenGL.GL import *
from OpenGL.GLU import *


def DrawLine(v1, v2):
	"""Zeichnet eine Linie zwischen zwei gegebenen Koordinaten
	Input: v1, v2 als Liste mit X,Y,Z als Koordinaten
	"""
	glBegin(GL_LINES)
	glVertex3f(v1[0], v1[1], v1[2])
	glVertex3f(v2[0], v2[1], v2[2])
	glEnd()


def CreateConvexPolygon(obj):

	#Zuerst werden alle horizontalen Flchen herausgefunden
	z_levels = []
	dic_Coords = {}
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
				if P[0] > dic_Coords[str(P1[2])][0][1]:
					dic_Coords[str(P1[2])][0][1] = P[0]

				if P[1] < dic_Coords[str(P1[2])][1][0]:
					dic_Coords[str(P1[2])][1][0] = P[1]
				if P[1] > dic_Coords[str(P1[2])][1][1]:
					dic_Coords[str(P1[2])][1][1] = P[1]
			

	#Mit denen werden nun die Eckpunkte der Gebude Markiert



	print("")
	return