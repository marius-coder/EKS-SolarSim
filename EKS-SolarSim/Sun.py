from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *


class Sun:
    def __init__(self, obj):
        self.obj = obj
        self.pos = [0, 0, 0]

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glBegin(GL_LINES)
        for edge in player.edges:
            for vertex in edge:
                glVertex3fv(player.vertices[vertex])
        glEnd()
        glPopMatrix()