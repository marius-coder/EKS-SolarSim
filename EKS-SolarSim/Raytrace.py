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

def DrawSunRay(obj_Sunray,v1, v2, mode):
	glPushMatrix()

	obj_Sunray.vertices[4] = tuple(list([v1[0][0], v1[0][1], v1[0][2]]))
	obj_Sunray.vertices[5] = tuple(list([v1[1][0], v1[1][1], v1[1][2]]))
	obj_Sunray.vertices[6] = tuple(list([v1[2][0], v1[2][1], v1[2][2]]))
	obj_Sunray.vertices[7] = tuple(list([v1[3][0], v1[3][1], v1[3][2]]))

	obj_Sunray.vertices[0] = tuple(list([v2[0]-mode[0] ,v2[1]+mode[1], v2[2]+mode[2]]))
	obj_Sunray.vertices[1] = tuple(list([v2[0]-mode[0], v2[1]-mode[1], v2[2]-mode[2]]))
	obj_Sunray.vertices[2] = tuple(list([v2[0]+mode[0], v2[1]+mode[1], v2[2]+mode[2]]))
	obj_Sunray.vertices[3] = tuple(list([v2[0]+mode[0], v2[1]-mode[1], v2[2]-mode[2]]))

	obj_Sunray.generate()
	obj_Sunray.render()

	glPopMatrix()


def GetCoordinates(obj_Sunray, v2, obj, face, az):
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
		
	add_X = 0
	add_Y = 0
	add_Z = 1

	if az <= 45 or az <= 315  :
		add_X = 0
		add_Y = 1

	elif 45 <= az <= 135:		
		add_X = 1
		add_Y = 0

	elif 135 <= az <= 225:
		add_X = 0
		add_Y = 1

	elif 225 <= az <= 315:
		add_X = 1
		add_Y = 0

	print(f"add_X {add_X}")
	print(f"add_Y {add_Y}")
	print(f"add_Z {add_Z}")
	
	DrawSunRay(obj_Sunray,v2 = v2, v1 = inter, mode = [add_X, add_Y, add_Z])



def CreateConvexPolygon(obj):
	"""Diese Funktion nimmt ein Gebaude welches nur aus Quadern bestehen darf, und teilt 
	dieses in Konvexe Quader."""

	#Zuerst werden alle horizontalen Flachen herausgefunden
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
			
	return