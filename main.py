from OpenGL.GL import *
from OpenGL.GLUT import *
import cv2
import numpy as np


def create_shader(shader_type, source):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    return shader


class Transform:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.scale = 1.0
        self.translation = [0.0, 0.0]
        self.dragging = False
        self.last_screen_coords = [0, 0]

    def geo_by_screen_coords(self, screen_coords):
        x = screen_coords[0] * 4 / self.width - 2
        y = 2 - screen_coords[1] * 4 / self.height
        x += self.translation[0]
        y += self.translation[1]
        x *= self.scale
        y *= self.scale
        return [x, y]

    def up_scale(self):
        self.scale *= 1.1
        self.translation[0] /= 1.1
        self.translation[1] /= 1.1
        return self.scale

    def down_scale(self):
        self.scale /= 1.1
        self.translation[0] *= 1.1
        self.translation[1] *= 1.1
        return self.scale

    def update_translation(self, new_screen_coords):
        old_canvas = [self.last_screen_coords[0] * 4 / self.width - 2,
                      2 - self.last_screen_coords[1] / self.height * 4]
        new_canvas = [new_screen_coords[0] / self.width * 4 - 2,
                      2 - new_screen_coords[1] / self.height * 4]
        self.translation[0] -= (new_canvas[0] - old_canvas[0])
        self.translation[1] -= (new_canvas[1] - old_canvas[1])
        self.last_screen_coords = new_screen_coords
        return self.translation


class Fractal:
    def __init__(self):
        width = 1000
        height = 1000
        self.transform = Transform(width, height)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(width, height)
        glutInitWindowPosition(50, 50)
        glutInit()
        glutCreateWindow("Shaders")
        glutDisplayFunc(self.draw)
        glutIdleFunc(self.draw)
        glutKeyboardFunc(self.key_pressed)
        glutSpecialFunc(self.special_pressed)
        glutMotionFunc(self.motion)
        glutMouseFunc(self.mouse)
        glBindTexture(GL_TEXTURE_1D, 1)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        img = cv2.imread('pal.ppm')
        alpha = np.ones(shape=(1, 256, 1), dtype=int)
        img = np.concatenate((img, alpha), axis=2)
        img = np.reshape(img, (256 * 4,), order='C')
        glTexImage1D(GL_TEXTURE_1D, 0, 4, 256, 0, GL_BGRA, GL_UNSIGNED_BYTE, img)
        glEnable(GL_TEXTURE_1D)
        with open('fractal.fs', 'r') as shader_file:
            shader_text = shader_file.read()

        fragment = create_shader(GL_FRAGMENT_SHADER, shader_text)

        program = glCreateProgram()
        glAttachShader(program, fragment)
        glLinkProgram(program)
        self.UNIFORM_LOCATIONS = {
            'u_resolution': glGetUniformLocation(program, 'u_resolution'),
            'max_iterations': glGetUniformLocation(program, 'max_iterations'),
            'threshold': glGetUniformLocation(program, 'threshold'),
            'translation': glGetUniformLocation(program, 'translation'),
            'scale': glGetUniformLocation(program, 'scale')
        }
        glUseProgram(program)
        glUniform1i(self.UNIFORM_LOCATIONS['max_iterations'], 100)
        glUniform1f(self.UNIFORM_LOCATIONS['threshold'], 2.0)
        glUniform2f(self.UNIFORM_LOCATIONS['translation'], 0.0, 0.0)
        glUniform1f(self.UNIFORM_LOCATIONS['scale'], 1.0)
        glutMainLoop()

    def draw(self):
        glClearColor(0.2, 0.2, 0.2, 1)
        glUniform2f(self.UNIFORM_LOCATIONS['u_resolution'], glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
        glEnableClientState(GL_VERTEX_ARRAY)
        points = [[-1.0, -1.0], [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0]]
        glVertexPointer(2, GL_FLOAT, 0, points)
        glDrawArrays(GL_QUADS, 0, 4)
        glDisableClientState(GL_VERTEX_ARRAY)
        glutSwapBuffers()

    def key_pressed(self, key, x, y):
        sys.exit()

    def special_pressed(self, key, x, y):
        if key == GLUT_KEY_UP:
            scale = self.transform.down_scale()
            glUniform1f(self.UNIFORM_LOCATIONS['scale'], scale)
            glUniform2f(self.UNIFORM_LOCATIONS['translation'],
                        self.transform.translation[0],
                        self.transform.translation[1])
        if key == GLUT_KEY_DOWN:
            scale = self.transform.up_scale()
            glUniform1f(self.UNIFORM_LOCATIONS['scale'], scale)
            glUniform2f(self.UNIFORM_LOCATIONS['translation'],
                        self.transform.translation[0],
                        self.transform.translation[1])

    def mouse(self, button, state, x, y):
        if state == 0:
            self.transform.dragging = True
            self.transform.last_screen_coords = [x, y]
        if state == 1:
            self.transform.dragging = False

    def motion(self, x, y):
        translation = self.transform.update_translation([x, y])
        glUniform2f(self.UNIFORM_LOCATIONS['translation'], translation[0], translation[1])


Fractal()
