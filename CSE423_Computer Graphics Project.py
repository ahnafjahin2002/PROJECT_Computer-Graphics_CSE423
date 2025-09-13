from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
GRID_LENGTH = 16000
TRACK_LENGTH = 30000
TRACK_WIDTH = 600

game_state = "racing"
race_start_time = 0
just_crossed_finish = False
current_lap = 1
total_laps = 3
lap_start_time = 0
lap_times = []
score_points = 0
last_player_z = -TRACK_LENGTH/2 + 100

reward_message = {'text': '', 'timer': 0}

headlights_on = False

time_of_day = 0.25
sky_color = [0.0, 0.0, 0.0]
light_color = [0.0, 0.0, 0.0]
current_weather = "clear"
particles = []
weather_change_timer = 0
WEATHER_DURATION = 1500

player_pos = [0, 5, -TRACK_LENGTH/2 + 100]
player_angle = 0.0
player_speed = 0.0
player_health = 100.0
wheel_rotation_angle = 0.0

player_coins = 0
coins = []
police_chase_active = False
police_car = {}
crossing_pedestrian = {}
pedestrian_cross_timer = 500

damage_effect_timer = 0
shield_active = False
shield_timer = 0

key_states = {'w': False, 's': False, 'a': False, 'd': False, 'n': False}

boost_active = False
boost_timer = 0
boost_cooldown = 0
cheat_mode = False

camera_mode = "third_person"
camera_angle_y = 0.0
camera_angle_h = 0.0
camera_distance = 200

opponents = [
    {'pos': [-200, 5, -TRACK_LENGTH/2 + 50], 'angle': 0.0, 'speed': 10.1, 'target_pos': (-200, TRACK_LENGTH/2)},
    {'pos': [200, 5, -TRACK_LENGTH/2 + 50], 'angle': 0.0, 'speed': 10.3, 'target_pos': (200, TRACK_LENGTH/2)}
]
oncoming_cars = []
oncoming_spawn_timer = 300

obstacles = [
    {'pos': (100, 10, -11000), 'size': (40, 40, 40), 'type': 'cube'},
    {'pos': (-120, 0, -5500), 'size': (20, 50), 'type': 'cone'},
    {'pos': (250, 10, -9000), 'size': (60, 60, 60), 'type': 'cube'},
    {'pos': (-280, 0, 4000), 'size': (30, 60), 'type': 'cone'},
    {'pos': (0, 10, 12500), 'size': (200, 20, 20), 'type': 'barrier'}
]
moving_obstacle = {'pos': [0, 10, 6500], 'size': (80, 20, 10), 'start_x': -TRACK_WIDTH/2 + 40, 'end_x': TRACK_WIDTH/2 - 40, 'dir': 1, 'type': 'moving'}
swinging_gate = {'pos': [0, 20, 10000], 'size': (120, 40, 10), 'angle': 0, 'max_angle': 75, 'dir': 1, 'speed': 0.5, 'type': 'swinging'}
moving_cone_group = {
    'pos': [0, 0, -2500], 'start_x': -200, 'end_x': 200, 'dir': 1,
    'cones': [(-40, 0), (0, 0), (40, 0)],
    'type': 'cone_group'
}
hazards = [
    {'pos': (10, 0.1, -8000), 'radius': 80, 'type': 'oil'},
    {'pos': (150, 0.1, 2000), 'radius': 60, 'type': 'oil'},
    {'pos': (-100, 0.1, 7500), 'radius': 70, 'type': 'slippery'}
]
powerups = [
    {'pos': (TRACK_WIDTH/4, 10, 3500), 'type': 'health', 'active': True},
    {'pos': (-TRACK_WIDTH/4, 10, -12500), 'type': 'shield', 'active': True},
]

def generate_coins():
    global coins
    coins = []
    num_coins = 100
    for i in range(num_coins):
        x = random.uniform(-TRACK_WIDTH/2 + 50, TRACK_WIDTH/2 - 50)
        z = random.uniform(-TRACK_LENGTH/2 + 500, TRACK_LENGTH/2 - 500)
        coins.append({'pos': [x, 15, z], 'active': True, 'angle': 0})

building_positions = []
PEDESTRIAN_COUNT = 100
pedestrians = []

def generate_city_layout():
    global building_positions
    building_positions = []
    for z_segment in range(int(-TRACK_LENGTH/2), int(TRACK_LENGTH/2), 400):
        for _ in range(2):
            x = random.uniform(-GRID_LENGTH/2, -TRACK_WIDTH/2 - 100)
            z = random.uniform(z_segment, z_segment + 400)
            height = random.uniform(150, 600); width = random.uniform(80, 200); depth = random.uniform(80, 200)
            color = [random.uniform(0.3, 0.7), random.uniform(0.3, 0.7), random.uniform(0.3, 0.7)]
            building_positions.append({'pos': (x, 0, z), 'size': (width, height, depth), 'color': color})
            x = random.uniform(TRACK_WIDTH/2 + 100, GRID_LENGTH/2)
            z = random.uniform(z_segment, z_segment + 400)
            height = random.uniform(150, 600); width = random.uniform(80, 200); depth = random.uniform(80, 200)
            color = [random.uniform(0.3, 0.7), random.uniform(0.3, 0.7), random.uniform(0.3, 0.7)]
            building_positions.append({'pos': (x, 0, z), 'size': (width, height, depth), 'color': color})

