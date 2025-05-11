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
from utils.object_loader import ObjManager
from utils.transformations_pipeline import model, view, projection

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

# --------------------------------------------------------

def camera_movement_handler():
    global window, cameraFront, cameraUp, cameraVel, CAMERA_SPEED, edit_pos
    global tx, ty, tz, rx, ry, rz, s

    OBJ_MOVE_SPEED = 0.001
    OBJ_ROT_SPEED = 0.01

    # W - mover câmera (frente)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cameraVel += glm.normalize(cameraFront)
    # S - mover câmera (trás)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cameraVel -= glm.normalize(cameraFront)
    # A - mover câmera (esquerda)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        cameraVel -= glm.normalize(glm.cross(cameraFront, cameraUp))
    # D - mover câmera (direita)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        cameraVel += glm.normalize(glm.cross(cameraFront, cameraUp))
    
    if glm.length(cameraVel) > 0:
        cameraVel = glm.normalize(cameraVel) * CAMERA_SPEED

    ###################################    
    if glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS:
        if edit_pos:
            tx += OBJ_MOVE_SPEED
        else:
            rx += OBJ_ROT_SPEED
        
    if glfw.get_key(window, glfw.KEY_X) == glfw.PRESS:
        if edit_pos:
            tx -= OBJ_MOVE_SPEED
        else:
            rx -= OBJ_ROT_SPEED
        
    if glfw.get_key(window, glfw.KEY_C) == glfw.PRESS:
        if edit_pos:
            ty += OBJ_MOVE_SPEED
        else:
            ry += OBJ_ROT_SPEED
        
    if glfw.get_key(window, glfw.KEY_V) == glfw.PRESS:
        if edit_pos:
            ty -= OBJ_MOVE_SPEED
        else:
            ry -= OBJ_ROT_SPEED
        
    if glfw.get_key(window, glfw.KEY_B) == glfw.PRESS:
        if edit_pos:
            tz += OBJ_MOVE_SPEED
        else:
            rz += OBJ_ROT_SPEED
        
    if glfw.get_key(window, glfw.KEY_N) == glfw.PRESS:
        if edit_pos:
            tz -= OBJ_MOVE_SPEED
        else:
            rz -= OBJ_ROT_SPEED
        
    if glfw.get_key(window, glfw.KEY_F) == glfw.PRESS:
        s += OBJ_MOVE_SPEED
        
    if glfw.get_key(window, glfw.KEY_G) == glfw.PRESS:
        s -= OBJ_MOVE_SPEED

