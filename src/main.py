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
import glm
import math
from numpy import random
import os
path_join = os.path.join

# códigos externos
from shaders.shader_s import Shader
from aux.object_loader import ObjManager

def model_objeto(vertice_inicial, num_vertices, t_x=0, t_y=0, t_z=0, s_x=1, s_y=1, s_z=1, r_x=0, r_y=0, r_z=0):
    # aplica a matriz model
    mat_model = model(t_x, t_y, t_z,  # translação
                    s_x, s_y, s_z,  # escala
                    r_x, r_y, r_z)  # rotação
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)

def desenha_objeto(vertice_inicial, num_vertices, texture_id=-1):
    # textura
    if texture_id >= 0:
        glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # desenha o objeto
    glDrawArrays(GL_TRIANGLES, vertice_inicial, num_vertices) ## renderizando

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
    program = ourShader.getProgram()

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
    loc_vertices = glGetAttribLocation(program, "position")
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
    textures = np.zeros(len(all_texture_coord), [("position", np.float32, 2)]) # duas coordenadas
    textures['position'] = all_texture_coord

    glBindBuffer(GL_ARRAY_BUFFER, buffer_VBO[1])
    glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
    stride = textures.strides[0]
    offset = ctypes.c_void_p(0)
    loc_texture_coord = glGetAttribLocation(program, "texture_coord")
    glEnableVertexAttribArray(loc_texture_coord)
    glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)


    # camera
    cameraPos   = glm.vec3(0.0, 0.0, 0.0)
    cameraFront = glm.vec3(0.0, 0.0, -1.0)
    cameraUp    = glm.vec3(0.0, 1.0, 0.0)

    firstMouse = True
    yaw   = -90.0	# yaw is initialized to -90.0 degrees since a yaw of 0.0 results in a direction vector pointing to the right so we initially rotate a bit to the left.
    pitch =  0.0
    lastX =  LARGURA_JANELA / 2.0
    lastY =  ALTURA_JANELA / 2.0
    fov   =  45.0

    # timing
    deltaTime = 0.0	# time between current frame and last frame
    lastFrame = 0.0

    # eventos de teclado
    def key_event(window,key,scancode,action,mods):
        global cameraPos, cameraFront, cameraUp

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


    def framebuffer_size_callback(window, largura, altura):
        # make sure the viewport matches the new window dimensions note that width and
        # height will be significantly larger than specified on retina displays.
        glViewport(0, 0, largura, altura)

    # glfw: whenever the mouse moves, this callback is called
    # -------------------------------------------------------
    def mouse_callback(window, xpos, ypos):
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

    # glfw: whenever the mouse scroll wheel scrolls, this callback is called
    # ----------------------------------------------------------------------
    def scroll_callback(window, xoffset, yoffset):
        global fov

        fov -= yoffset
        if (fov < 1.0):
            fov = 1.0
        if (fov > 45.0):
            fov = 45.0

    glfw.set_key_callback(window,key_event)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # tell GLFW to capture our mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    ### Matrizes Model, View e Projection

    def view():
        global cameraPos, cameraFront, cameraUp
        mat_view = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
        mat_view = np.array(mat_view)
        return mat_view

    def projection(width, height):
        # perspective parameters: fovy, aspect, near, far
        mat_projection = glm.perspective(glm.radians(fov), width/height, 0.1, 100.0)

        mat_projection = np.array(mat_projection)
        return mat_projection

    """### Nesse momento, nós exibimos a janela!

    """

    glfw.show_window(window)

    """### Loop principal da janela."""

    glEnable(GL_DEPTH_TEST) ### importante para 3D

    while not glfw.window_should_close(window):

        currentFrame = glfw.get_time()
        deltaTime = currentFrame - lastFrame
        lastFrame = currentFrame

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glClearColor(1.0, 1.0, 1.0, 1.0)

        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)

        # desenho
        slice_vertices_caixa = obj_manager.get_vertices_slice(0)
        model_objeto(*slice_vertices_caixa, t_z=-10)
        desenha_objeto(*slice_vertices_caixa, 0)

        mat_view = view()
        loc_view = glGetUniformLocation(program, "view")
        glUniformMatrix4fv(loc_view, 1, GL_TRUE, mat_view)

        mat_projection = projection(LARGURA_JANELA, ALTURA_JANELA)
        loc_projection = glGetUniformLocation(program, "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, mat_projection)

        glfw.swap_buffers(window)

    glfw.terminate()