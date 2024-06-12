import sys, os
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resources.utils.file_paths import MAP_IMG_PATH, NODES_DATA_JSON
from resources.utils.vectors import Vector2, Vector3
from resources.utils.map_conversions import image_to_ingame_coords, ingame_to_image_coords
from resources.utils.nodes_classes import PathNode
from resources.utils.json_utils import load_json
from resources.utils.pathfinding.Dijkstra import pathfind_dijkstra



class MainGUI():
    map_img_resized = Image.open(MAP_IMG_PATH).resize((512, 512), Image.Resampling.LANCZOS)
    marker_size = 4 # start/end marker

    theme_dark = {
        'bg': '#333333',
        'menu_bg': '#262626',
        'text_color': '#c5c5c5',
        'button_bg': '#262626',
        'button_border': '#1a9ef7'
    }

    def __init__(self):
        # Define root
        self.root = Tk()

        self.start_marker = None
        self.end_marker = None

        self.start_marker_position_ingame = None
        self.end_marker_position_ingame = None

        self.path_line_ids = {}

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
        under_map_label = Label(text='LMB = Start Marker | RMB = End Marker', pady=10)

        # Buttons
        self.button_run = Button(self.root, text='Run', width=10, height=2, command=self.run_button)
        self.button_compute = Button(self.root, text='Compute Path', width=10, height=2, command=self.compute_button)
        self.button_clear = Button(self.root, text='Clear Start/End', width=10, height=2, command=self.clear_button)

        # Grid
        self.canvas.grid(row=0, column=0, columnspan=3, pady=10, padx=10)

        under_map_label.grid(column=0, row=1, columnspan=3)

        self.button_run.grid(column=0, row=2, pady=10, padx=0, sticky='ew')
        self.button_compute.grid(column=1, row=2, pady=10, padx=0, sticky='ew')
        self.button_clear.grid(column=2, row=2, pady=10, padx=0, sticky='ew')

        # Checks
        self.update_button_states()

        # Theme
        self.change_theme(self.theme_dark)

        self.root.mainloop()
    

    def set_start_position(self, event):
        clicked_pos = Vector2(event.x, event.y)
        self.start_marker_position_ingame = image_to_ingame_coords(clicked_pos, self.map_img_resized)

        if self.start_marker != None:
            self.canvas.delete(self.start_marker)

        self.start_marker = self.canvas.create_oval(clicked_pos.x - self.marker_size, clicked_pos.y - self.marker_size,
                                                    clicked_pos.x + self.marker_size, clicked_pos.y + self.marker_size,
                                                    fill='green')
        
        self.update_button_states()


    def set_end_position(self, event):
        clicked_pos = Vector2(event.x, event.y)
        self.end_marker_position_ingame = image_to_ingame_coords(clicked_pos, self.map_img_resized)

        if self.end_marker != None:
            self.canvas.delete(self.end_marker)

        self.end_marker = self.canvas.create_oval(clicked_pos.x - self.marker_size, clicked_pos.y - self.marker_size,
                                                    clicked_pos.x + self.marker_size, clicked_pos.y + self.marker_size,
                                                    fill='red')
        
        self.update_button_states()
    

    def change_theme(self, theme):
        self.root.config(bg=theme['bg'])

        # Apply to widgets
        for widget in self.root.winfo_children():
            widget_type = widget.winfo_class()

            if widget_type == 'Menu':
                widget.configure(bg=theme['menu_bg'])
            elif widget_type == 'Label':
                widget.configure(bg=theme['bg'], fg=theme['text_color'])
            elif widget_type == 'Button':
                widget.configure(bg=theme['button_bg'], fg=theme['text_color'], bd=2)
            elif widget_type == 'Canvas':
                widget.configure(bg=theme['bg'], highlightthickness=0)


    def run_button(self):
        pass

    
    def compute_button(self):
        nodes_data = load_json(NODES_DATA_JSON)

        closest_node_to_start_marker = PathNode.get_closest_node_to_pos(nodes_data, self.start_marker_position_ingame)
        closest_node_to_end_marker = PathNode.get_closest_node_to_pos(nodes_data, self.end_marker_position_ingame)

        solved_path = pathfind_dijkstra(nodes_data, closest_node_to_start_marker, closest_node_to_end_marker)

        # Delete old path markers from canvas if existing
        if self.path_line_ids:
            for path_line_id in self.path_line_ids.values():
                self.canvas.delete(path_line_id)
            
            self.path_line_ids = {} # Set dict as empty for the next part (Draw new path markers on canvas)

        # Draw new path markers on canvas
        for i, node in enumerate(solved_path):
            node_pos = Vector2(node.position.x, node.position.z)
            node_pos_to_image = ingame_to_image_coords(node_pos, self.map_img_resized)
            
            # Draw path line if 'node' isnt last one in solved_path
            if i != len(solved_path)-1:
                next_node = solved_path[i+1]
                next_node_pos = Vector2(next_node.position.x, next_node.position.z)
                next_node_pos_to_image = ingame_to_image_coords(next_node_pos, self.map_img_resized)

                path_line_id = self.canvas.create_line(node_pos_to_image.x, node_pos_to_image.y,
                                                                next_node_pos_to_image.x, next_node_pos_to_image.y,
                                                                width=2, fill='orange')

            # Store 
            self.path_line_ids[i] = path_line_id


    def update_button_states(self):
        # Check 'compute' button if it can be enabled or not
        self.button_compute.config(state=NORMAL)
        if self.start_marker == None or self.end_marker == None:
            self.button_compute.config(state=DISABLED)


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

        self.update_button_states()



if __name__ == '__main__':
    gui = MainGUI()

    gui.display_main()
