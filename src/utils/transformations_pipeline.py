import glm
import numpy as np
import math
from OpenGL.GL import *

### Matrizes Model, View e Projection

def model(t_x=0, t_y=0, t_z=0, s_x=1, s_y=1, s_z=1, r_x=0, r_y=0, r_z=0): 
    matrix_transform = glm.mat4(1.0) # instanciando uma matriz identidade
       
    # aplicando translacao (terceira operação a ser executada)
    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))
    
    # aplicando rotacao (segunda operação a ser executada)
    # eixo x
    matrix_transform = glm.rotate(matrix_transform, math.radians(r_x), glm.vec3(1, 0, 0))
    
    # eixo y
    matrix_transform = glm.rotate(matrix_transform, math.radians(r_y), glm.vec3(0, 1, 0))
    
    # eixo z
    matrix_transform = glm.rotate(matrix_transform, math.radians(r_z), glm.vec3(0, 0, 1))
    
    # aplicando escala (primeira operação a ser executada)
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))
    
    matrix_transform = np.array(matrix_transform)
    
    return matrix_transform

# --------------------------------------------------------

def view(pos, front, up, toNumpy=False):
    mat_view = glm.lookAt(pos, pos + front, up)
    if toNumpy:
        mat_view = np.array(mat_view)
    return mat_view

# --------------------------------------------------------

def projection(fov, width, height, toNumpy=False):
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(fov), width/height, 0.1, 100.0)
    if toNumpy:
        mat_projection = np.array(mat_projection)
    return mat_projection

# --------------------------------------------------------
