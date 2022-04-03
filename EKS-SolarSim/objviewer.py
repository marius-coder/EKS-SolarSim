# -*- coding: latin-1 -*-
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import *

from Data.Sonnenstand import Sonne
from Raytrace import DrawLine
import math

pygame.init()
display = (1280, 720)
scree = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)

glShadeModel(GL_SMOOTH)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])

obj = OBJ("Building1.obj", swapyz=True)

obj.generate()
obj_Sun = OBJ(".\Objects\Sonne\Sonne.obj", swapyz=True)
obj_Sun.generate()

glMatrixMode(GL_PROJECTION)
gluPerspective(90, (display[0]/display[1]), 0.1, 5000.0)

glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -8, 0, 0, 0, 0, 0, 0, 1)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

# init mouse movement and center mouse on screen
displayCenter = [scree.get_size()[i] // 2 for i in range(2)]
mouseMove = [0, 0]
pygame.mouse.set_pos(displayCenter)

x = 0
y = 0  
A = 0

hour = 0
#Sonne Initialisieren
sun = Sonne()
sun.Init("Berlin")

up_down_angle = 0.0
paused = False
run = True
calculate = False
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                run = False
            if event.key == pygame.K_PAUSE or event.key == pygame.K_p:
                paused = not paused
                pygame.mouse.set_pos(displayCenter) 
        if not paused: 
            if event.type == pygame.MOUSEMOTION:
                mouseMove = [event.pos[i] - displayCenter[i] for i in range(2)]
            pygame.mouse.set_pos(displayCenter)    

    if not paused:
        # get keys
        keypress = pygame.key.get_pressed()

        if keypress[pygame.K_UP]:  
            y += 1
        if keypress[pygame.K_DOWN]:
            y -= 1
        if keypress[pygame.K_LEFT]:
            x -= 1
        if keypress[pygame.K_RIGHT]:
            x += 1
        if keypress[pygame.K_HOME]:  
            calculate = True
        if keypress[pygame.K_END]: 
            calculate = False
        # init model view matrix
        glLoadIdentity()

        # apply the look up and down
        up_down_angle += mouseMove[1]*0.1
        glRotatef(up_down_angle, 1.0, 0.0, 0.0)

        # init the view matrix
        glPushMatrix()
        glLoadIdentity()

        # apply the movment 
        camera_Speed = 0.2
        if keypress[pygame.K_w]:
            glTranslatef(0,0,camera_Speed)
        if keypress[pygame.K_s]:
            glTranslatef(0,0,-camera_Speed)
        if keypress[pygame.K_d]:
            glTranslatef(-camera_Speed,0,0)
        if keypress[pygame.K_a]:
            glTranslatef(camera_Speed,0,0)
        if keypress[pygame.K_SPACE]:
            glTranslatef(0,-camera_Speed,0)
        if keypress[pygame.K_LSHIFT]:
            glTranslatef(0,camera_Speed,0)
        if keypress[pygame.K_KP_PLUS]:
            hour += 1
        if keypress[pygame.K_KP_MINUS]:
            hour -= 1

        # apply the left and right rotation
        glRotatef(mouseMove[0]*0.1, 0.0, 1.0, 0.0)

        # multiply the current matrix by the get the new view matrix and store the final vie matrix 
        glMultMatrixf(viewMatrix)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        # apply view matrix
        glPopMatrix()
        glMultMatrixf(viewMatrix)

        glLightfv(GL_LIGHT0, GL_POSITION, [sun.x, sun.y, sun.z])

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glRotatef(A,1,1,1)
        glScalef(-1.0, 1.0, 1.0)
        obj.render()
        glPopMatrix()

        glPushMatrix()

        glColor4f(0.5, 0.5, 0.5, 1)
        glBegin(GL_QUADS)
        glVertex3f(-10, -10, -2)
        glVertex3f(10, -10, -2)
        glVertex3f(10, 10, -2)
        glVertex3f(-10, 10, -2)
        glEnd()



        cx = 0
        cy = 0
        print(f"Stunde: {hour}")
        if hour < 0:
            hour = 23
        elif hour > 23:
            hour = 0
        angles = sun.CalcSonnenstand("2022-06-21 "+str(hour)+":00:00")
        print(f"Azimuth: {angles['Azimuth']}")
        print(f"Hohenwinkel: {angles['Hohenwinkel']}")
        sun.x = y * math.sin(math.radians(angles["Hohenwinkel"])) * math.cos(math.radians(angles["Azimuth"]))        
        sun.y = y * math.sin(math.radians(angles["Hohenwinkel"])) * math.sin(math.radians(angles["Azimuth"]))
        sun.z = y * math.cos(math.radians(angles["Hohenwinkel"])) * -1
        
        print(f"X Koordinate: {sun.x}")
        print(f"Y Koordinate: {sun.y}")
        print(f"Z Koordinate: {sun.z}")

        glTranslate(sun.x, sun.y , sun.z)
        obj_Sun.render()
        glPopMatrix()

        DrawLine([0,0,0], [sun.x,sun.y,sun.z])

        glColor4f(1, 0, 0, 1)
        DrawLine([-100,0,0], [100,0,0])

        glColor4f(0, 1, 0, 1)
        DrawLine([0,-100,0], [0,100,0])

        glColor4f(0, 0, 1, 1)
        DrawLine([0,0,-100], [0,0,100])

        glColor4f(0.5, 0.5, 0.5, 1)
        glLineWidth(2.0)



        globalStrahlung = sun.CalcGlobalstrahlung(hohenwinkel = angles["Hohenwinkel"])
        if calculate == True:
            for face in obj.faces:
            
                print(obj.vertices[face[0][0]-1])
                print(obj.vertices[face[0][1]-1])
                print(obj.vertices[face[0][2]-1])
                print(obj.vertices[face[0][3]-1])
                sun.AddOrientationandTilt(obj, face, angles, globalStrahlung)
                print("----------------------------------")
            calculate = False


        pygame.display.flip()
        pygame.time.wait(10)
        import os
        clear = lambda: os.system('cls')
        clear()

pygame.quit()