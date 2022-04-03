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