"""
Projeto 2 - Navegação em ambientes
Disciplina SCC0250 - Computação Gráfica

----------------------------------------------------------

João Pedro Ribeiro da Silva - 12563727
Miller Matheus Lima Anacleto Rocha - 13727954

Código baseado naqueles desenvolvidos e disponibilizados pelo professor
"""

# bibliotecas
import glfw
from OpenGL.GL import *
import numpy as np
import math
import glm
from numpy import random
import os
path_join = os.path.join

# códigos externos
from shaders.shader_s import Shader
from aux.object_loader import ObjManager
from aux.transformations_pipeline import model, view, projection

# funções auxiliares
def model_objeto(vertice_inicial, num_vertices, program, t_x=0, t_y=0, t_z=0, s_x=1, s_y=1, s_z=1, r_x=0, r_y=0, r_z=0):
    # aplica a matriz model
    mat_model = model(t_x, t_y, t_z,  # translação
                    s_x, s_y, s_z,  # escala
                    r_x, r_y, r_z)  # rotação
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)

# --------------------------------------------------------

def desenha_objeto(vertice_inicial, num_vertices, texture_id=-1):
    # textura
    if texture_id >= 0:
        glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # desenha o objeto
    glDrawArrays(GL_TRIANGLES, vertice_inicial, num_vertices) ## renderizando

# funções callback
def key_event(window,key,scancode,action,mods):
    global cameraPos, cameraFront, cameraUp, deltaTime

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    cameraSpeed = 5 * deltaTime
    if key == glfw.KEY_W and (action == glfw.PRESS or action == glfw.REPEAT):
        cameraPos += cameraSpeed * cameraFront

    if key == glfw.KEY_S and (action == glfw.PRESS or action == glfw.REPEAT):
        cameraPos -= cameraSpeed * cameraFront

    if key == glfw.KEY_A and (action == glfw.PRESS or action == glfw.REPEAT):
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == glfw.KEY_D and (action == glfw.PRESS or action == glfw.REPEAT):
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

# --------------------------------------------------------

def framebuffer_size_callback(window, largura, altura):
    glViewport(0, 0, largura, altura)

# --------------------------------------------------------

def mouse_event(window, xpos, ypos):
    global cameraFront, lastX, lastY, firstMouse, yaw, pitch

    if (firstMouse):
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos # reversed since y-coordinates go from bottom to top
    lastX = xpos
    lastY = ypos

    sensitivity = 0.1 # change this value to your liking
    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset
    pitch += yoffset

    # make sure that when pitch is out of bounds, screen doesn't get flipped
    if (pitch > 89.0):
        pitch = 89.0
    if (pitch < -89.0):
        pitch = -89.0

    front = glm.vec3()
    front.x = glm.cos(glm.radians(yaw)) * glm.cos(glm.radians(pitch))
    front.y = glm.sin(glm.radians(pitch))
    front.z = glm.sin(glm.radians(yaw)) * glm.cos(glm.radians(pitch))
    cameraFront = glm.normalize(front)

# --------------------------------------------------------

def scroll_event(window, xoffset, yoffset):
    global fov

    fov -= yoffset
    if (fov < 1.0):
        fov = 1.0
    if (fov > 45.0):
        fov = 45.0

# MAIN
if __name__ == '__main__':
    ### CONSTANTES IMPORTANTES
    ABSOLUTE_ROOT_PATH, _ = os.path.split(os.path.dirname(os.path.realpath(__file__)))
    LARGURA_JANELA = 700
    ALTURA_JANELA = 700

    ### INICIALIZANDO JANELA
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    window = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, "Cabana Assombrada", None, None)

    if (window == None):
        print("Failed to create GLFW window")
        glfwTerminate()
        exit(1)

    glfw.make_context_current(window)

    ### SHADERS
    shaders_path = path_join(ABSOLUTE_ROOT_PATH, 'src', 'shaders')

    ourShader = Shader(path_join(shaders_path, 'vertex_shader.vs'), path_join(shaders_path, 'fragment_shader.fs'))
    ourShader.use()
    PROGRAM = ourShader.getProgram()

    ### CARREGANDO OBJETOS
    buffer_VBO = glGenBuffers(2)

    ## vertices
    obj_manager = ObjManager()
    objects_path = path_join(ABSOLUTE_ROOT_PATH, 'objetos')

    caixa_madeira_vertices = obj_manager.load_obj(
        path_join(objects_path, 'caixa.obj')
    )
    
    caixa_tijolos_vertices = obj_manager.load_obj(
        path_join(objects_path, 'caixa.obj')
    )

    # carregando na GPU
    all_vertices = obj_manager.get_all_vertices()
    vertices = np.zeros(len(all_vertices), [("position", np.float32, 3)])
    vertices['position'] = all_vertices

    glBindBuffer(GL_ARRAY_BUFFER, buffer_VBO[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)
    loc_vertices = glGetAttribLocation(PROGRAM, "position")
    glEnableVertexAttribArray(loc_vertices)
    glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

    ## texturas
    textures_path = path_join(ABSOLUTE_ROOT_PATH, 'texturas')

    obj_manager.load_textures([
        path_join(textures_path, 'madeira.jpg'),
        path_join(textures_path, 'tijolos.jpg'),
    ])

    # carregando na GPU
    all_texture_coord = obj_manager.textures_coord_list
    textures = np.zeros(len(all_texture_coord), [("position", np.float32, 2)])
    textures['position'] = all_texture_coord

    glBindBuffer(GL_ARRAY_BUFFER, buffer_VBO[1])
    glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
    stride = textures.strides[0]
    offset = ctypes.c_void_p(0)
    loc_texture_coord = glGetAttribLocation(PROGRAM, "texture_coord")
    glEnableVertexAttribArray(loc_texture_coord)
    glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

    # variáveis para os callbacks
    cameraPos   = glm.vec3(0.0, 0.0, 0.0)
    cameraFront = glm.vec3(0.0, 0.0, -1.0)
    cameraUp    = glm.vec3(0.0, 1.0, 0.0)
    deltaTime   = 0.0
    lastFrame   = 0.0

    firstMouse = True
    yaw   = -90.0
    pitch =  0.0
    lastX =  LARGURA_JANELA / 2.0
    lastY =  ALTURA_JANELA / 2.0
    
    fov   =  45.0

    # adicionando callbacks
    glfw.set_key_callback(window,key_event)
    glfw.set_cursor_pos_callback(window, mouse_event)
    glfw.set_scroll_callback(window, scroll_event)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # captura de mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # exibindo janela
    glfw.show_window(window)

    # 3D
    glEnable(GL_DEPTH_TEST)

    ### LOOP PRINCIPAL DA JANELA

    while not glfw.window_should_close(window):
        # setup
        currentFrame = glfw.get_time()
        deltaTime = currentFrame - lastFrame
        lastFrame = currentFrame

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)

        glfw.poll_events()

        ## TRANSFORMAÇÕES

        # model
        slice_vertices_caixa = obj_manager.get_vertices_slice(0)
        model_objeto(*slice_vertices_caixa, PROGRAM, t_z=-10)
        
        desenha_objeto(*slice_vertices_caixa, 0)

        # view
        mat_view = view(cameraPos, cameraFront, cameraUp)
        loc_view = glGetUniformLocation(PROGRAM, "view")
        glUniformMatrix4fv(loc_view, 1, GL_TRUE, mat_view)

        # projection
        mat_projection = projection(fov, LARGURA_JANELA, ALTURA_JANELA)
        loc_projection = glGetUniformLocation(PROGRAM, "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, mat_projection)

        glfw.swap_buffers(window)

    glfw.terminate()