import sys, os
from tkinter import *
from tkinter import font
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image

import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resources.utils.file_paths import MAP_IMG_PATH, NODES_DATA_JSON, AUTODRIVER_CONFIGS_DIR, SCRIPTS_DIR
from resources.utils.vectors import Vector2, Vector3
from resources.utils.map_conversions import image_to_ingame_coords, ingame_to_image_coords
from resources.utils.nodes_classes import PathNode
from resources.utils.json_utils import load_json, save_json
from resources.utils.pathfinding.Dijkstra import pathfind_dijkstra
from resources.utils.memory.utils.memory_utils import try_get_gta_sa
from resources.utils.memory.memory_adresses import *
from resources.utils.events.event_manager import EventManager, EventType
from resources.utils.autodriver.autodriver_main import Autodriver
from resources.utils.keypress import release_keys
from resources.gui.utils.gui_classes import GuidingMarker
from resources.gui.utils.utils import change_theme, Themes
from resources.gui.nodes_editor.nodes_editor import NodesEditor
from resources.utils.memory.memory_variables import GameData



class MainGUI():
    _instance = None

    get_gta_sa_interval = 2500 # miliseconds
    map_img_resized = Image.open(MAP_IMG_PATH).resize((512, 512), Image.Resampling.LANCZOS)
    marker_size = 4 # start/end marker
    player_marker_size = 10

    def __init__(self):
        if MainGUI._instance:
            print('MainGUI already running')
            return
        MainGUI._instance = self

        # Define root
        self.root = Tk()

        self.gta_sa = self.check_gta_sa_running()

        self.player_marker = None

        self.start_marker = None
        self.guiding_markers = []
        self.end_marker = None

        self.start_marker_position_ingame = None
        self.end_marker_position_ingame = None

        self.solved_path = []
        self.path_line_ids = {}

        EventManager.subscribe(self.on_blip_update, EventType.BlipChangedEvent)
        EventManager.subscribe(self.on_marker_update, EventType.MarkerChangedEvent)

        self.blip_autodrive_boolvar = BooleanVar()
        self.marker_autodrive_boolvar = BooleanVar()
        self.is_circuit_boolvar = BooleanVar()

        self.blip_autodrive = False
        self.marker_autodrive = False

        self.is_circuit = False

        self.is_driving_to_blip = False
        self.is_driving_to_marker = False

        self.autodriver = None

        self.config_files = {}
        for config in os.listdir(AUTODRIVER_CONFIGS_DIR):
            if config.endswith('.ini'):
                config_path = os.path.join(AUTODRIVER_CONFIGS_DIR, config)
                self.config_files[config] = config_path
        Autodriver._config_file = self.config_files['default.ini']

        self.selected_script = None

        self.nodes_editor = None


    def check_gta_sa_running(self):
        try_get_gta_sa()

        self.root.after(MainGUI.get_gta_sa_interval, self.check_gta_sa_running)


    def display_main(self):
        self.root.title('GTA-SAMP External Pathfinding')
        self.root.resizable(0, 0) # Dont allow user to resize window

        # Create the menu bar
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # 'Path' Menu
        path_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Path', menu=path_menu)
        path_menu.add_command(label='Save Path', command=self.save_path)
        path_menu.add_command(label='Load Path', command=self.load_path)

        # 'Config' Menu
        config_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Config', menu=config_menu)
        for config_name in self.config_files.keys():
            config_menu.add_command(label=config_name, command=lambda name=config_name: self.switch_autodriver_config(name))

        # 'Scripts' Menu
        scripts_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Scripts', menu=scripts_menu)
        scripts_menu.add_command(label='Load Script', command=self.load_script)

        # 'Tools' Menu
        tools_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Tools', menu=tools_menu)
        tools_menu.add_command(label='Nodes Editor', command=lambda: NodesEditor(self.root))

        # Canvas for map image
        self.canvas = Canvas(self.root, width=512, height=512)
        self.canvas.bind('<Button-1>', self.set_start_position) # LMB -> start_marker
        self.canvas.bind('<Button-2>', self.set_guider_position) # MMB -> guider
        self.canvas.bind('<Button-3>', self.set_end_position) # RMB -> end_marker


        # Load and display the map image
        map_img_tk = ImageTk.PhotoImage(self.map_img_resized)
        self.canvas.create_image(0, 0, image=map_img_tk, anchor='nw')

        # Labels
        under_map_label = Label(text='LMB = Start Marker | MMB = Guiding Marker | RMB = End Marker', font=font.Font(family="Segoe UI", weight="bold"))

        # Buttons
        self.button_drive = Button(self.root, text='Drive', width=20, height=2, command=self.drive_path)
        self.button_pause = Button(self.root, text='Pause', width=9, height=2, command=self.pause_autodriver)
        self.button_stop = Button(self.root, text='Stop', width=9, height=2, command=self.stop_autodriver)
        self.button_compute = Button(self.root, text='Compute Path', width=20, height=2, command=self.compute_button)
        self.button_clear = Button(self.root, text='Clear Start/End', width=20, height=2, command=self.clear_canvas)

        # Checkbuttons
        self.checkbutton_blip_autodrive = Checkbutton(self.root, text='Blip Autodrive (PRIORITY)', variable=self.blip_autodrive_boolvar,
                                                      command=self.checkbuttons_update)
        self.checkbutton_marker_autodrive = Checkbutton(self.root, text='Marker Autodrive', variable=self.marker_autodrive_boolvar,
                                                        command=self.checkbuttons_update)
        self.checkbutton_is_circuit = Checkbutton(self.root, text='Is Circuit', variable=self.is_circuit_boolvar,
                                                  command=self.checkbuttons_update)

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
        self.checkbutton_is_circuit.grid(column=1, row=3, pady=2, padx=10, sticky='w')

        # Checks
        self.update_widget_states()

        # Theme
        change_theme(self.root, Themes.theme_dark)

        # Misc
        #self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.update_player_on_map()


        self.root.mainloop()
    

    def save_path(self):
        if not self.solved_path:
            messagebox.showwarning('No existing path', 'You have to create a path before saving it.')
            return
        
        # Select save path
        default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'saves', 'paths'))
                                      
        save_path = filedialog.asksaveasfilename(
            title="Select 'path' file",
            filetypes=[("JSON files", "*.json")],
            initialdir=default_dir
        )
        if not save_path.endswith('.json'):
            save_path += '.json'

        # Convert self.solved_path to JSON
        path_json = {
            "header": {
                "is_circuit": self.is_circuit
            },
            "path":{

            }
        }
        for node in self.solved_path:
            path_json['path'][str(node.node_id)] = node.to_dict()

        save_json(path_json, save_path)


    def load_path(self):
        # Select file
        default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'saves', 'paths'))
                                      
        path_file = filedialog.askopenfilename(
            title="Select 'path' file",
            filetypes=[("JSON files", "*.json")],
            initialdir=default_dir
        )

        if not path_file:
            return
        
        # Read file and place in self.solved_path
        self.clear_canvas()

        path_json = load_json(path_file)
        self.solved_path = []
        self.solved_path.extend(PathNode.from_dict(node) for node in path_json['path'].values())

        self.is_circuit = path_json['header']['is_circuit']
        self.is_circuit_boolvar.set(self.is_circuit)

        # Updates canvas, buttons, checkbuttons
        self.draw_solved_path()
        self.update_widget_states()

        # Draw start and end marker after drawing path so markers are on top
        start_marker_pos_image = ingame_to_image_coords(self.solved_path[0].position, self.map_img_resized)

        self.start_marker = self.canvas.create_oval(start_marker_pos_image.x - self.marker_size, start_marker_pos_image.z - self.marker_size,
                                                    start_marker_pos_image.x + self.marker_size, start_marker_pos_image.z + self.marker_size,
                                                    fill='green')
        
        # Only draw end marker if path is not circuit
        if not self.is_circuit:
            end_marker_pos_image = ingame_to_image_coords(self.solved_path[len(self.solved_path)-1].position, self.map_img_resized)
            self.end_marker = self.canvas.create_oval(end_marker_pos_image.x - self.marker_size, end_marker_pos_image.z - self.marker_size,
                                                      end_marker_pos_image.x + self.marker_size, end_marker_pos_image.z + self.marker_size,
                                                      fill='red')


    def switch_autodriver_config(self, config):
        Autodriver._config_file = self.config_files[config]


    def load_script(self):
        # Select file
        default_dir = SCRIPTS_DIR

        script_file = filedialog.askopenfilename(
            title="Select 'script' file",
            filetypes=[("Python", "*.py")],
            initialdir=default_dir
        )

        if not script_file:
            return

        self.selected_script = script_file


    def on_blip_update(self):
        if self.blip_autodrive:
            self.drive_to_blip()


    def on_marker_update(self):
        if self.marker_autodrive:
            self.drive_to_marker()


    def drive_to_blip(self):
        if GameData.gta_sa:
            return
        
        if self.is_driving_to_marker:
            self.is_driving_to_marker = False

        if self.is_circuit:
            self.is_circuit = False
            self.is_circuit_boolvar.set(False)

        # Stop autodriver if it was already running
        if self.autodriver:
            self.stop_autodriver()
        
        nodes_data = load_json(NODES_DATA_JSON)
        start_node = PathNode.get_closest_node_to_pos(nodes_data, GameData.player_pos)
        target_node = PathNode.get_closest_node_to_pos(nodes_data, GameData.blip_pos)

        self.solved_path = pathfind_dijkstra(nodes_data, start_node, target_node)
        self.draw_solved_path()      

        # Start driving with the current solved path
        self.autodriver = Autodriver(self.solved_path)
        self.autodriver.start_driving(self.is_circuit)

        self.is_driving_to_blip = True

        self.update_widget_states()


    def drive_to_marker(self):
        if not self.gta_sa:
            return
        
        if self.is_driving_to_blip:
            self.is_driving_to_blip = False

        if self.is_circuit:
            self.is_circuit = False
            self.is_circuit_boolvar.set(False)

        if self.autodriver:
            self.stop_autodriver()
        
        nodes_data = load_json(NODES_DATA_JSON)
        start_node = PathNode.get_closest_node_to_pos(nodes_data, GameData.player_pos)
        target_node = PathNode.get_closest_node_to_pos(nodes_data, GameData.marker_pos)

        self.solved_path = pathfind_dijkstra(nodes_data, start_node, target_node)
        self.draw_solved_path()

        # Start driving with the current solved path
        self.autodriver = Autodriver(self.solved_path)
        self.autodriver.start_driving(self.is_circuit)

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
        if GameData.gta_sa == None:
            return
        
        if self.player_marker:
            self.canvas.delete(self.player_marker)

        player_position = GameData.player_pos
        player_position_to_image_pos = ingame_to_image_coords(player_position, self.map_img_resized)

        player_orientation = GameData.player_angle_radians
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


    def set_guider_position(self, event):
        clicked_pos = Vector2(event.x, event.y)
        clicked_pos_v3 = Vector3(clicked_pos.x, 0, clicked_pos.y)

        guiding_markers_index = len(self.guiding_markers)
        self.guiding_markers.append(GuidingMarker(
            self.canvas.create_oval(clicked_pos.x - self.marker_size, clicked_pos.y - self.marker_size,
                                                 clicked_pos.x + self.marker_size, clicked_pos.y + self.marker_size,
                                                 fill='blue'),
            image_to_ingame_coords(clicked_pos_v3, self.map_img_resized)   
        ))

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


    def checkbuttons_update(self):
        # Blip Autodrive
        if self.blip_autodrive_boolvar.get():
            self.blip_autodrive = True
        else:
            self.blip_autodrive = False

        # Marker Autodrive
        if self.marker_autodrive_boolvar.get():
            self.marker_autodrive = True
        else:
            self.marker_autodrive = False

        # Is Circuit
        if self.is_circuit_boolvar.get():
            self.is_circuit = True
        else:
            self.is_circuit = False

        self.update_widget_states()


    def drive_path(self):
        if self.solved_path:
            # If Autodriver exists and is paused resume it else create new instance and start driving
            if self.autodriver:
                if self.autodriver.is_paused:
                    self.autodriver.pause_driving(False)

                    self.update_widget_states()
                return
            
            self.autodriver = Autodriver(self.solved_path)
            self.autodriver.start_driving(self.is_circuit)

            self.blip_autodrive_boolvar.set(False)
            self.marker_autodrive_boolvar.set(False)
            self.update_widget_states()


    def pause_autodriver(self):
        if not self.autodriver._instance.is_paused:
            self.autodriver.pause_driving(True)
        else:
            self.autodriver.pause_driving(False)

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

        # Connect start and end node if circuit
        if self.is_circuit:
            start_node_pos = self.solved_path[0].position
            end_node_pos = self.solved_path[len(self.solved_path)-1].position
            start_node_pos_to_image = ingame_to_image_coords(start_node_pos, self.map_img_resized)
            end_node_pos_to_image = ingame_to_image_coords(end_node_pos, self.map_img_resized)

            path_line_id = self.canvas.create_line(start_node_pos_to_image.x, start_node_pos_to_image.z,
                                                                end_node_pos_to_image.x, end_node_pos_to_image.z,
                                                                width=2, fill='orange')
            
            self.path_line_ids[str(len(self.path_line_ids))] = path_line_id


    def compute_button(self):
        nodes_data = load_json(NODES_DATA_JSON)

        closest_node_to_start_marker = PathNode.get_closest_node_to_pos(nodes_data, self.start_marker_position_ingame)
        closest_node_to_end_marker = PathNode.get_closest_node_to_pos(nodes_data, self.end_marker_position_ingame)

        self.solved_path = []
        if self.guiding_markers:
            last_guider_node = None
            for i, guider in enumerate(self.guiding_markers):
                cur_guider_node = PathNode.get_closest_node_to_pos(nodes_data, guider.ingame_pos)

                # If first guider
                if i == 0:
                    solved_path_segment = pathfind_dijkstra(nodes_data, closest_node_to_start_marker, cur_guider_node)
                    self.solved_path.extend(solved_path_segment[:-1])

                    last_guider_node = cur_guider_node

                    continue
                
                solved_path_segment = pathfind_dijkstra(nodes_data, last_guider_node, cur_guider_node)
                last_guider_node = cur_guider_node

                self.solved_path.extend(solved_path_segment[:-1])

            # Last guider
            solved_path_segment = pathfind_dijkstra(nodes_data, last_guider_node, closest_node_to_end_marker)
            self.solved_path.extend(solved_path_segment[:-1])

        else:
            self.solved_path = pathfind_dijkstra(nodes_data, closest_node_to_start_marker, closest_node_to_end_marker)
        
        # If circuit
        if self.is_circuit:
            solved_path_segment = pathfind_dijkstra(nodes_data, closest_node_to_end_marker, closest_node_to_start_marker)
            self.solved_path.extend(solved_path_segment[:-1])

        self.draw_solved_path()

        self.update_widget_states()
        

    def clear_canvas(self):
        if self.start_marker:
            self.canvas.delete(self.start_marker)
            self.start_marker = None

        if self.end_marker:
            self.canvas.delete(self.end_marker)
            self.end_marker = None

        if self.guiding_markers:
            for marker in self.guiding_markers:
                self.canvas.delete(marker.canvas_id)
            self.guiding_markers = []

        if self.path_line_ids:
            for path_line_id in self.path_line_ids.values():
                self.canvas.delete(path_line_id)

            self.path_line_ids = {}

        if self.solved_path:
            self.solved_path = []

        self.update_widget_states()


    def update_widget_states(self):
        # Check 'run' button if it can be enabled
        if hasattr(self, 'button_drive'):
            self.button_drive.config(state=DISABLED)
            if GameData.gta_sa:
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
            if self.start_marker or self.end_marker or self.guiding_markers or self.solved_path:
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

        # Check 'is_circuit' checkbutton if it can be enabled
        if hasattr(self, 'checkbutton_is_circuit'):
            self.checkbutton_is_circuit.config(state=NORMAL)
            if self.solved_path:
                self.checkbutton_is_circuit.config(state=DISABLED)


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
