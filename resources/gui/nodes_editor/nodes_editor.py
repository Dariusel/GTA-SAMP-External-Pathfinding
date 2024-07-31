from tkinter import *
from tkinter import font
from PIL import ImageTk, Image
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from resources.utils.file_paths import NODES_DATA_JSON, MAP_IMG_PATH, SOUNDS_DIR
from resources.utils.json_utils import save_json, load_json
from resources.utils.nodes_classes import PathNode
from resources.gui.nodes_editor.utils.utils import (
    get_canvas_crop_bbox, get_zoomed_image_clicked_position, get_zoomed_image_xy_canvas_position, calculate_player_polygon,
    is_inside_bbox_2d)
from resources.utils.map_conversions import ingame_to_image_coords, image_to_ingame_coords
from resources.gui.utils.utils import change_theme, Themes
from resources.utils.vectors import *
from resources.utils.memory.memory_variables import GameData
from resources.utils.sound_manager import play_sound


class NodesEditor():
    _instance = None


    def __init__(self, parent) -> None:
        if NodesEditor._instance:
            return
        
        NodesEditor._instance = self

        self.parent = parent

        # Nodes
        self.nodes_json = load_json(NODES_DATA_JSON)
        self.segment_selected_nodes = {}
        self.new_nodes = {}
        self.new_node_min_spacing = 1 # Minimum distance required between newly created nodes to prevent accidental overlap.
        self.modified_nodes = {}

        self.marker_ids = {} # For canvas

        self.selected_node = None

        # Canvas
        self.canvas_size = 512

        self.map_img_full = Image.open(MAP_IMG_PATH)

        self.target_resolution = {
            1: self.map_img_full.resize((768,768), Image.Resampling.LANCZOS),
            3: self.map_img_full.resize((1256,1256), Image.Resampling.LANCZOS),
            4.5: self.map_img_full.resize((2000,2000), Image.Resampling.LANCZOS),
            8: self.map_img_full.resize((3200,3200), Image.Resampling.LANCZOS),
            16: self.map_img_full.resize((4500,4500), Image.Resampling.LANCZOS),
            30: self.map_img_full.resize((6144,6144), Image.Resampling.LANCZOS),
        }
        self.cur_img = self.target_resolution[1]
        self.map_crop_bbox = (0, 0, 768, 768)

        self.zoom_scale = 1

        self.player_marker = None

        # Misc
        self.loaded_window = False

        self.init_window()

    
    def init_window(self):
        self.root = Toplevel(self.parent)
        self.root.title('Nodes Editor')
        self.root.resizable(0, 0)  # Disable resizing

        # Create widgets
        self.create_canvas()
        self.create_buttons()
        self.create_labels()

        # Grid layout
        self.grid_widgets()

        # Misc
        self.update_canvas()

        # Theme
        change_theme(self.root, Themes.theme_dark)

        # Misc
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.loaded_window = True

        self.root.mainloop()


    def create_canvas(self):
        # Create it
        self.canvas = Canvas(self.root, width=self.canvas_size, height=self.canvas_size)

        # Load and display the map image
        self.map_img_resized = self.map_img_full.resize((self.canvas_size, self.canvas_size), Image.Resampling.LANCZOS)
        self.map_img_tk = ImageTk.PhotoImage(self.map_img_resized)
        self.map_img_id = self.canvas.create_image(0, 0, image=self.map_img_tk, anchor='nw')

        # Events
        self.canvas.bind('<MouseWheel>', self.canvas_zoom) # Zoom In/Zoom Out
        self.canvas.bind('<Button-1>', self.node_click) # idk
        self.canvas.bind('<Button-2>', self.display_segment) # Display segment


    def create_buttons(self):
        self.new_node_at_player_button = Button(self.root, text='New Node at Player', width=20, height=2, command=self.node_at_player_pos)
        self.apply_button = Button(self.root, text='Apply', width=20, height=2, command=self.apply)


    def create_labels(self):
        from resources.utils.keybinds_manager import NODES_EDITOR_NODE_AT_POSITION, key_to_str

        labels_font=font.Font(family="Segoe UI", weight="bold")

        self.header_label = Label(self.root, text='Nodes Editor Menu', font=labels_font)
        self.under_map_label = Label(self.root, text='Scroll = Zoom', font=labels_font)

        node_at_player_pos_keybind_text = f'<{' + '.join(key_to_str(key) for key in NODES_EDITOR_NODE_AT_POSITION)}>'
        self.node_at_player_pos_keybind_label = Label(self.root, text=node_at_player_pos_keybind_text)


    def grid_widgets(self):
        # Grid layout
        self.canvas.grid(column=0, row=0, rowspan=10, padx=10, pady=10)
        self.under_map_label.grid(column=0, row=11, padx=10, pady=(0,10))

        self.header_label.grid(column=1, row=0, columnspan=2, padx=100, pady=10)

        self.new_node_at_player_button.grid(column=1, row=1, padx=10, pady=(10,5))
        self.node_at_player_pos_keybind_label.grid(column=1, row=2, padx=10, pady=(5,10))

        self.apply_button.grid(column=2, row=11, padx=10, pady=10)


    def on_close(self):
        from resources.gui.gui_main import MainGUI

        MainGUI._instance.nodes_editor = None

        NodesEditor._instance = None
        self.root.destroy()


    def display_segment(self, event):
        img_size = self.cur_img.size[0]

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        zoomed_pos = get_zoomed_image_clicked_position(x, y, img_size, self.map_crop_bbox, self.zoom_scale)
        ingame_click_pos = image_to_ingame_coords(zoomed_pos, self.cur_img)
        
        click_area_id = PathNode.get_closest_node_to_pos(self.nodes_json, ingame_click_pos).area_id


        for node in self.nodes_json.values():
            node_obj = PathNode.from_dict(node)
            
            if node_obj.area_id == click_area_id or node_obj.area_id == -1:
                if str(node_obj.node_id) in self.segment_selected_nodes:
                    continue
                
                # Add to segment_selected_nodes list
                self.segment_selected_nodes[str(node_obj.node_id)] = node


        self.update_canvas()
        

    def node_click(self, event):
        img_size = self.cur_img.size[0]

        x, y = event.x, event.y

        zoomed_pos = get_zoomed_image_clicked_position(x, y, img_size, self.map_crop_bbox, self.zoom_scale)
        ingame_click_pos = image_to_ingame_coords(zoomed_pos, self.cur_img)
        
        clicked_node_from_segment_selected_nodes = PathNode.get_closest_node_to_pos(self.segment_selected_nodes, ingame_click_pos)
        clicked_node_from_new_nodes = PathNode.get_closest_node_to_pos(self.new_nodes, ingame_click_pos)

        distance_to_selected = float('inf')
        distance_to_new = float('inf')
        if clicked_node_from_segment_selected_nodes:
            distance_to_selected = Vector3.distance(clicked_node_from_segment_selected_nodes.position, ingame_click_pos)
        if clicked_node_from_new_nodes:
            distance_to_new = Vector3.distance(clicked_node_from_new_nodes.position, ingame_click_pos)

        clicked_node = clicked_node_from_segment_selected_nodes if distance_to_selected < distance_to_new else clicked_node_from_new_nodes

        distance_to_clicked_node = float('inf')
        if clicked_node:
            distance_to_clicked_node = Vector3.distance(clicked_node.position, ingame_click_pos)

        # If distance from click position to clicked node is more than (X units), unassign clicked_node so you dont press on a side of the canvas and select something from the totally opposite side
        clicked_node = clicked_node if distance_to_clicked_node < 100 else None
        
        if not clicked_node:
            return
        
        self.selected_node = clicked_node

        self.update_canvas()
        

    def node_at_player_pos(self):
        if not GameData.gta_sa:
            return
        
        closest_node_to_new = PathNode.get_closest_node_to_pos(self.new_nodes, GameData.player_pos)
        distance_to_closest_node = float('inf')
        if closest_node_to_new:
            distance_to_closest_node = Vector3.distance(GameData.player_pos, closest_node_to_new.position)
        
        if distance_to_closest_node < self.new_node_min_spacing:
            return
        
        # Create new node
        new_node_pos = GameData.player_pos
        adj_nodes = {}
        new_node_id = len(self.nodes_json) + len(self.new_nodes)
        new_area_id = -1
        node_type = 1 # Default 1 for cars
        flags = 0
        optional = {
            'player_created': True,
            'player_modified': True
        }
        new_node = PathNode(new_node_pos, adj_nodes, new_node_id, new_area_id, node_type, flags, optional)
        
        # Add it to new_nodes and modified_nodes
        self.new_nodes[new_node_id] = new_node.to_dict()
        self.modified_nodes[new_node_id] = new_node.to_dict()

        play_sound(os.path.join(SOUNDS_DIR, 'interact.wav'))

        self.render_nodes(self.new_nodes, '#00D4FF', 2)


    def apply(self):
        pass


    def canvas_zoom(self, event):
        x = event.x
        y = event.y
        
        last_zoom_scale = self.zoom_scale
        # Determine zoom direction and adjust scale
        if event.delta > 0:
            self.zoom_scale *= 1.1  # Zoom In
        else:
            self.zoom_scale /= 1.1  # Zoom Out

        # Clamp zoom scale within specified limits
        self.zoom_scale = min(max(self.zoom_scale, 1), 40)

        # Find the closest target resolution based on zoom scale
        last_img_size = self.cur_img.size[0]
        closest_zoom = min(self.target_resolution.keys(), key=lambda z: abs(self.zoom_scale - z))
        cur_target_image = self.target_resolution[closest_zoom]

        # Calculate cropped image coordinates
        self.cur_img = cur_target_image
        last_map_crop_bbox = self.map_crop_bbox
        self.map_crop_bbox = get_canvas_crop_bbox(self.cur_img.size[0], last_img_size, x, y, last_map_crop_bbox, self.zoom_scale, last_zoom_scale)

        # Crop and resize the image
        self.map_img_cropped = cur_target_image.crop(self.map_crop_bbox).resize((512, 512), Image.LANCZOS)

        # Update the displayed image on the canvas
        self.map_img_tk = ImageTk.PhotoImage(self.map_img_cropped)
        self.canvas.itemconfig(self.map_img_id, image=self.map_img_tk)

        # Lower the image to the background
        self.canvas.lower(self.map_img_id)

        # Print debug information
        #print(f'Zoom Scale: {self.zoom_scale} -> Image Size: {self.cur_img.size[0]} -> Crop: {self.cur_img.size[0]/self.zoom_scale}')
        # print(f'Crop Coordinates: ({x1}, {y1}, {x2}, {y2})')

        self.update_canvas()


    def update_canvas(self):
        marker_size = 2
        img_size = self.cur_img.size[0]

        # Update player marker on map
        if GameData.gta_sa:
            # Remove previous marker to create new one
            if self.player_marker:
                self.canvas.delete(self.player_marker)

            player_on_image_pos = ingame_to_image_coords(GameData.player_pos, img_size)
            player_on_image_pos = get_zoomed_image_xy_canvas_position(player_on_image_pos.x, player_on_image_pos.z,
                                                                      img_size, self.canvas_size,
                                                                      self.map_crop_bbox,
                                                                      self.zoom_scale)
            
            player_polygon = calculate_player_polygon(10,
                                                      player_on_image_pos,
                                                      math.degrees(GameData.player_angle_radians))
            
            self.player_marker = self.canvas.create_polygon(player_polygon, fill='#FF00EC')
        elif self.player_marker:
            self.canvas.delete(self.player_marker)
        
        # Transform each node in selected nodes to canvas position and update it
        self.render_nodes(self.segment_selected_nodes, 'grey', marker_size)

        # New Nodes -||-
        self.render_nodes(self.new_nodes, '#00D4FF', marker_size)

        # Selected Node
        if self.selected_node:
            # Delete previous marker before creating new one if previous marker exists # Delete previous marker before creating new one if previous marker exists
            node_id_str = str(self.selected_node.node_id)
            if node_id_str in self.marker_ids:
                self.canvas.delete(self.marker_ids[node_id_str])

            # Convert ingame node position to cropped and zoomed canvas position
            node_on_canvas_pos = ingame_to_image_coords(self.selected_node.position, img_size)
            node_on_canvas_pos = get_zoomed_image_xy_canvas_position(node_on_canvas_pos.x, node_on_canvas_pos.z, img_size, self.canvas_size, self.map_crop_bbox, self.zoom_scale)

            # Display on canvas
            marker_id = self.canvas.create_oval(node_on_canvas_pos.x - marker_size, node_on_canvas_pos.z - marker_size,
                                                node_on_canvas_pos.x + marker_size, node_on_canvas_pos.z + marker_size,
                                                fill='#04FF00')
            
            self.marker_ids[node_id_str] = marker_id
            

    def render_nodes(self, nodes, color: str, marker_size: float):
        img_size = self.cur_img.size[0]

        bbox_corner_1_ingame = image_to_ingame_coords(Vector3(self.map_crop_bbox[0], 0, self.map_crop_bbox[1]),
                                                      img_size)
        bbox_corner_2_ingame = image_to_ingame_coords(Vector3(self.map_crop_bbox[2], 0, self.map_crop_bbox[3]),
                                                      img_size)
        crop_bbox_ingame = [bbox_corner_1_ingame.x, bbox_corner_1_ingame.z, bbox_corner_2_ingame.x, bbox_corner_2_ingame.z]

        for node in nodes.values():
            node_obj = PathNode.from_dict(node)

            node_pos = node_obj.position

            # Delete previous marker before creating new one if previous marker exists
            node_id_str = str(node_obj.node_id)
            if node_id_str in self.marker_ids:
                self.canvas.delete(self.marker_ids[node_id_str])

            # Check if node is in canvas crop bbox and if it is stop rendering it
            if not is_inside_bbox_2d(Vector2(node_pos.x, node_pos.z), crop_bbox_ingame):
                continue


            # Convert ingame node position to cropped and zoomed canvas position
            node_on_canvas_pos = ingame_to_image_coords(node_pos, img_size)
            node_on_canvas_pos = get_zoomed_image_xy_canvas_position(node_on_canvas_pos.x, node_on_canvas_pos.z, img_size, self.canvas_size, self.map_crop_bbox, self.zoom_scale)

            # Display on canvas
            marker_id = self.canvas.create_oval(node_on_canvas_pos.x - marker_size, node_on_canvas_pos.z - marker_size,
                                                node_on_canvas_pos.x + marker_size, node_on_canvas_pos.z + marker_size,
                                                fill=color)
            
            # Update marker id
            self.marker_ids[node_id_str] = marker_id






        



if __name__ == '__main__':
    NodesEditor()