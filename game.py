import base64
import json
import random
from datetime import datetime

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


app = Ursina()

try:
    # user_save = json.load(open('saves/states.json'))
    with open('saves/states.txt', 'r', encoding='utf8') as f:
        texto = f.read()
        user_save_json = base64.b64decode(texto).decode()
        user_save = json.loads(user_save_json)

except FileNotFoundError:
    user_save = {
            "llave_cogida": False,
            "puerta_abierta": False,
            "player_position": [0, 100, 0]
    }


sky = Sky()

player = FirstPersonController()

texto_ayuda = Text(text="W A S D para moverse y Espacio para saltar", color=color.black, scale=(1, 1), origin=(0, -19))

cubo_inicio = Entity(position=Vec3(0, 0, 0),
                     model='cube',
                     scale=Vec3(1, 1, 1),
                     color=color.green,
                     collider='box')

cubo_fin = Entity(position=Vec3(0, 0, -1),
                  model='cube',
                  scale=Vec3(1, 1, 1),
                  color=color.red,
                  collider='box')


def crear_cubo(posicion, p_color=color.light_gray):
    Entity(position=posicion,
           model='cube',
           scale=Vec3(1, 1, 1),
           color=p_color,
           texture='brick',
           collider='box')


class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(parent=scene,
            position=position,
            model='cube',
            origin_y=.5,
            texture='white_cube',
            color=color.color(0, 0, random.uniform(.9, 1.0)),
            highlight_color=color.lime,
        )

pos = user_save["player_position"]
player.position = Vec3(pos[0], pos[1] + 2, pos[2])

# for i in range(1, 10):
#     x = random.randint(0, 4)
#     crear_cubo(Vec3(x, 0, i))


with open('niveles/nivel0.txt', 'r', encoding='utf8') as f:
    texto = f.read()

    lineas = texto.split('\n')
    linea_actual = 0
    for linea in lineas:
        columna_actual = 0
        for codigo in linea:
            if codigo == '0':
                pass
            if codigo == '1':
                crear_cubo(Vec3(columna_actual, 0, linea_actual))
            if codigo == '2':
                crear_cubo(Vec3(columna_actual, 1, linea_actual), color.blue)
                crear_cubo(Vec3(columna_actual, 2, linea_actual), color.blue)
            if codigo == '3':
                crear_cubo(Vec3(columna_actual, 0, linea_actual))
                llave = Voxel(position=(columna_actual, 2, linea_actual))
                llave.color = color.yellow
                if user_save["llave_cogida"]:
                    llave.cogida = True
                    llave.visible = False
                    llave.collision = None
                else:
                    llave.cogida = True
            if codigo == '4':
                crear_cubo(Vec3(columna_actual, 0, linea_actual))
                puerta = Voxel(position=(columna_actual, 2, linea_actual))
                puerta.color = color.brown
                puerta.abierta = False

                if user_save["puerta_abierta"]:
                    puerta.abierta = True
                    puerta.visible = False
                    puerta.collision = None
                else:
                    puerta.abierta = False

            columna_actual = columna_actual + 1

        linea_actual = linea_actual + 1

print(texto)


tiempo_inicio = datetime.now()


def update():
    tiempo_ahora = datetime.now()

    if (tiempo_ahora - tiempo_inicio).total_seconds() > 3:
        texto_ayuda.disable()

    if player.position.y <= -10:
        player.position = Vec3(0, 100, 0)

    ray = raycast(player.position, player.down, distance=2, ignore=[player])  # noqa

    if ray.entity == cubo_fin:
        player.disable()

        texto = Text(text="llegaste al final", color=color.black, scale=(4, 4), origin=(0, -1))
        boton = Button(text="Salir", color=color.black, scale=(0.2, 0.1), origin=(0, 1))
        boton.on_click = application.quit


def input(key):  # noqa
    if key == 'escape':
        quit()

    if key == 'p':
        data = {
            "llave_cogida": llave.cogida,
            "puerta_abierta": puerta.abierta,
            "player_position": [player.position.x, player.position.y, player.position.z]
        }
        str_data = json.dumps(data)
        b = base64.b64encode(bytes(str_data, 'utf-8'))
        base64_str = b.decode('utf-8')

        with open('saves/states.txt', 'w') as f:
            f.write(base64_str)

    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.entity == llave:
            destroy(llave)
            llave.cogida = True
            print("llave cogida")

        if hit_info.entity == puerta:
            if llave.cogida:
                destroy(puerta)
                puerta.abierta = True
                print("puerta abierta")
            else:
                texto_llave = Text(text="coge la llave", color=color.black, scale=(4, 4), origin=(0, -1))


app.run()