def generate_pedestrians():
    global pedestrians
    pedestrians = []
    for _ in range(PEDESTRIAN_COUNT):
        x = random.choice([-TRACK_WIDTH/2 - 30, TRACK_WIDTH/2 + 30])
        z = random.uniform(-TRACK_LENGTH/2, TRACK_LENGTH/2)
        pedestrians.append({'pos': [x, 15, z], 'dir': random.choice([-1, 1]), 'speed': random.uniform(0.5, 1.5)})

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1.0, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_ui():
    draw_text(10, WINDOW_HEIGHT - 30, f"Objective: Reach the Finish Line!")
    elapsed_time = (glutGet(GLUT_ELAPSED_TIME) - race_start_time) / 1000.0
    minutes = int(elapsed_time / 60)
    seconds = int(elapsed_time % 60)
    draw_text(10, WINDOW_HEIGHT - 60, f"Time: {minutes:02d}:{seconds:02d}")
    draw_text(10, WINDOW_HEIGHT - 90, f"Lap: {current_lap}/{total_laps}")
    draw_text(10, WINDOW_HEIGHT - 120, f"Score: {int(score_points)}")
    draw_text(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 30, f"Health: {int(player_health)}%")
    draw_text(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 60, f"Weather: {current_weather.capitalize()}")
    headlight_status = "ON" if headlights_on else "OFF"
    draw_text(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 90, f"Headlights (F): {headlight_status}")
    boost_status = "READY" if (not boost_active and boost_cooldown <= 0) else ("ACTIVE" if boost_active else f"CD {boost_cooldown//60}s")
    cheat_status = "ON" if cheat_mode else "OFF"
    draw_text(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 120, f"Boost (N): {boost_status}")
    draw_text(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 150, f"Cheat (C): {cheat_status}")
    draw_text(WINDOW_WIDTH/2 - 150, 20, "Press T to reset car position")
    draw_text(10, 10, f"Coins: {player_coins}")
    if shield_active:
        draw_text(WINDOW_WIDTH/2 - 50, 50, f"SHIELD ACTIVE!", GLUT_BITMAP_TIMES_ROMAN_24)

    if reward_message['timer'] > 0:
        draw_text(WINDOW_WIDTH/2 - 70, WINDOW_HEIGHT/2 + 50, reward_message['text'], GLUT_BITMAP_TIMES_ROMAN_24)
        
    if game_state != "racing":
        msg = "YOU WIN!"
        if game_state == "lost": msg = "GAME OVER"
        elif game_state == "busted": msg = "BUSTED!"
        draw_text(WINDOW_WIDTH/2 - 100, WINDOW_HEIGHT/2, msg, GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(WINDOW_WIDTH/2 - 120, WINDOW_HEIGHT/2 - 40, "Press 'R' to Restart", GLUT_BITMAP_HELVETICA_18)
    draw_speedometer()
    draw_minimap()

def draw_minimap():
    map_width = 180
    map_height = 140
    margin_x = 10
    margin_y = 170
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_QUADS)
    left_x = WINDOW_WIDTH - margin_x - map_width
    right_x = WINDOW_WIDTH - margin_x
    top_y = WINDOW_HEIGHT - margin_y
    bottom_y = WINDOW_HEIGHT - margin_y - map_height
    glVertex2f(left_x, bottom_y)
    glVertex2f(right_x, bottom_y)
    glVertex2f(right_x, top_y)
    glVertex2f(left_x, top_y)
    glEnd()
    inner_margin = 8
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(left_x + inner_margin, top_y - inner_margin)
    glVertex2f(right_x - inner_margin, top_y - inner_margin)
    glVertex2f(right_x - inner_margin, bottom_y + inner_margin)
    glVertex2f(left_x + inner_margin, bottom_y + inner_margin)
    glEnd()
    def world_to_map(px, pz):
        x_norm = (px + TRACK_WIDTH/2) / TRACK_WIDTH
        z_norm = (pz + TRACK_LENGTH/2) / TRACK_LENGTH
        x = left_x + inner_margin + x_norm * (map_width - 2*inner_margin)
        y = top_y - (inner_margin + z_norm * (map_height - 2*inner_margin))
        return x, y
    glPointSize(6)
    glBegin(GL_POINTS)
    glColor3f(0.1, 0.7, 1.0)
    mx, my = world_to_map(player_pos[0], player_pos[2])
    glVertex2f(mx, my)
    glEnd()
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(1.0, 0.3, 0.3)
    for car in opponents:
        mx, my = world_to_map(car['pos'][0], car['pos'][2])
        glVertex2f(mx, my)
    glEnd()
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def draw_speedometer():
    max_speed_for_ui = 15.0
    speed_fraction = min(abs(player_speed) / max_speed_for_ui, 1.0)
    needle_angle = 135 - (speed_fraction * 180)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glTranslatef(WINDOW_WIDTH - 100, 100, 0)
    glColor3f(0.8, 0.8, 0.8)
    glBegin(GL_LINE_STRIP)
    for angle in range(-135, 46, 5):
        rad = math.radians(angle)
        glVertex2f(80 * math.cos(rad), 80 * math.sin(rad))
    glEnd()
    glPushMatrix(); glRotatef(needle_angle, 0, 0, 1)
    glColor3f(1, 0, 0); glLineWidth(2)
    glBegin(GL_LINES); glVertex2f(0, 0); glVertex2f(75, 0); glEnd()
    glLineWidth(1); glPopMatrix(); glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_environment():
    global crossing_pedestrian
    glColor3f(sky_color[0], sky_color[1], sky_color[2])
    q = gluNewQuadric()
    glPushMatrix(); glCullFace(GL_FRONT)
    gluSphere(q, GRID_LENGTH * 1.5, 32, 32)
    glCullFace(GL_BACK); glPopMatrix()
    glDisable(GL_LIGHTING)
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH/2, 0, -GRID_LENGTH/2)
    glVertex3f(GRID_LENGTH/2, 0, -GRID_LENGTH/2)
    glVertex3f(GRID_LENGTH/2, 0, GRID_LENGTH/2)
    glVertex3f(-GRID_LENGTH/2, 0, GRID_LENGTH/2)
    glEnd()
    glEnable(GL_LIGHTING)
    for building in building_positions:
        glPushMatrix(); glTranslatef(building['pos'][0], building['pos'][1] + building['size'][1]/2, building['pos'][2])
        glColor3fv(building['color']); glScalef(building['size'][0], building['size'][1], building['size'][2])
        glutSolidCube(1); glPopMatrix()
    for p in pedestrians:
        glPushMatrix(); glTranslatef(p['pos'][0], p['pos'][1], p['pos'][2])
        glColor3f(0.8, 0.6, 0.4); glutSolidSphere(10, 8, 8)
        glPushMatrix(); glTranslatef(0, 15, 0); glutSolidSphere(7, 8, 8); glPopMatrix()
        glPopMatrix()
    if crossing_pedestrian.get('active'):
        p = crossing_pedestrian['pos']
        glPushMatrix(); glTranslatef(p[0], p[1], p[2])
        glColor3f(1.0, 0.2, 0.2); glutSolidSphere(10, 8, 8)
        glPushMatrix(); glTranslatef(0, 15, 0); glutSolidSphere(7, 8, 8); glPopMatrix()
        glPopMatrix()

