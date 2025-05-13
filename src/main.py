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

def desenha_objeto(vertice_inicial, num_vertices, texture_id=-1, cube_map=False):
    # textura
    if texture_id < 0:
        return
    
    if cube_map:
        # glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)
    else:
        glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # desenha o objeto
    glDrawArrays(GL_TRIANGLES, vertice_inicial, num_vertices) ## renderizando

# --------------------------------------------------------

def camera_movement_handler():
    global window, cameraFront, cameraUp 
    global cameraVel, CAMERA_SPEED_WALKING, CAMERA_SPEED_RUNNING, flying_state
    global haunter_t, deltaTime

    OBJ_MOVE_SPEED = 1
    camera_speed = CAMERA_SPEED_WALKING

    if flying_state:
        frontDir = cameraFront
    else:
        frontDir = glm.vec3(cameraFront.x, 0.0, cameraFront.z)

    # W - mover câmera (frente)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cameraVel += glm.normalize(frontDir)
    # S - mover câmera (trás)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cameraVel -= glm.normalize(frontDir)
    # A - mover câmera (esquerda)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        cameraVel -= glm.normalize(glm.cross(frontDir, cameraUp))
    # D - mover câmera (direita)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        cameraVel += glm.normalize(glm.cross(frontDir, cameraUp))
    # SHIFT - correr
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        camera_speed = CAMERA_SPEED_RUNNING

    if glm.length(cameraVel) > 0:
        cameraVel = glm.normalize(cameraVel) * camera_speed

    ###################################    
    if glfw.get_key(window, glfw.KEY_G) == glfw.PRESS:
        haunter_t += OBJ_MOVE_SPEED * deltaTime
          
    if glfw.get_key(window, glfw.KEY_H) == glfw.PRESS:
        haunter_t -= OBJ_MOVE_SPEED * deltaTime
        
    