# funções callback
def key_event(window,key,scancode,action,mods):
    global show_lines, edit_pos
    # ESC - fechar janela
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    # P - exibir malha poligonal
    if key == glfw.KEY_P and action == glfw.PRESS:
        show_lines = not show_lines
        if show_lines:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    if key == glfw.KEY_TAB and action == glfw.PRESS:
        edit_pos = not edit_pos

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

    casa_vertices = obj_manager.load_obj(
        path_join(objects_path, 'casa.obj')
    )

    mesa_escritorio = obj_manager.load_obj(
        path_join(objects_path, 'mesa_escritorio.obj')
    )

    mesa = obj_manager.load_obj(
        path_join(objects_path, 'mesa.obj')
    )

    cama = obj_manager.load_obj(
        path_join(objects_path, 'cama.obj')
    )

    machado = obj_manager.load_obj(
        path_join(objects_path, 'machado.obj')
    )

    papel = obj_manager.load_obj(
        path_join(objects_path, 'papel.obj')
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
        path_join(textures_path, 'casa.png'),
        path_join(textures_path, 'mesa_escritorio.jpg'),
        path_join(textures_path, 'mesa.png'),
        path_join(textures_path, 'cama.png'),
        path_join(textures_path, 'machado.jpg'),
        path_join(textures_path, 'papel.png'),
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

    # variáveis para a movimentação da câmera
    cameraPos   = glm.vec3(0.0, 0.0, -30.0)
    cameraFront = glm.vec3(0.0, 0.0, -1.0)
    cameraUp    = glm.vec3(0.0, 1.0, 0.0)
    cameraVel   = glm.vec3(0.0, 0.0, 0.0)
    CAMERA_SPEED = 5
    deltaTime   = 0.0
    lastFrame   = 0.0

    
    tx = ty = tz = rx = ry = rz = 0.0
    s = 1.0

    # variáveis para os callbacks
    show_lines = False
    edit_pos = True

    firstMouse = True
    yaw   = -90.0
    pitch =  0.0
    lastX =  LARGURA_JANELA / 2.0
    lastY =  ALTURA_JANELA / 2.0
    
    fov   =  45.0

    # adicionando callbacks
    glfw.set_key_callback(window, key_event)
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

        glfw.poll_events()
        camera_movement_handler()

        ## TRANSFORMAÇÕES

        # model
        slice_vertices_caixa1 = obj_manager.get_vertices_slice(obj_index=0)
        model_objeto(*slice_vertices_caixa1, PROGRAM, t_x=-1, t_z=-10)
        desenha_objeto(*slice_vertices_caixa1, texture_id=0)

        slice_vertices_caixa2 = obj_manager.get_vertices_slice(obj_index=1)
        model_objeto(*slice_vertices_caixa2, PROGRAM, t_x=1, t_z=-10)
        desenha_objeto(*slice_vertices_caixa2, texture_id=1)

        slice_vertices_casa = obj_manager.get_vertices_slice(obj_index=2)
        model_objeto(*slice_vertices_casa, PROGRAM, t_x=1, t_y=-2, t_z=-30, r_y=-90, s_x=2, s_y=2, s_z=2)
        desenha_objeto(*slice_vertices_casa, texture_id=2)

        slice_vertices_mesa_escritorio = obj_manager.get_vertices_slice(obj_index=3)
        model_objeto(*slice_vertices_mesa_escritorio, PROGRAM, t_x=-1.9, t_y=-1.5, t_z=-32, r_x=90, r_y=180, r_z=-90, s_x=0.01, s_y=0.01, s_z=0.01)
        desenha_objeto(*slice_vertices_mesa_escritorio, texture_id=3)

        slice_vertices_mesa = obj_manager.get_vertices_slice(obj_index=4)
        model_objeto(*slice_vertices_mesa, PROGRAM, t_y=-1.55, t_z=-28.58, r_y=45, s_x=0.55, s_y=0.55, s_z=0.55)
        desenha_objeto(*slice_vertices_mesa, texture_id=4)

        slice_vertices_cama = obj_manager.get_vertices_slice(obj_index=5)
        model_objeto(*slice_vertices_cama, PROGRAM, t_x=3.6, t_y=-1.56, t_z=-31.9, r_y=-90, s_x=0.007, s_y=0.007, s_z=0.007)
        desenha_objeto(*slice_vertices_cama, texture_id=5)
        
        slice_vertices_machado = obj_manager.get_vertices_slice(obj_index=6)
        model_objeto(*slice_vertices_machado, PROGRAM, t_y=-0.764, t_z=-28.75, r_y=-112)
        desenha_objeto(*slice_vertices_machado, texture_id=6)
        
        slice_vertices_papel = obj_manager.get_vertices_slice(obj_index=7)
        model_objeto(*slice_vertices_papel, PROGRAM, t_x=-2.02, t_y=-0.723, t_z=-31.965, r_y=85)
        desenha_objeto(*slice_vertices_papel, texture_id=7)

        print(f"t: ({tx}, {ty}, {tz}) r: ({rx}, {ry}, {rz}) s:  ({s})")

        # view
        cameraPos += cameraVel * deltaTime
        cameraVel = glm.vec3(0.0, 0.0, 0.0)

        mat_view = view(cameraPos, cameraFront, cameraUp)
        loc_view = glGetUniformLocation(PROGRAM, "view")
        glUniformMatrix4fv(loc_view, 1, GL_TRUE, mat_view)


        # projection
        mat_projection = projection(fov, LARGURA_JANELA, ALTURA_JANELA)
        loc_projection = glGetUniformLocation(PROGRAM, "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, mat_projection)

        glfw.swap_buffers(window)

    glfw.terminate()