def draw_hazards():
    for hazard in hazards:
        glPushMatrix(); glTranslatef(hazard['pos'][0], hazard['pos'][1], hazard['pos'][2])
        if hazard['type'] == 'oil': glColor4f(0.1, 0.1, 0.1, 0.7)
        elif hazard['type'] == 'slippery': glColor4f(0.8, 0.8, 1.0, 0.5)
        glBegin(GL_TRIANGLE_FAN); glVertex3f(0, 0, 0)
        for i in range(21):
            angle = i * (2 * math.pi / 20)
            glVertex3f(hazard['radius'] * math.cos(angle), 0, hazard['radius'] * math.sin(angle))
        glEnd(); glPopMatrix()

def draw_particles():
    glDisable(GL_LIGHTING); glPointSize(3.0)
    for p in particles:
        if p['type'] == 'rain':
            glColor3f(0.7, 0.8, 0.9); glLineWidth(1.0); glBegin(GL_LINES)
            glVertex3fv(p['pos'])
            glVertex3f(p['pos'][0], p['pos'][1] + 10.0, p['pos'][2]); glEnd()
        elif p['type'] == 'snow':
            glColor3f(0.9, 0.9, 1.0); glBegin(GL_POINTS)
            glVertex3fv(p['pos']); glEnd()
    glEnable(GL_LIGHTING)

def draw_track():
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_QUADS)
    glVertex3f(-TRACK_WIDTH/2, 0, -TRACK_LENGTH/2)
    glVertex3f(TRACK_WIDTH/2, 0, -TRACK_LENGTH/2)
    glVertex3f(TRACK_WIDTH/2, 0, TRACK_LENGTH/2)
    glVertex3f(-TRACK_WIDTH/2, 0, TRACK_LENGTH/2)
    glEnd()
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.0)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for z in range(int(-TRACK_LENGTH/2), int(TRACK_LENGTH/2), 100):
        glVertex3f(0, 0.2, z)
        glVertex3f(0, 0.2, z + 50)
    glVertex3f(-TRACK_WIDTH/2 + 10, 0.2, -TRACK_LENGTH/2)
    glVertex3f(-TRACK_WIDTH/2 + 10, 0.2, TRACK_LENGTH/2)
    glVertex3f(TRACK_WIDTH/2 - 10, 0.2, -TRACK_LENGTH/2)
    glVertex3f(TRACK_WIDTH/2 - 10, 0.2, TRACK_LENGTH/2)
    glEnd()
    glEnable(GL_LIGHTING)
    draw_bridge(TRACK_WIDTH, 0)
    draw_tunnel(TRACK_WIDTH, 7500)
    draw_bridge(TRACK_WIDTH, -7500, 50)
    draw_tunnel(TRACK_WIDTH, -12500)
    glColor3f(1, 1, 1); glLineWidth(5); glBegin(GL_LINES)
    glVertex3f(-TRACK_WIDTH/2, 0.1, TRACK_LENGTH/2 - 10)
    glVertex3f(TRACK_WIDTH/2, 0.1, TRACK_LENGTH/2 - 10); glEnd(); glLineWidth(1)

def draw_bridge(track_width, center_z, height=80):
    ramp_length = 400; deck_length = 600
    glColor3f(0.35, 0.35, 0.4)
    glBegin(GL_QUADS); glVertex3f(-track_width/2, 0, center_z - deck_length/2 - ramp_length); glVertex3f(track_width/2, 0, center_z - deck_length/2 - ramp_length); glVertex3f(track_width/2, height, center_z - deck_length/2); glVertex3f(-track_width/2, height, center_z - deck_length/2); glEnd()
    glBegin(GL_QUADS); glVertex3f(-track_width/2, height, center_z - deck_length/2); glVertex3f(track_width/2, height, center_z - deck_length/2); glVertex3f(track_width/2, height, center_z + deck_length/2); glVertex3f(-track_width/2, height, center_z + deck_length/2); glEnd()
    glBegin(GL_QUADS); glVertex3f(-track_width/2, height, center_z + deck_length/2); glVertex3f(track_width/2, height, center_z + deck_length/2); glVertex3f(track_width/2, 0, center_z + deck_length/2 + ramp_length); glVertex3f(-track_width/2, 0, center_z + deck_length/2 + ramp_length); glEnd()
    q = gluNewQuadric(); glColor3f(0.5,0.5,0.5)
    for x in [-track_width/2 + 20, track_width/2 - 20]:
        for z_offset in [-200, 0, 200]:
            glPushMatrix(); glTranslatef(x, 0, center_z + z_offset); glRotatef(-90, 1, 0, 0)
            gluCylinder(q, 15, 15, height, 16, 16); glPopMatrix()

