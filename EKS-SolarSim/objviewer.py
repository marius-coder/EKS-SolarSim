# -*- coding: latin-1 -*-
# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

import math
# IMPORT OBJECT LOADER
from objloader import *

from Sun import Sun
from camera import Camera

pygame.init()
cam = Camera()
first_mouse = True
global left, right, forward, backward
left, right, forward, backward = False, False, False, False
viewport = (800,600)
hx = viewport[0]/2
hy = viewport[1]/2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

# LOAD OBJECT AFTER PYGAME INIT
obj = OBJ("untitled.obj", swapyz=True)
for i,face in enumerate(obj.faces):
        if i % 2 == 0:
            face = list(face)
            face[-1] = "Red"
            obj.faces[i] = tuple(face)
obj.generate()
obj_Sun = OBJ(".\Objects\Sonne\Sonne.obj", swapyz=True)
obj_Sun.generate()

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(90, width/float(height), 1, 100.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

rx, ry = (0,0)
tx, ty = (0,0)
zpos = 5
rotate = move = False

x = 0
y = 0  
A = 0
up_down_angle = 0.0
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

# init mouse movement and center mouse on screen
displayCenter = [srf.get_size()[i] // 2 for i in range(2)]
mouseMove = [0, 0]
pygame.mouse.set_pos(displayCenter)
def do_movement():
    #Camera Movement
    if left:
        cam.process_keyboard("LEFT", 0.05)
    if right:
        cam.process_keyboard("RIGHT", 0.05)
    if forward:
        cam.process_keyboard("FORWARD", 0.05)
    if backward:
        cam.process_keyboard("BACKWARD", 0.05)
def mouse_look_clb(window, xpos, ypos):
    global first_mouse, lastX, lastY

    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos

    lastX = xpos
    lastY = ypos

    cam.process_mouse_movement(xoffset, yoffset)

while 1:
    clock.tick(30)
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: zpos = max(1, zpos-1)
            elif e.button == 5: zpos += 1
            elif e.button == 1: rotate = True
            elif e.button == 3: move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: rotate = False
            elif e.button == 3: move = False
        elif e.type == MOUSEMOTION:
            mouseMove = [e.pos[i] - displayCenter[i] for i in range(2)]
            i, j = e.rel
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j
        keypress = pygame.key.get_pressed()
                   # init model view matrix
        glLoadIdentity()

        # apply the look up and down
        up_down_angle += mouseMove[1]*0.1
        glRotatef(up_down_angle, 1.0, 0.0, 0.0)

        # init the view matrix
        glPushMatrix()
        glLoadIdentity()
        #Camera Movement
        if keypress[pygame.K_w]:
            glTranslatef(0,0,0.1)
        if keypress[pygame.K_s]:
            glTranslatef(0,0,-0.1)
        if keypress[pygame.K_a]:
            glTranslatef(0.1,0,0)
        if keypress[pygame.K_d]:
            glTranslatef(-0.1,0,0)

        if keypress[pygame.K_UP]:  
            y += 1
        if keypress[pygame.K_DOWN]:
            y -= 1
        if keypress[pygame.K_LEFT]:
            x -= 1
        if keypress[pygame.K_RIGHT]:
            x += 1
        if keypress[pygame.K_PAGEUP]:  
            A += 30
        if keypress[pygame.K_PAGEDOWN]: 
            A-= 30
                
        # apply the left and right rotation
        glRotatef(mouseMove[0]*0.1, 0.0, 1.0, 0.0)

        # multiply the current matrix by the get the new view matrix and store the final vie matrix 
        glMultMatrixf(viewMatrix)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        # apply view matrix
        glPopMatrix()
        glMultMatrixf(viewMatrix)

    do_movement()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()



    # RENDER OBJECT
    glTranslate(tx/20., ty/20., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)   

    obj.render()   
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport
    #gluPerspective(90.0, width/float(height), 1, 100.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()# RENDER OBJECT

    cx = 0
    cy = 0
    
    X = cx + (x-cx)*math.cos(math.radians(A)) - (y-cy)*math.sin(math.radians(A))
    Y = cx + (x-cx)*math.sin(math.radians(A)) + (y-cy)*math.cos(math.radians(A))
    glTranslate(X, Y, - zpos)
    obj_Sun.render()

    pygame.display.flip()


