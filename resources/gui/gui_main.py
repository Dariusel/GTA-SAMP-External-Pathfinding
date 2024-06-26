import sys, os
from tkinter import *
from tkinter import font
from PIL import ImageTk, Image

import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resources.utils.file_paths import MAP_IMG_PATH, NODES_DATA_JSON
from resources.utils.vectors import Vector2, Vector3
from resources.utils.map_conversions import image_to_ingame_coords, ingame_to_image_coords
from resources.utils.nodes_classes import PathNode
from resources.utils.json_utils import load_json
from resources.utils.pathfinding.Dijkstra import pathfind_dijkstra
from resources.utils.memory.memory_adresses import *
from resources.utils.memory.utils.memory_utils import try_get_gta_sa
from resources.utils.memory.memory_events import blip_changed_event, marker_changed_event
from resources.utils.autodriver.autodriver_main import Autodriver
from resources.utils.keypress import release_keys



class MainGUI():
    _instance = None

    map_img_resized = Image.open(MAP_IMG_PATH).resize((512, 512), Image.Resampling.LANCZOS)
    get_gta_sa_interval_ms = 2500
    marker_size = 4 # start/end marker
    player_marker_size = 10

    theme_dark = {
        'bg': '#333333',
        'menu_bg': '#262626',
        'text_color': '#c5c5c5',
        'button_bg': '#262626',
        'button_border': '#1a9ef7'
    }

    def __init__(self):
        if MainGUI._instance:
            print('MainGUI already running')
            return
        MainGUI._instance = self

        # Define root
        self.root = Tk()

        self.gta_sa = try_get_gta_sa()

        self.player_marker = None
        self.start_marker = None
        self.end_marker = None

        self.start_marker_position_ingame = None
        self.end_marker_position_ingame = None

        self.solved_path = []
        self.path_line_ids = {}

        blip_changed_event.add_subscriber(self.on_blip_update)
        marker_changed_event.add_subscriber(self.on_marker_update)

        self.blip_autodrive_boolvar = BooleanVar()
        self.marker_autodrive_boolvar = BooleanVar()

        self.blip_autodrive = False
        self.marker_autodrive = False

        self.is_driving_to_blip = False
        self.is_driving_to_marker = False

        self.autodriver = None


    def display_main(self):
        self.root.title('GTA-SAMP External Pathfinding')
        self.root.resizable(0, 0) # Dont allow user to resize window

        # Create the menu bar
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # 'Pathfind' Menu
        pathfind_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Pathfind', menu=pathfind_menu)
        pathfind_menu.add_command(label='TEST', command=lambda: print("TEST"))

        # Canvas for map image
        self.canvas = Canvas(self.root, width=512, height=512)
        self.canvas.bind('<Button-1>', self.set_start_position) # LMB -> start_marker
        self.canvas.bind('<Button-3>', self.set_end_position) # RMB -> end_marker


        # Load and display the map image
        map_img_tk = ImageTk.PhotoImage(self.map_img_resized)
        self.canvas.create_image(0, 0, image=map_img_tk, anchor='nw')

        # Labels
        under_map_label = Label(text='LMB = Start Marker | RMB = End Marker', font=font.Font(family="Segoe UI", weight="bold"))

        # Buttons
        self.button_drive = Button(self.root, text='Drive', width=20, height=2, command=self.drive_button)
        self.button_pause = Button(self.root, text='Pause', width=9, height=2, command=self.pause_button)
        self.button_stop = Button(self.root, text='Stop', width=9, height=2, command=self.stop_autodriver)
        self.button_compute = Button(self.root, text='Compute Path', width=20, height=2, command=self.compute_button)
        self.button_clear = Button(self.root, text='Clear Start/End', width=20, height=2, command=self.clear_button)

        # Checkbuttons
        self.checkbutton_blip_autodrive = Checkbutton(self.root, text='Blip Autodrive (PRIORITY)', variable=self.blip_autodrive_boolvar,
                                                      command=self.blip_autodrive_check)
        self.checkbutton_marker_autodrive = Checkbutton(self.root, text='Marker Autodrive', variable=self.marker_autodrive_boolvar,
                                                        command=self.marker_autodrive_check)

        # Grid
        self.canvas.grid(row=0, column=0, columnspan=3, pady=10, padx=10)

        under_map_label.grid(column=0, row=1, columnspan=3, pady=2)

        self.button_drive.grid(column=0, row=4, pady=5)
        self.button_pause.grid(column=0, row=5, pady=5, padx=20, sticky='w')
        self.button_stop.grid(column=0, row=5, pady=5, padx=20, sticky='e')
        self.button_compute.grid(column=1, row=4, pady=5)
        self.button_clear.grid(column=2, row=4, pady=5)

        self.checkbutton_blip_autodrive.grid(column=0, row=2, pady=2, padx=10, sticky='w')
        self.checkbutton_marker_autodrive.grid(column=0, row=3, pady=2, padx=10, sticky='w')

        # Checks
        self.update_widget_states()

        # Theme
        self.change_theme(self.theme_dark)

        # Misc
        self.update_player_on_map()


        self.root.mainloop()
    

    def on_blip_update(self):
        if self.blip_autodrive:
            self.drive_to_blip()


    def on_marker_update(self):
        if self.marker_autodrive:
            self.drive_to_marker()


    def drive_to_blip(self):
        if not self.gta_sa:
            return
        
        if self.is_driving_to_marker:
            self.is_driving_to_marker = False

        # Stop autodriver if it was already running
        if self.autodriver:
            self.stop_autodriver()
        
        player_position = Vector3(self.gta_sa.read_float(PLAYER_X),
                                  self.gta_sa.read_float(PLAYER_Y),
                                  self.gta_sa.read_float(PLAYER_Z))
        
        blip_position = Vector3(self.gta_sa.read_float(GPS_BLIP_X),
                                       self.gta_sa.read_float(GPS_BLIP_Y),
                                       self.gta_sa.read_float(GPS_BLIP_Z))
        
        nodes_data = load_json(NODES_DATA_JSON)
        start_node = PathNode.get_closest_node_to_pos(nodes_data, player_position)
        target_node = PathNode.get_closest_node_to_pos(nodes_data, blip_position)

        self.solved_path = pathfind_dijkstra(nodes_data, start_node, target_node)
        self.draw_solved_path()      

        # Start driving with the current solved path
        self.autodriver = Autodriver(self.solved_path)
        self.autodriver.start_driving()

        self.is_driving_to_blip = True

        self.update_widget_states()


    def drive_to_marker(self):
        if not self.gta_sa:
            return
        
        if self.is_driving_to_blip:
            self.is_driving_to_blip = False

        if self.autodriver:
            self.stop_autodriver()
                
        player_position = Vector3(self.gta_sa.read_float(PLAYER_X),
                                  self.gta_sa.read_float(PLAYER_Y),
                                  self.gta_sa.read_float(PLAYER_Z))
        
        marker_position = Vector3(self.gta_sa.read_float(GPS_MARKER_X),
                                       self.gta_sa.read_float(GPS_MARKER_Y),
                                       self.gta_sa.read_float(GPS_MARKER_Z))
        
        nodes_data = load_json(NODES_DATA_JSON)
        start_node = PathNode.get_closest_node_to_pos(nodes_data, player_position)
        target_node = PathNode.get_closest_node_to_pos(nodes_data, marker_position)

        self.solved_path = pathfind_dijkstra(nodes_data, start_node, target_node)
        self.draw_solved_path()

        # Start driving with the current solved path
        self.autodriver = Autodriver(self.solved_path)
        self.autodriver.start_driving()

        self.is_driving_to_marker = True

        self.update_widget_states()


    def calculate_player_polygon(self, position: Vector3, angle_orientation):
        point1_angle_rad = math.radians(angle_orientation)
        point2_angle_rad = point1_angle_rad + math.radians(140)
        point3_angle_rad = point1_angle_rad + math.radians(180)
        point4_angle_rad= point1_angle_rad - math.radians(140)
        
        #Point 1
        x1 = position.x + self.player_marker_size * math.cos(point1_angle_rad)
        z1 = position.z - self.player_marker_size * math.sin(point1_angle_rad)
        #Point 2
        x2 = position.x + self.player_marker_size * math.cos(point2_angle_rad)
        z2 = position.z - self.player_marker_size * math.sin(point2_angle_rad)
        #Point 3
        x3 = position.x + self.player_marker_size * (math.cos(point3_angle_rad) * 0.2)
        z3 = position.z - self.player_marker_size * (math.sin(point3_angle_rad) * 0.2)
        #Point 4
        x4 = position.x + self.player_marker_size * math.cos(point4_angle_rad)
        z4 = position.z - self.player_marker_size * math.sin(point4_angle_rad)

        return x1, z1, x2, z2, x3, z3, x4, z4


    def update_player_on_map(self):
        # Return if gta_sa process is not found
        if self.gta_sa == None:
            return
        
        if self.player_marker:
            self.canvas.delete(self.player_marker)

        player_position = Vector3(self.gta_sa.read_float(PLAYER_X), self.gta_sa.read_float(PLAYER_Y), self.gta_sa.read_float(PLAYER_Z))
        player_position_to_image_pos = ingame_to_image_coords(player_position, self.map_img_resized)

        player_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)
        self.player_marker = self.canvas.create_polygon(self.calculate_player_polygon(player_position_to_image_pos, math.degrees(player_orientation)),
                                                        fill='#FF00EC')
        
        # Loop
        self.root.after(1000, self.update_player_on_map)
        

    def set_start_position(self, event):
        clicked_pos = Vector2(event.x, event.y)
        clicked_pos_v3 = Vector3(clicked_pos.x, 0, clicked_pos.y)
        self.start_marker_position_ingame = image_to_ingame_coords(clicked_pos_v3, self.map_img_resized)

        if self.start_marker != None:
            self.canvas.delete(self.start_marker)

        self.start_marker = self.canvas.create_oval(clicked_pos.x - self.marker_size, clicked_pos.y - self.marker_size,
                                                    clicked_pos.x + self.marker_size, clicked_pos.y + self.marker_size,
                                                    fill='green')
        
        self.update_widget_states()


    def set_end_position(self, event):
        clicked_pos = Vector2(event.x, event.y)
        clicked_pos_v3 = Vector3(clicked_pos.x, 0, clicked_pos.y)
        self.end_marker_position_ingame = image_to_ingame_coords(clicked_pos_v3, self.map_img_resized)

        if self.end_marker != None:
            self.canvas.delete(self.end_marker)

        self.end_marker = self.canvas.create_oval(clicked_pos.x - self.marker_size, clicked_pos.y - self.marker_size,
                                                    clicked_pos.x + self.marker_size, clicked_pos.y + self.marker_size,
                                                    fill='red')
        
        self.update_widget_states()
    

    def change_theme(self, theme):
        self.root.config(bg=theme['bg'])

        # Apply to widgets
        for widget in self.root.winfo_children():
            widget_type = widget.winfo_class()

            if widget_type == 'Menu':
                pass
            elif widget_type == 'Label':
                widget.configure(bg=theme['bg'], fg=theme['text_color'])
            elif widget_type == 'Button':
                widget.configure(bg=theme['button_bg'], fg=theme['text_color'], bd=2)
            elif widget_type == 'Checkbutton':
                widget.configure(bg=theme['bg'], fg=theme['text_color'], selectcolor=theme['menu_bg'], activebackground=theme['menu_bg'])
            elif widget_type == 'Canvas':
                widget.configure(bg=theme['bg'], highlightthickness=0)


    def blip_autodrive_check(self):
        if self.blip_autodrive_boolvar.get():
            self.blip_autodrive = True
        else:
            self.blip_autodrive = False

        self.update_widget_states()


    def marker_autodrive_check(self):
        if self.marker_autodrive_boolvar.get():
            self.marker_autodrive = True
        else:
            self.marker_autodrive = False
            
        self.update_widget_states()


    def drive_button(self):
        if self.solved_path:
            # If Autodriver exists and is paused resume it else create new instance and start driving
            if self.autodriver:
                if self.autodriver.is_paused:
                    self.autodriver.pause_driving(False)

                    self.update_widget_states()
                return
            
            self.autodriver = Autodriver(self.solved_path)
            self.autodriver.start_driving()

            self.blip_autodrive_boolvar.set(False)
            self.marker_autodrive_boolvar.set(False)
            self.update_widget_states()


    def pause_button(self):
        self.autodriver.pause_driving(True)

        self.update_widget_states()


    def stop_autodriver(self):
        if self.autodriver:
            self.autodriver.destroy()
            self.autodriver = None

            self.is_driving_to_blip = False
            self.is_driving_to_marker = False

            release_keys()

            self.update_widget_states()

    
    def draw_solved_path(self):
        # Delete old path markers from canvas if existing
        if self.path_line_ids:
            for path_line_id in self.path_line_ids.values():
                self.canvas.delete(path_line_id)
            
            self.path_line_ids = {} # Set dict as empty for the next part (Draw new path markers on canvas)

        # Draw new path markers on canvas
        for i, node in enumerate(self.solved_path):
            node_pos = Vector3(node.position.x, node.position.y, node.position.z)
            node_pos_to_image = ingame_to_image_coords(node_pos, self.map_img_resized)
            
            # Draw path line if 'node' isnt last one in solved_path
            if i != len(self.solved_path)-1:
                next_node = self.solved_path[i+1]
                next_node_pos = Vector3(next_node.position.x, next_node.position.y, next_node.position.z)
                next_node_pos_to_image = ingame_to_image_coords(next_node_pos, self.map_img_resized)

                path_line_id = self.canvas.create_line(node_pos_to_image.x, node_pos_to_image.z,
                                                                next_node_pos_to_image.x, next_node_pos_to_image.z,
                                                                width=2, fill='orange')

            # Store 
            self.path_line_ids[i] = path_line_id


    def compute_button(self):
        nodes_data = load_json(NODES_DATA_JSON)

        closest_node_to_start_marker = PathNode.get_closest_node_to_pos(nodes_data, self.start_marker_position_ingame)
        closest_node_to_end_marker = PathNode.get_closest_node_to_pos(nodes_data, self.end_marker_position_ingame)

        self.solved_path = pathfind_dijkstra(nodes_data, closest_node_to_start_marker, closest_node_to_end_marker)

        self.draw_solved_path()

        self.update_widget_states()


    def clear_button(self):
        if self.start_marker != None:
            self.canvas.delete(self.start_marker)
            self.start_marker = None

        if self.end_marker != None:
            self.canvas.delete(self.end_marker)
            self.end_marker = None

        if self.path_line_ids:
            for path_line_id in self.path_line_ids.values():
                self.canvas.delete(path_line_id)

            self.path_line_ids = {}

        self.update_widget_states()


    def update_widget_states(self):
        # Check 'run' button if it can be enabled
        if hasattr(self, 'button_drive'):
            self.button_drive.config(state=DISABLED)
            if self.gta_sa:
                # Disable button if autodriver is running already
                if self.autodriver:
                    if self.autodriver.is_paused:
                        self.button_drive.config(state=NORMAL)
                # Enable button if there is a path to execute
                elif self.solved_path:
                    self.button_drive.config(state=NORMAL)

        # Check 'pause' button if it can be enabled
        if hasattr(self, 'button_pause'):
            self.button_pause.config(state=DISABLED)
            if self.autodriver:
                if not self.autodriver.is_paused:
                    self.button_pause.config(state=NORMAL)

        # Check 'stop' button if it can be enabled
        if hasattr(self, 'button_stop'):
            self.button_stop.config(state=DISABLED)
            if self.autodriver:
                self.button_stop.config(state=NORMAL)

        # Check 'compute' button if it can be enabled
        if hasattr(self, 'button_compute'):
            self.button_compute.config(state=DISABLED)
            if self.start_marker != None and self.end_marker != None:
                self.button_compute.config(state=NORMAL)

        # Check 'clear' button if it can be enabled
        if hasattr(self, 'button_clear'):
            self.button_clear.config(state=DISABLED)
            if self.start_marker or self.end_marker:
                self.button_clear.config(state=NORMAL)

        # Check 'blip_autodrive' checkbutton if it can be enabled
        if hasattr(self, 'checkbutton_blip_autodrive'):
            self.checkbutton_blip_autodrive.config(state=DISABLED)
            if not self.autodriver:
                self.checkbutton_blip_autodrive.config(state=NORMAL)

        # Check 'marker_autodrive' checkbutton if it can be enabled
        if hasattr(self, 'checkbutton_marker_autodrive'):
            self.checkbutton_marker_autodrive.config(state=DISABLED)
            if not self.autodriver:
                self.checkbutton_marker_autodrive.config(state=NORMAL)

        # Check if 'gta_sa.exe' exists and draw text on canvas if not
        if not self.gta_sa:
            text_pos = Vector2(MainGUI.map_img_resized.size[0] / 2, 10)
            self.gta_sa_not_running_canvas_text = self.canvas.create_text(text_pos.x, text_pos.y,
                                                                          text="'gta_sa.exe' is not running!",
                                                                          font=font.Font(family="Segoe UI", size=20, weight='bold'),
                                                                          fill='red')


if __name__ == '__main__':
    gui = MainGUI()

    gui.display_main()