def draw_tunnel(track_width, center_z):
    tunnel_length = 1000; tunnel_height = 100
    glColor3f(0.2, 0.2, 0.25)
    glBegin(GL_QUADS); glVertex3f(-track_width/2, 0, center_z - tunnel_length/2); glVertex3f(-track_width/2, tunnel_height, center_z - tunnel_length/2); glVertex3f(-track_width/2, tunnel_height, center_z + tunnel_length/2); glVertex3f(-track_width/2, 0, center_z + tunnel_length/2); glEnd()
    glBegin(GL_QUADS); glVertex3f(track_width/2, 0, center_z - tunnel_length/2); glVertex3f(track_width/2, tunnel_height, center_z - tunnel_length/2); glVertex3f(track_width/2, tunnel_height, center_z + tunnel_length/2); glVertex3f(track_width/2, 0, center_z + tunnel_length/2); glEnd()
    glBegin(GL_QUADS); glVertex3f(-track_width/2, tunnel_height, center_z - tunnel_length/2); glVertex3f(track_width/2, tunnel_height, center_z - tunnel_length/2); glVertex3f(track_width/2, tunnel_height, center_z + tunnel_length/2); glVertex3f(-track_width/2, tunnel_height, center_z + tunnel_length/2); glEnd()

def draw_wheel():
    q = gluNewQuadric()
    glColor3f(0.1, 0.1, 0.1)
    gluCylinder(q, 9, 9, 6, 16, 16)
    glColor3f(0.2, 0.2, 0.2)
    gluDisk(q, 0, 9, 16, 1)
    glPushMatrix()
    glTranslatef(0, 0, 6)
    glColor3f(0.75, 0.75, 0.75)
    gluDisk(q, 0, 7, 16, 1)
    glColor3f(0.4, 0.4, 0.4)
    gluDisk(q, 0, 2, 16, 1)
    glPopMatrix()

def draw_car(is_player=False, is_police=False, is_oncoming=False):
    glPushMatrix()
    if is_player:
        glColor3f(0.1, 0.5, 1.0)
        if shield_active:
            glColor4f(0.5, 0.8, 1.0, 0.5)
            glutSolidSphere(35, 16, 16)
    elif is_police: glColor3f(0.1, 0.1, 0.8)
    elif is_oncoming: glColor3f(1.0, 1.0, 1.0)
    else: glColor3f(1.0, 0.2, 0.2)
    glScalef(1.0, 0.5, 2.0); glutSolidCube(30); glPopMatrix()
    glPushMatrix(); glTranslatef(0, 12, -5)
    if is_player: glColor3f(0.3, 0.7, 1.0)
    elif is_police: glColor3f(1.0, 1.0, 1.0)
    elif is_oncoming: glColor3f(0.8, 0.8, 0.8)
    else: glColor3f(1.0, 0.4, 0.4)
    glScalef(0.8, 0.4, 1.2); glutSolidCube(25); glPopMatrix()
    if is_police:
        glPushMatrix(); glTranslatef(0, 25, -5)
        if int(glutGet(GLUT_ELAPSED_TIME) / 250) % 2 == 0: glColor3f(1,0,0)
        else: glColor3f(0,0,1)
        glScalef(0.2, 0.2, 0.2); glutSolidCube(20); glPopMatrix()
    wheel_positions = [(-18, -5, 20), (18, -5, 20), (-18, -5, -20), (18, -5, -20)]
    for i, (x, y, z) in enumerate(wheel_positions):
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(-90, 0, 1, 0)
        glRotatef(wheel_rotation_angle, 0, 0, 1)
        draw_wheel()
        glPopMatrix()

def draw_blob_shadow(y_offset, radius):
    glPushMatrix(); glTranslatef(0, y_offset, 0)
    glScalef(1, 0.01, 1); glColor4f(0, 0, 0, 0.4)
    glutSolidSphere(radius, 16, 16); glPopMatrix()

def draw_player():
    glPushMatrix(); glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 1, 0); draw_car(is_player=True); glPopMatrix()
    glPushMatrix(); glTranslatef(player_pos[0], 0.1, player_pos[2])
    draw_blob_shadow(0, 30); glPopMatrix()
    if boost_active:
        glPushMatrix(); glTranslatef(player_pos[0], player_pos[1], player_pos[2])
        glRotatef(player_angle, 0, 1, 0); glTranslatef(0, 5, -35)
        glDisable(GL_LIGHTING)
        glBegin(GL_TRIANGLES)
        glColor4f(0.2, 0.6, 1.0, 0.8)
        glVertex3f(0, 0, 0); glVertex3f(-6, -2, -25); glVertex3f(6, -2, -25)
        glColor4f(1.0, 0.8, 0.2, 0.9)
        glVertex3f(0, -1, -5); glVertex3f(-3, -3, -15); glVertex3f(3, -3, -15)
        glEnd(); glEnable(GL_LIGHTING); glPopMatrix()

def draw_opponents():
    for car in opponents:
        glPushMatrix(); glTranslatef(car['pos'][0], car['pos'][1], car['pos'][2])
        glRotatef(car['angle'], 0, 1, 0); draw_car(); glPopMatrix()
        glPushMatrix(); glTranslatef(car['pos'][0], 0.1, car['pos'][2])
        draw_blob_shadow(0, 30); glPopMatrix()

def draw_oncoming_cars():
    for car in oncoming_cars:
        glPushMatrix(); glTranslatef(car['pos'][0], car['pos'][1], car['pos'][2])
        glRotatef(car['angle'], 0, 1, 0); draw_car(is_oncoming=True); glPopMatrix()
        glPushMatrix(); glTranslatef(car['pos'][0], 0.1, car['pos'][2])
        draw_blob_shadow(0, 30); glPopMatrix()

def draw_police_car():
    if police_chase_active:
        pos = police_car['pos']
        glPushMatrix(); glTranslatef(pos[0], pos[1], pos[2])
        glRotatef(police_car['angle'], 0, 1, 0); draw_car(is_police=True); glPopMatrix()
        glPushMatrix(); glTranslatef(pos[0], 0.1, pos[2])
        draw_blob_shadow(0, 30); glPopMatrix()

def draw_coins():
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 0.85, 0.0)
    for coin in coins:
        if coin['active']:
            glPushMatrix(); glTranslatef(coin['pos'][0], coin['pos'][1], coin['pos'][2])
            glRotatef(coin['angle'], 0, 1, 0)
            glutSolidTorus(2, 8, 8, 20)
            glPopMatrix()
    glEnable(GL_LIGHTING)