# funções callback
def key_event(window,key,scancode,action,mods):
    global cameraPos
    global papelPos, papelEscala, pegandoPapel, papelVisivel
    global machadoRotacao
    global show_lines, flying_state, mostrar_corpo
    # ESC - fechar janela
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    
    # ESPAÇO - mostrar corpo do fantasma
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        mostrar_corpo = not mostrar_corpo

    # P - toggle malha poligonal
    if key == glfw.KEY_P and action == glfw.PRESS:
        show_lines = not show_lines
        if show_lines:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # F - toggle voar
    if key == glfw.KEY_F and action == glfw.PRESS:
        flying_state = not flying_state
        if not flying_state:
            cameraPos.y = CAMERA_HEIGHT

    # E - pegar nota
    if key == glfw.KEY_E and action == glfw.PRESS:
        distToNote = glm.distance(cameraPos, papelPos)
        if distToNote < 2:
            pegandoPapel = True
            papelVisivel = not papelVisivel

    # C - toggle rotação machado (anti-horário)
    if key == glfw.KEY_C and action == glfw.PRESS:
        if machadoRotacao < 0:
            machadoRotacao = 0
        else:
            machadoRotacao = 1
    
    # V - toggle rotação machado (horário)
    if key == glfw.KEY_V and action == glfw.PRESS:
        if machadoRotacao > 0:
            machadoRotacao = 0
        else:
            machadoRotacao = -1

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
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    ### SHADERS
    shaders_path = path_join(ABSOLUTE_ROOT_PATH, 'src', 'shaders')

    DEFAULT_SHADER = Shader(
        path_join(shaders_path, 'default.vs'),
        path_join(shaders_path, 'default.fs')
    )
    DEFAULT_SHADER.use()

    SKYBOX_SHADER = Shader(
        path_join(shaders_path, 'skybox.vs'),
        path_join(shaders_path, 'skybox.fs')
    )
    SKYBOX_SHADER.use()
    glUniform1i(glGetUniformLocation(SKYBOX_SHADER.getProgram(), "skybox"), 0)

    ### CARREGANDO OBJETOS

    ## SKYBOX

    # vértices
    skyboxVertices = [
        [-1.0, -1.0,  1.0],
        [1.0, -1.0,  1.0],
        [1.0, -1.0, -1.0],
        [-1.0, -1.0, -1.0],
        [-1.0,  1.0,  1.0],
        [1.0,  1.0,  1.0],
        [1.0,  1.0, -1.0],
        [-1.0,  1.0, -1.0]
    ]

    skyboxIndices = [
        1, 2, 6,
        6, 5, 1,
        0, 4, 7,
        7, 3, 0,
        4, 5, 6,
        6, 7, 4,
        0, 3, 2,
        2, 1, 0,
        0, 1, 5,
        5, 4, 0,
        3, 7, 6,
        6, 2, 3
    ]

    vertices = []
    for i in skyboxIndices:
        vertices.append(skyboxVertices[i])
    allSkyboxVertices = np.zeros(len(vertices), [("position", np.float32, 3)])
    allSkyboxVertices['position'] = vertices

    skyboxVAO = glGenVertexArrays(1)
    skyboxVBO = glGenBuffers(1)

    glBindVertexArray(skyboxVAO)

    glBindBuffer(GL_ARRAY_BUFFER, skyboxVBO)
    glBufferData(GL_ARRAY_BUFFER, allSkyboxVertices.nbytes, allSkyboxVertices, GL_STATIC_DRAW)

    stride = allSkyboxVertices.strides[0]
    offset = ctypes.c_void_p(0)
    loc_vertices = glGetAttribLocation(SKYBOX_SHADER.getProgram(), "aPos")
    glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)
    glEnableVertexAttribArray(loc_vertices)

    # texturas
    skybox_root_path = path_join(ABSOLUTE_ROOT_PATH, 'texturas', 'skybox')
    skybox_textures_list = []
    skybox_textures_list.append(path_join(skybox_root_path, 'right.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'left.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'top.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'bottom.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'front.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'back.png'))

    obj_manager = ObjManager()
    skyboxTexture = obj_manager.load_texture(skybox_textures_list, cube_map=True)

    ## DEMAIS OBJETOS
    DEFAULT_SHADER.use()

    objects_path = path_join(ABSOLUTE_ROOT_PATH, 'objetos')
    
    obj_manager.load_obj(path_join(objects_path, 'chao.obj'))
    obj_manager.load_obj(path_join(objects_path, 'caixa.obj'))
    obj_manager.load_obj(path_join(objects_path, 'casa.obj'))
    obj_manager.load_obj(path_join(objects_path, 'mesa_escritorio.obj'))
    obj_manager.load_obj(path_join(objects_path, 'mesa.obj'))
    obj_manager.load_obj(path_join(objects_path, 'cama.obj'))
    obj_manager.load_obj(path_join(objects_path, 'machado.obj'))
    obj_manager.load_obj(path_join(objects_path, 'papel.obj'))
    obj_manager.load_obj(path_join(objects_path, 'tronco.obj'))
    obj_manager.load_obj(path_join(objects_path, 'fantasma.obj'))
    obj_manager.load_obj(path_join(objects_path, 'fake.obj'))
    obj_manager.load_obj(path_join(objects_path, 'olhos.obj'))
    obj_manager.load_obj(path_join(objects_path, 'haunter.obj'))
    obj_manager.load_obj(path_join(objects_path, 'muro.obj'))
    obj_manager.load_obj(path_join(objects_path, 'lapide.obj'))

    # carregando na GPU
    objectsVAO = glGenVertexArrays(1)
    objectsVBO = glGenBuffers(1)

    glBindVertexArray(objectsVAO)

    all_vertices = obj_manager.get_all_vertices()
    vertices = np.zeros(len(all_vertices), [("position", np.float32, 3)])
    vertices['position'] = all_vertices
    glBindBuffer(GL_ARRAY_BUFFER, objectsVBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)
    loc_vertices = glGetAttribLocation(DEFAULT_SHADER.getProgram(), "position")
    glEnableVertexAttribArray(loc_vertices)
    glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

    ## texturas
    textures_path = path_join(ABSOLUTE_ROOT_PATH, 'texturas')

    obj_manager.load_texture(path_join(textures_path, 'terra.png'))
    obj_manager.load_texture(path_join(textures_path, 'tijolos.jpg'))
    obj_manager.load_texture(path_join(textures_path, 'casa.png'))
    obj_manager.load_texture(path_join(textures_path, 'mesa_escritorio.jpg'))
    obj_manager.load_texture(path_join(textures_path, 'mesa.png'))
    obj_manager.load_texture(path_join(textures_path, 'cama.png'))
    obj_manager.load_texture(path_join(textures_path, 'machado.jpg'))
    obj_manager.load_texture(path_join(textures_path, 'papel.png'))
    obj_manager.load_texture(path_join(textures_path, 'tronco.jpg'))
    obj_manager.load_texture(path_join(textures_path, 'fantasma.png'))
    obj_manager.load_texture(path_join(textures_path, 'fake_1.png'))
    obj_manager.load_texture(path_join(textures_path, 'fake_2.png'))
    obj_manager.load_texture(path_join(textures_path, 'olhos.png'))
    obj_manager.load_texture(path_join(textures_path, 'haunter.png'))
    obj_manager.load_texture(path_join(textures_path, 'muro.jpg'))
    obj_manager.load_texture(path_join(textures_path, 'lapide.jpeg'))

    # carregando na GPU
    all_texture_coord = obj_manager.textures_coord_list
    textures = np.zeros(len(all_texture_coord), [("position", np.float32, 2)])
    textures['position'] = all_texture_coord

    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
    stride = textures.strides[0]
    offset = ctypes.c_void_p(0)
    loc_texture_coord = glGetAttribLocation(DEFAULT_SHADER.getProgram(), "texture_coord")
    glEnableVertexAttribArray(loc_texture_coord)
    glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

    # variáveis para a movimentação da câmera
    CAMERA_HEIGHT = -0.4
    cameraPos   = glm.vec3(0.0, CAMERA_HEIGHT, 0.0)
    cameraFront = glm.vec3(0.0, 0.0, -1.0)
    cameraUp    = glm.vec3(0.0, 1.0, 0.0)
    cameraVel   = glm.vec3(0.0, 0.0, 0.0)
    CAMERA_SPEED_WALKING = 5
    CAMERA_SPEED_RUNNING = 10
    deltaTime   = 0.0
    lastFrame   = 0.0
    X_LIMIT = (-35, 35)
    Y_LIMIT = (-1.5, 10)
    Z_LIMIT = (-40, 10)


    # variáveis auxiliares
    papelPos = glm.vec3(-2.02, -0.723, -31.965)
    papelEscala = 1
    pegandoPapel = False
    papelVisivel = True
    machadoRotacao = 0
    machadoAngulo = -112
    haunter_t = 0.0
    mostrar_corpo = False

    # variáveis para os callbacks
    show_lines = False
    flying_state = False

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

        ## SKYBOX
        SKYBOX_SHADER.use()

        glDepthFunc(GL_LEQUAL)

        glBindVertexArray(skyboxVAO)
        glBindBuffer(GL_ARRAY_BUFFER, skyboxVBO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, skyboxTexture)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        glDepthFunc(GL_LESS)


        ## TRANSFORMAÇÕES

        # model
        DEFAULT_SHADER.use()
        glBindVertexArray(objectsVAO)
        glBindBuffer(GL_ARRAY_BUFFER, objectsVBO)
        slice_vertices_chao = obj_manager.get_vertices_slice(obj_index=0)
        model_objeto(*slice_vertices_chao, DEFAULT_SHADER.getProgram(), t_z=-15, t_y=-1.6, s_x=35, s_z=25)
        desenha_objeto(*slice_vertices_chao, texture_id=2)

        # slice_vertices_caixa2 = obj_manager.get_vertices_slice(obj_index=1)
        # model_objeto(*slice_vertices_caixa2, DEFAULT_SHADER.getProgram(), t_x=1, t_z=-10)
        # desenha_objeto(*slice_vertices_caixa2, texture_id=3)

        slice_vertices_casa = obj_manager.get_vertices_slice(obj_index=2)
        model_objeto(*slice_vertices_casa, DEFAULT_SHADER.getProgram(), t_x=1, t_y=-2, t_z=-30, r_y=-90, s_x=2, s_y=2, s_z=2)
        desenha_objeto(*slice_vertices_casa, texture_id=4)

        slice_vertices_mesa_escritorio = obj_manager.get_vertices_slice(obj_index=3)
        model_objeto(*slice_vertices_mesa_escritorio, DEFAULT_SHADER.getProgram(), t_x=-1.9, t_y=-1.5, t_z=-32, r_x=90, r_y=180, r_z=-90, s_x=0.01, s_y=0.01, s_z=0.01)
        desenha_objeto(*slice_vertices_mesa_escritorio, texture_id=5)

        slice_vertices_mesa = obj_manager.get_vertices_slice(obj_index=4)
        model_objeto(*slice_vertices_mesa, DEFAULT_SHADER.getProgram(), t_y=-1.55, t_z=-28.58, r_y=45, s_x=0.55, s_y=0.55, s_z=0.55)
        desenha_objeto(*slice_vertices_mesa, texture_id=6)

        slice_vertices_cama = obj_manager.get_vertices_slice(obj_index=5)
        model_objeto(*slice_vertices_cama, DEFAULT_SHADER.getProgram(), t_x=3.6, t_y=-1.56, t_z=-31.9, r_y=-90, s_x=0.007, s_y=0.007, s_z=0.007)
        desenha_objeto(*slice_vertices_cama, texture_id=7)
        
        machadoAngulo += (machadoRotacao * deltaTime * 480)
        slice_vertices_machado = obj_manager.get_vertices_slice(obj_index=6)
        model_objeto(*slice_vertices_machado, DEFAULT_SHADER.getProgram(), t_y=-0.764, t_z=-28.75, r_y=machadoAngulo)
        desenha_objeto(*slice_vertices_machado, texture_id=8)
        
        if pegandoPapel:
            if not papelVisivel:
                papelEscala *= (1 - (8 * deltaTime))  # 1/8 de segundo de animação
                if papelEscala < 0.01:
                    papelEscala = 0
                    pegandoPapel = False
            else:
                if papelEscala == 0:
                    papelEscala = 0.0001
                papelEscala /= (1 - (8 * deltaTime))  # 1/8 de segundo de animação
                if papelEscala > 1:
                    papelEscala = 1
                    pegandoPapel = False
        slice_vertices_papel = obj_manager.get_vertices_slice(obj_index=7)
        model_objeto(*slice_vertices_papel, DEFAULT_SHADER.getProgram(), 
            t_x=papelPos.x, t_y=papelPos.y, t_z=papelPos.z, 
            s_x=papelEscala, s_y=papelEscala, s_z=papelEscala, 
            r_y=85)
        desenha_objeto(*slice_vertices_papel, texture_id=9)
        
        slice_vertices_tronco1 = obj_manager.get_vertices_slice(obj_index=8)
        model_objeto(*slice_vertices_tronco1, DEFAULT_SHADER.getProgram(), t_x=-5, t_y=-2.3)
        desenha_objeto(*slice_vertices_tronco1, texture_id=10)
        slice_vertices_tronco2 = obj_manager.get_vertices_slice(obj_index=8)
        model_objeto(*slice_vertices_tronco2, DEFAULT_SHADER.getProgram(), t_x=-25, t_y=-2.3, t_z=-20)
        desenha_objeto(*slice_vertices_tronco2, texture_id=10)
        slice_vertices_tronco3 = obj_manager.get_vertices_slice(obj_index=8)
        model_objeto(*slice_vertices_tronco3, DEFAULT_SHADER.getProgram(), t_x=25, t_y=-2.3, t_z=-15)
        desenha_objeto(*slice_vertices_tronco3, texture_id=10)
        slice_vertices_tronco4 = obj_manager.get_vertices_slice(obj_index=8)
        model_objeto(*slice_vertices_tronco4, DEFAULT_SHADER.getProgram(), t_x=15, t_y=-2.3, t_z=-35)
        desenha_objeto(*slice_vertices_tronco4, texture_id=10)

        fantasma_tz = -28.6

        fantasma_dx = cameraPos.x
        fantasma_dz = cameraPos.z - fantasma_tz
        fantasma_rot_y = math.degrees(math.atan2(fantasma_dx, fantasma_dz))
        slice_vertices_fantasma = obj_manager.get_vertices_slice(obj_index=9)
        model_objeto(*slice_vertices_fantasma, DEFAULT_SHADER.getProgram(), t_y=-1.29, t_z=fantasma_tz, r_y=fantasma_rot_y, s_x=0.5, s_y=0.5, s_z=0.5)
        desenha_objeto(*slice_vertices_fantasma, texture_id=11)

        n_fake_arvores = 7
        raio = 50
        fake_cx, fake_cz = 0, -15  # centro do círculo
        for i in range(n_fake_arvores):
            angulo = 2 * math.pi * i / n_fake_arvores  # divide a circunferência em partes iguais

            fake_tx = fake_cx + raio * math.cos(angulo)  # coordenada X
            fake_tz = fake_cz + raio * math.sin(angulo)  # coordenada Z
            
            dx = cameraPos.x - fake_tx
            dz = cameraPos.z - fake_tz

            # ângulo para olhar para o centro (em radianos)
            rot_y = math.degrees(math.atan2(dx, dz))

            slice_vertices_fake = obj_manager.get_vertices_slice(obj_index=10)
            model_objeto(*slice_vertices_fake, DEFAULT_SHADER.getProgram(), t_x=fake_tx, t_y=-2, t_z=fake_tz, r_y=rot_y, s_x=8, s_y=8, s_z=8)
            desenha_objeto(*slice_vertices_fake, texture_id=12+(i%2))

        escala = 15.0

        haunter_x = escala * math.cos(haunter_t)
        haunter_z = escala * math.sin(haunter_t * 0.7 + math.cos(haunter_t * 0.5))

        haunter_dx = cameraPos.x - haunter_x
        haunter_dz = cameraPos.z - haunter_z
        haunter_rot_y = math.degrees(math.atan2(haunter_dx, haunter_dz))
        
        slice_vertices_olhos = obj_manager.get_vertices_slice(obj_index=11)
        model_objeto(*slice_vertices_olhos, DEFAULT_SHADER.getProgram(),t_x=haunter_x, t_z=haunter_z-10, r_y=haunter_rot_y)
        desenha_objeto(*slice_vertices_olhos, texture_id=14)
        
        if mostrar_corpo:
            slice_vertices_haunter = obj_manager.get_vertices_slice(obj_index=12)
            model_objeto(*slice_vertices_haunter, DEFAULT_SHADER.getProgram(),t_x=haunter_x, t_z=haunter_z-10, r_y=haunter_rot_y)
            desenha_objeto(*slice_vertices_haunter, texture_id=15)

        tamanho_muro = 4

        for j in Z_LIMIT:
            for i in range(X_LIMIT[0], X_LIMIT[1], tamanho_muro):
                slice_vertices_muro= obj_manager.get_vertices_slice(obj_index=13)
                model_objeto(*slice_vertices_muro, DEFAULT_SHADER.getProgram(),t_x=i, t_y=0.4, t_z=j)
                desenha_objeto(*slice_vertices_muro, texture_id=16)
        
        for j in X_LIMIT:
            for i in range(Z_LIMIT[0], Z_LIMIT[1]+ tamanho_muro, tamanho_muro):
                slice_vertices_muro= obj_manager.get_vertices_slice(obj_index=13)
                model_objeto(*slice_vertices_muro, DEFAULT_SHADER.getProgram(),t_x=j, t_y=0.4, t_z=i, r_y=90)
                desenha_objeto(*slice_vertices_muro, texture_id=16)

        slice_vertices_muro= obj_manager.get_vertices_slice(obj_index=14)
        model_objeto(*slice_vertices_muro, DEFAULT_SHADER.getProgram(),t_x=5, t_y=-1.6,t_z=-32.4,r_y=90, s_x=0.01, s_y=0.01, s_z=0.01)
        desenha_objeto(*slice_vertices_muro, texture_id=17)

        # view
        cameraPos += cameraVel * deltaTime
        cameraVel = glm.vec3(0.0, 0.0, 0.0)

        # verificando limites da cena
        if cameraPos.x < X_LIMIT[0] + 0.5:
            cameraPos.x = X_LIMIT[0] + 0.5
        elif cameraPos.x > X_LIMIT[1] - 0.5:
            cameraPos.x = X_LIMIT[1] - 0.5
        
        if cameraPos.y < Y_LIMIT[0]:
            cameraPos.y = Y_LIMIT[0]
        elif cameraPos.y > Y_LIMIT[1]:
            cameraPos.y = Y_LIMIT[1]
        
        if cameraPos.z < Z_LIMIT[0] + 0.5:
            cameraPos.z = Z_LIMIT[0] + 0.5
        elif cameraPos.z > Z_LIMIT[1] - 0.5:
            cameraPos.z = Z_LIMIT[1] - 0.5

        mat_view = view(cameraPos, cameraFront, cameraUp)
        loc_view = glGetUniformLocation(DEFAULT_SHADER.getProgram(), "view")
        glUniformMatrix4fv(loc_view, 1, GL_TRUE, np.array(mat_view))


        # projection
        mat_projection = projection(fov, LARGURA_JANELA, ALTURA_JANELA)
        loc_projection = glGetUniformLocation(DEFAULT_SHADER.getProgram(), "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, np.array(mat_projection))

        # SKYBOX (view e projection)
        SKYBOX_SHADER.use()

        # view
        loc_projection = glGetUniformLocation(SKYBOX_SHADER.getProgram(), "view")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, np.array(glm.mat4(glm.mat3(mat_view))))

        # projection
        loc_projection = glGetUniformLocation(SKYBOX_SHADER.getProgram(), "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, np.array(mat_projection))

        glfw.swap_buffers(window)

    glfw.terminate()