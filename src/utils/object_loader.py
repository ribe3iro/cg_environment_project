# funções associadas ao carregamento de objetos, vértices e texturas
from OpenGL.GL import *
from PIL import Image

def read_obj_from_file(filename):
    """Reads a Wavefront OBJ file. """
    obj = {
        'vertices': [],
        'texture_coords': [],
        'faces': []
    }

    material = None

    # abre o arquivo obj para leitura
    for line in open(filename, "r"): ## para cada linha do arquivo .obj
        if line.startswith('#'): continue ## ignora comentarios
        values = line.split() # quebra a linha por espaço
        if not values: continue

        ### recuperando vertices
        if values[0] == 'v':
            obj['vertices'].append(values[1:4])

        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            obj['texture_coords'].append(values[1:3])

        ### recuperando faces
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'f':
            face = []
            face_texture = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    face_texture.append(int(w[1]))
                else:
                    face_texture.append(0)

            obj['faces'].append((face, face_texture, material))

    return obj

# --------------------------------------------------------

def load_texture_from_file(texture_id, texture_img):
    print(texture_id, texture_img)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    img = Image.open(texture_img)
    img_width = img.size[0]
    img_height = img.size[1]
    image_data = img.tobytes("raw", "RGB", 0, -1)
    #image_data = np.array(list(img.getdata()), np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

# --------------------------------------------------------

def circular_sliding_window_of_three(arr):
    # Créditos: Hélio Nogueira Cardoso e Danielle Modesti (SCC0650 - 2024/2).
    if len(arr) == 3:
        return arr
    circular_arr = arr + [arr[0]]
    result = []
    for i in range(len(circular_arr) - 2):
        result.extend(circular_arr[i:i+3])
    return result

# --------------------------------------------------------

class ObjManager:
    def __init__(self):
        self.vertices = []
        self.textures_coord_list = []
        self.num_textures = 0

    # --------------------------------------------------------

    def load_obj(self, objFile):
        modelo = read_obj_from_file(objFile)

        faces_visited = []
        vertices_list = []
        textures_coord_list = []
        for face in modelo['faces']:
            if face[2] not in faces_visited:
                faces_visited.append(face[2])
            for vertice_id in circular_sliding_window_of_three(face[0]):
                vertices_list.append(modelo['vertices'][vertice_id - 1])
            for texture_id in circular_sliding_window_of_three(face[1]):
                textures_coord_list.append(modelo['texture_coords'][texture_id - 1])

        self.vertices.append(vertices_list)
        self.textures_coord_list += textures_coord_list

    # --------------------------------------------------------

    def load_textures(self, textures_list):
        for i in range(len(textures_list)):
            load_texture_from_file(self.num_textures, textures_list[i])
            self.num_textures += 1

    # --------------------------------------------------------

    def get_all_vertices(self):
        all_vertices = []
        for vertices_list in self.vertices:
            all_vertices += vertices_list
        return all_vertices

    # --------------------------------------------------------

    def get_vertices_slice(self, obj_index):
        acum_len = 0
        for i in range(obj_index):
            acum_len += len(self.vertices[i])
        
        initial_vertex_index = acum_len
        vertices_len = len(self.vertices[obj_index])

        return initial_vertex_index, vertices_len

# --------------------------------------------------------