def draw_obstacles():
    q = gluNewQuadric()
    for obs in obstacles:
        glPushMatrix(); glTranslatef(obs['pos'][0], obs['pos'][1], obs['pos'][2])
        glColor3f(1, 0.8, 0)
        if obs['type'] == 'cube': glutSolidCube(obs['size'][0])
        elif obs['type'] == 'cone': glRotatef(-90, 1, 0, 0); glutSolidCone(obs['size'][0], obs['size'][1], 16, 16)
        elif obs['type'] == 'barrier': glScalef(obs['size'][0], obs['size'][1], obs['size'][2]); glutSolidCube(1)
        glPopMatrix()
    pos = moving_obstacle['pos']
    glPushMatrix(); glTranslatef(pos[0], pos[1], pos[2])
    glColor3f(1.0, 0.5, 0)
    glScalef(moving_obstacle['size'][0], moving_obstacle['size'][1], moving_obstacle['size'][2])
    glutSolidCube(1); glPopMatrix()
    gate = swinging_gate
    glPushMatrix(); glTranslatef(gate['pos'][0], gate['pos'][1], gate['pos'][2])
    glRotatef(gate['angle'], 0, 1, 0)
    glColor3f(0.6, 0.4, 0.2)
    glScalef(gate['size'][0], gate['size'][1], gate['size'][2])
    glutSolidCube(1); glPopMatrix()
    group = moving_cone_group
    for offset in group['cones']:
        glPushMatrix()
        glTranslatef(group['pos'][0] + offset[0], group['pos'][1], group['pos'][2] + offset[1])
        glColor3f(1, 0.8, 0); glRotatef(-90, 1, 0, 0)
        glutSolidCone(20, 50, 16, 16); glPopMatrix()

def draw_powerups():
    for p in powerups:
        if p['active']:
            glPushMatrix(); glTranslatef(p['pos'][0], p['pos'][1], p['pos'][2])
            if p['type'] == 'health': glColor3f(0, 1, 0); glutSolidCube(20)
            elif p['type'] == 'shield': glColor3f(0.2, 0.8, 1.0); glutSolidSphere(15,16,16)
            glPopMatrix()

def update_player():
    global player_pos, player_speed, player_angle, damage_effect_timer, wheel_rotation_angle, score_points
    if game_state != "racing": return
    wheel_rotation_angle = (wheel_rotation_angle + player_speed * 10) % 360
    for hazard in hazards:
        dist_sq = (player_pos[0] - hazard['pos'][0])**2 + (player_pos[2] - hazard['pos'][2])**2
        if dist_sq < hazard['radius']**2:
            if hazard['type'] == 'oil': player_speed *= 0.8
            elif hazard['type'] == 'slippery': player_angle += random.uniform(-10, 10)
    if damage_effect_timer > 0:
        max_speed = 6.0 * (player_health / 100.0)
        player_angle += random.uniform(-1.5, 1.5)
        damage_effect_timer -= 1
    else:
        max_speed = 10.0 * (player_health / 100.0)
    if boost_active:
        max_speed *= 1.6
    acceleration = (0.18 if boost_active else 0.15); drag = (0.985 if boost_active else 0.98); steer_speed = 1.5
    if abs(player_speed) < 0.5: steer_speed = 0
    if key_states['a']: player_angle += steer_speed
    if key_states['d']: player_angle -= steer_speed
    if key_states['w']: player_speed += acceleration
    elif key_states['s']: player_speed -= acceleration
    player_speed = max(-max_speed/2, min(max_speed, player_speed)); player_speed *= drag
    rad_angle = math.radians(player_angle)
    dx = math.sin(rad_angle) * player_speed
    dz = math.cos(rad_angle) * player_speed
    px, py, pz = player_pos
    new_px, new_pz = px + dx, pz + dz
    new_py = 5
    if -700 < new_pz < 700:
        bridge_height = 80; ramp_length=400;
        if -700 < new_pz < -100: new_py = lerp(5, bridge_height + 5, (new_pz + 700) / ramp_length)
        elif -100 < new_pz < 100: new_py = bridge_height + 5
        elif 100 < new_pz < 700: new_py = lerp(bridge_height + 5, 5, (new_pz - 100) / ramp_length)
    if -8200 < new_pz < -6800:
        bridge_height = 50; ramp_length=400; deck_length=600; center_z=-7500
        if (center_z - deck_length/2 - ramp_length) < new_pz < (center_z - deck_length/2): new_py = lerp(5, bridge_height+5, (new_pz - (center_z-deck_length/2-ramp_length))/ramp_length)
        elif (center_z - deck_length/2) < new_pz < (center_z + deck_length/2): new_py = bridge_height + 5
        elif (center_z + deck_length/2) < new_pz < (center_z+deck_length/2+ramp_length): new_py = lerp(bridge_height+5, 5, (new_pz - (center_z+deck_length/2))/ramp_length)
    player_pos = [new_px, new_py, new_pz]
    if not cheat_mode:
        player_pos[0] = max(-TRACK_WIDTH/2 + 20, min(TRACK_WIDTH/2 - 20, player_pos[0]))
        min_z = -TRACK_LENGTH/2 + 50
        max_z = TRACK_LENGTH/2 - 10
        if player_pos[2] < min_z:
            player_pos[2] = min_z; player_speed *= 0.7
        if player_pos[2] > max_z:
            player_pos[2] = max_z; player_speed *= 0.7
    score_points += abs(player_speed) * 0.25

def update_opponents():
    if game_state != "racing": return
    for car in opponents:
        target_pos = car['target_pos']
        pos = car['pos']
        dx = target_pos[0] - pos[0]; dz = target_pos[1] - pos[2]
        dist = math.sqrt(dx**2 + dz**2)
        if dist > 1:
            car['angle'] = math.degrees(math.atan2(dx, dz))
            pos[0] += (dx / dist) * car['speed']
            pos[2] += (dz / dist) * car['speed']

def update_moving_obstacles():
    moving_obstacle['pos'][0] += 2.0 * moving_obstacle['dir']
    if moving_obstacle['pos'][0] > moving_obstacle['end_x'] or moving_obstacle['pos'][0] < moving_obstacle['start_x']:
        moving_obstacle['dir'] *= -1
    gate = swinging_gate
    gate['angle'] += gate['speed'] * gate['dir']
    if abs(gate['angle']) > gate['max_angle']:
        gate['dir'] *= -1
    moving_cone_group['pos'][0] += 1.5 * moving_cone_group['dir']
    if moving_cone_group['pos'][0] > moving_cone_group['end_x'] or moving_cone_group['pos'][0] < moving_cone_group['start_x']:
        moving_cone_group['dir'] *= -1

def update_oncoming_cars():
    global oncoming_spawn_timer, oncoming_cars
    if game_state != "racing": return
    oncoming_spawn_timer -= 1
    if oncoming_spawn_timer <= 0:
        x_pos = random.uniform(-TRACK_WIDTH/2 + 50, TRACK_WIDTH/2 - 50)
        z_pos = player_pos[2] + 4000
        if z_pos < TRACK_LENGTH/2:
            oncoming_cars.append({'pos': [x_pos, 5, z_pos], 'angle': 180, 'speed': 8.0, 'target_pos': (x_pos, -TRACK_LENGTH/2)})
        oncoming_spawn_timer = random.randint(120, 300)
    cars_to_keep = []
    for car in oncoming_cars:
        target_pos = car['target_pos']
        pos = car['pos']
        dx = target_pos[0] - pos[0]; dz = target_pos[1] - pos[2]
        dist = math.sqrt(dx**2 + dz**2)
        if dist > 1:
            pos[2] += (dz / dist) * car['speed']
        if pos[2] > player_pos[2] - 500:
            cars_to_keep.append(car)
    oncoming_cars = cars_to_keep

def update_coins_and_police():
    global police_chase_active, police_car
    for coin in coins:
        coin['angle'] = (coin['angle'] + 5) % 360
    if police_chase_active:
        pos = police_car['pos']
        dx = player_pos[0] - pos[0]
        dz = player_pos[2] - pos[2]
        dist = math.sqrt(dx**2 + dz**2)
        if dist > 1:
            police_car['angle'] = math.degrees(math.atan2(dx, dz))
            pos[0] += (dx / dist) * police_car['speed']
            pos[2] += (dz / dist) * police_car['speed']

def update_crossing_pedestrian():
    global pedestrian_cross_timer, crossing_pedestrian
    if police_chase_active: return
    if not crossing_pedestrian.get('active'):
        pedestrian_cross_timer -= 1
        if pedestrian_cross_timer <= 0:
            z_pos = player_pos[2] + random.uniform(800, 1200)
            start_x = -TRACK_WIDTH/2 - 20
            crossing_pedestrian = {'active': True, 'pos': [start_x, 15, z_pos], 'target_x': TRACK_WIDTH/2 + 20, 'speed': 2.0}
    else:
        crossing_pedestrian['pos'][0] += crossing_pedestrian['speed']
        if crossing_pedestrian['pos'][0] > crossing_pedestrian['target_x']:
            crossing_pedestrian['active'] = False
            pedestrian_cross_timer = random.randint(500, 1000)

def check_collisions():
    global player_health, player_speed, damage_effect_timer, shield_active, shield_timer, player_coins, police_chase_active, police_car, game_state, score_points, reward_message
    px, _, pz = player_pos
    if cheat_mode:
        return
    player_radius = 25
    for coin in coins:
        if coin['active']:
            dist_sq = (px - coin['pos'][0])**2 + (pz - coin['pos'][2])**2
            if dist_sq < (player_radius + 8)**2:
                coin['active'] = False
                player_coins += 1
                coin_reward = 50
                score_points += coin_reward
                reward_message['text'] = f"+{coin_reward} Reward!"
                reward_message['timer'] = 90
    if crossing_pedestrian.get('active'):
        ped = crossing_pedestrian
        dist_sq = (px - ped['pos'][0])**2 + (pz - ped['pos'][2])**2
        if dist_sq < (player_radius + 10)**2:
            ped['active'] = False
            if not police_chase_active:
                police_chase_active = True
                police_car = {'pos': [player_pos[0], 5, player_pos[2] - 200], 'angle': player_angle, 'speed': 10.5}
    if police_chase_active:
        pol = police_car
        dist_sq = (px - pol['pos'][0])**2 + (pz - pol['pos'][2])**2
        if dist_sq < (player_radius + 25)**2:
            game_state = "busted"
    if shield_active: return
    player_box = (px - 15, pz - 30, px + 15, pz + 30)
    all_obs_list = obstacles + [moving_obstacle, swinging_gate, moving_cone_group]
    for obs in all_obs_list:
        if obs['type'] == 'cone_group':
            for offset in obs['cones']:
                ox, oz = obs['pos'][0] + offset[0], obs['pos'][2] + offset[1]
                dist_sq = (px-ox)**2 + (pz-oz)**2
                if dist_sq < (player_radius + 10)**2:
                    player_health -= 10; player_speed *= 0.8; damage_effect_timer = 30
                    break
        else:
            ox, _, oz = obs['pos']
            if obs['type'] == 'cone': w = d = obs['size'][0]
            else: w = obs['size'][0] / 2; d = obs['size'][2] / 2
            obs_box = (ox - w, oz - d, ox + w, oz + d)
            if (player_box[0] < obs_box[2] and player_box[2] > obs_box[0] and
                player_box[1] < obs_box[3] and player_box[3] > obs_box[1]):
                player_health -= 25; player_speed = -player_speed * 0.7; damage_effect_timer = 120
    for p in powerups:
        if p['active']:
            ox, _, oz = p['pos']; dist_sq = (px-ox)**2 + (pz-oz)**2
            if dist_sq < (25)**2:
                if p['type'] == 'health': player_health = min(100.0, player_health + 50)
                elif p['type'] == 'shield': shield_active = True; shield_timer = 300
                p['active'] = False
    for car in opponents:
        ox, _, oz = car['pos']; dist_sq = (px - ox)**2 + (pz - oz)**2
        if dist_sq < (30 + 30)**2:
            player_health -= 5; player_speed *= 0.8; damage_effect_timer = 60
    for car in oncoming_cars:
        ox, _, oz = car['pos']; dist_sq = (px - ox)**2 + (pz - oz)**2
        if dist_sq < (30 + 30)**2:
            player_health -= 50; player_speed = 0; damage_effect_timer = 180
            car['pos'][2] -= 200

def lerp(a, b, t): return a * (1.0 - t) + b * t

def update_lighting_and_sky():
    global time_of_day, sky_color, light_color
    time_of_day = (time_of_day + 0.0001) % 1.0; angle = time_of_day * 2 * math.pi
    light_x = math.cos(angle) * 3000
    light_y = math.sin(angle) * 3000
    light_z = 1000
    lightPosition = [light_x, light_y, light_z, 0]
    if 0.25 <= time_of_day < 0.75:
        t = (time_of_day - 0.25) * 2
        if t < 0.5: t2 = t * 2
        else: t2 = (1-t)*2
        sky_color = [lerp(0.9, 0.5, t2), lerp(0.6, 0.8, t2), lerp(0.4, 1.0, t2)]
        light_color = [lerp(1.0, 1.0, t2), lerp(0.8, 1.0, t2), lerp(0.6, 1.0, t2)]
    else:
        sky_color = [0.05, 0.05, 0.15]
        light_color = [0.3, 0.3, 0.4]
    glLightfv(GL_LIGHT0, GL_POSITION, lightPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color + [1.0])
    if headlights_on:
        glEnable(GL_LIGHT1)
        headlight_pos = [player_pos[0] + 30 * math.sin(math.radians(player_angle)),
                           player_pos[1] + 10,
                           player_pos[2] + 30 * math.cos(math.radians(player_angle)), 1]
        headlight_dir = [math.sin(math.radians(player_angle)), 0, math.cos(math.radians(player_angle))]
        glLightfv(GL_LIGHT1, GL_POSITION, headlight_pos)
        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, headlight_dir)
        glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 30.0)
        glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 10.0)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [1.0, 1.0, 0.8, 1.0])
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.005)
        glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.0001)
    else:
        glDisable(GL_LIGHT1)

def init_particles(count):
    global particles; particles = []
    if current_weather not in ["rain", "snow"]: return
    for _ in range(count):
        px = player_pos[0] + random.uniform(-GRID_LENGTH/2, GRID_LENGTH/2)
        py = random.uniform(500, 1000)
        pz = player_pos[2] + random.uniform(-2000, 2000)
        vel = [0, 0, 0]
        if current_weather == "rain": vel = [0, random.uniform(-20, -15), 0]
        elif current_weather == "snow": vel = [random.uniform(-1, 1), random.uniform(-4, -2), 0]
        particles.append({'pos': [px, py, pz], 'vel': vel, 'type': current_weather})

def update_particles():
    for p in particles:
        p['pos'][0] += p['vel'][0]; p['pos'][1] += p['vel'][1]; p['pos'][2] += p['vel'][2]
        if p['type'] == 'snow': p['pos'][0] += math.sin(p['pos'][1] * 0.1) * 0.5
        if p['pos'][1] < 0 or abs(p['pos'][0] - player_pos[0]) > GRID_LENGTH/2 or abs(p['pos'][2] - player_pos[2]) > 2000:
            p['pos'][0] = player_pos[0] + random.uniform(-GRID_LENGTH/2, GRID_LENGTH/2)
            p['pos'][1] = 1000
            p['pos'][2] = player_pos[2] + random.uniform(-2000, 2000)

def update_pedestrians():
    for p in pedestrians:
        p['pos'][2] += p['speed'] * p['dir']
        if p['pos'][2] > TRACK_LENGTH/2 or p['pos'][2] < -TRACK_LENGTH/2:
            p['dir'] *= -1

def apply_weather_effects():
    glFogfv(GL_FOG_COLOR, sky_color + [1.0])
    if current_weather == "fog": glFogf(GL_FOG_START, 400.0); glFogf(GL_FOG_END, 1800.0)
    elif current_weather == "rain": glFogf(GL_FOG_START, 800.0); glFogf(GL_FOG_END, 2500.0)
    elif current_weather == "snow": glFogf(GL_FOG_START, 350.0); glFogf(GL_FOG_END, 1600.0)
    init_particles(300)

def manage_fog_state():
    is_foggy_weather = current_weather in ["fog", "rain", "snow"]
    if is_foggy_weather and not headlights_on: glEnable(GL_FOG)
    else: glDisable(GL_FOG)

def setupCamera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(75, WINDOW_WIDTH / WINDOW_HEIGHT, 1.0, 80000.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    if camera_mode == "third_person":
        cam_x = player_pos[0] - camera_distance * math.sin(math.radians(player_angle + camera_angle_h))
        cam_y = player_pos[1] + camera_distance/2 + camera_angle_y
        cam_z = player_pos[2] - camera_distance * math.cos(math.radians(player_angle + camera_angle_h))
        look_at = (player_pos[0], player_pos[1] + 20, player_pos[2])
        gluLookAt(cam_x, cam_y, cam_z, *look_at, 0, 1, 0)
    elif camera_mode == "first_person":
        cam_x = player_pos[0] + 15 * math.sin(math.radians(player_angle))
        cam_y = player_pos[1] + 20
        cam_z = player_pos[2] + 15 * math.cos(math.radians(player_angle))
        look_at = (player_pos[0] + 500 * math.sin(math.radians(player_angle)), player_pos[1] + 15, player_pos[2] + 500 * math.cos(math.radians(player_angle)))
        gluLookAt(cam_x, cam_y, cam_z, *look_at, 0, 1, 0)

def keyboardListener(key, x, y):
    global headlights_on, boost_active, boost_timer, boost_cooldown, cheat_mode
    key_str = key.decode('utf-8').lower()
    if key_str in key_states: key_states[key_str] = True
    if key_str == 'r': reset_game()
    if key_str == 'f': headlights_on = not headlights_on
    if key_str == 't': reset_car_position()
    if key_str == 'n':
        if not boost_active and boost_cooldown <= 0:
            boost_active = True; boost_timer = 300; boost_cooldown = 900
    if key_str == 'c': cheat_mode = not cheat_mode

def keyboardUpListener(key, x, y):
    key_str = key.decode('utf-8').lower()
    if key_str in key_states: key_states[key_str] = False

def specialKeyListener(key, x, y):
    global camera_angle_y, camera_angle_h
    if key == GLUT_KEY_UP: camera_angle_y += 5
    elif key == GLUT_KEY_DOWN: camera_angle_y -= 5
    elif key == GLUT_KEY_LEFT: camera_angle_h -= 5
    elif key == GLUT_KEY_RIGHT: camera_angle_h += 5

def mouseListener(button, state, x, y):
    global camera_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = "first_person" if camera_mode == "third_person" else "third_person"

def idle():
    global game_state, just_crossed_finish, weather_change_timer, current_weather, shield_active, shield_timer, boost_active, boost_timer, boost_cooldown, current_lap, lap_start_time, lap_times, score_points, last_player_z, reward_message
    manage_fog_state()
    update_player(); update_opponents(); update_moving_obstacles(); check_collisions()
    update_lighting_and_sky(); update_particles(); update_pedestrians()
    update_coins_and_police(); update_crossing_pedestrian(); update_oncoming_cars()
    if boost_active:
        boost_timer -= 1
        if boost_timer <= 0:
            boost_active = False
    if boost_cooldown > 0:
        boost_cooldown -= 1
    if shield_active:
        shield_timer -= 1
        if shield_timer <= 0: shield_active = False
    
    if reward_message['timer'] > 0:
        reward_message['timer'] -= 1
        
    weather_change_timer += 1
    if weather_change_timer > WEATHER_DURATION:
        weather_change_timer = 0
        current_weather = random.choice(["clear", "rain", "snow", "fog"])
        apply_weather_effects()
    finish_threshold = TRACK_LENGTH/2 - 50
    if last_player_z <= finish_threshold and player_pos[2] > finish_threshold and not just_crossed_finish:
        just_crossed_finish = True
        current_time = glutGet(GLUT_ELAPSED_TIME)
        lap_time_sec = (current_time - (lap_start_time if lap_start_time else race_start_time)) / 1000.0
        lap_times.append(lap_time_sec)
        score_points += 1000
        if current_lap >= total_laps:
            game_state = "won"
        else:
            current_lap += 1
            for car in opponents: car['speed'] *= 1.08
            moving_obstacle['dir'] = 1 if moving_obstacle['dir'] >= 0 else -1
            swinging_gate['speed'] *= 1.08
            player_pos[2] = -TRACK_LENGTH/2 + 120; player_pos[0] = 0; player_speed = 0
            lap_start_time = current_time; just_crossed_finish = False
    last_player_z = player_pos[2]
    if player_health <= 0: game_state = "lost"
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST); setupCamera(); glEnable(GL_LIGHTING)
    draw_environment(); draw_track(); draw_obstacles(); draw_hazards()
    draw_powerups(); draw_player(); draw_opponents(); draw_particles()
    draw_coins(); draw_police_car(); draw_oncoming_cars()
    glDisable(GL_LIGHTING); draw_ui(); glutSwapBuffers()

def init():
    global race_start_time, lap_start_time, current_lap, lap_times, score_points, boost_active, boost_timer, boost_cooldown, cheat_mode
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST); glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_LIGHT1); glEnable(GL_COLOR_MATERIAL)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])
    apply_weather_effects()
    generate_city_layout()
    generate_pedestrians()
    generate_coins()
    race_start_time = glutGet(GLUT_ELAPSED_TIME)
    lap_start_time = race_start_time
    current_lap = 1
    lap_times = []
    score_points = 0
    boost_active = False; boost_timer = 0; boost_cooldown = 0
    cheat_mode = False

def reset_game():
    global player_pos, player_angle, player_speed, player_health, game_state, race_start_time, opponents, just_crossed_finish, damage_effect_timer, shield_active, shield_timer, player_coins, police_chase_active, oncoming_cars, current_lap, lap_start_time, lap_times, score_points, boost_active, boost_timer, boost_cooldown, cheat_mode
    player_pos = [0, 5, -TRACK_LENGTH/2 + 100]
    player_angle = 0.0; player_speed = 0.0; player_health = 100.0
    damage_effect_timer = 0; shield_active = False; shield_timer = 0
    player_coins = 0; police_chase_active = False; oncoming_cars = []
    opponents[0]['pos'] = [-200, 5, -TRACK_LENGTH/2 + 50]
    opponents[1]['pos'] = [200, 5, -TRACK_LENGTH/2 + 50]
    for p in powerups: p['active'] = True
    game_state = "racing"; just_crossed_finish = False
    race_start_time = glutGet(GLUT_ELAPSED_TIME)
    lap_start_time = race_start_time
    current_lap = 1
    lap_times = []
    score_points = 0
    boost_active = False; boost_timer = 0; boost_cooldown = 0
    cheat_mode = False
    generate_city_layout()
    generate_pedestrians()
    generate_coins()

def reset_car_position():
    global player_pos, player_angle, player_speed, damage_effect_timer
    player_pos[0] = 0
    player_pos[1] = 5
    player_pos[2] = max(player_pos[2] - 120, -TRACK_LENGTH/2 + 120)
    player_angle = 0.0
    player_speed = 0.0
    damage_effect_timer = 0

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"3D Racing Game - Final Version")
    glutDisplayFunc(showScreen); glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener); glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener); glutMouseFunc(mouseListener)
    init(); glutMainLoop()

if __name__ == "__main__":
    main()