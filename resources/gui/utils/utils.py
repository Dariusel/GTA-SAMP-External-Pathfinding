class Themes():
    theme_dark = {
        'bg': '#333333',
        'menu_bg': '#262626',
        'text_color': '#c5c5c5',
        'button_bg': '#262626',
        'button_border': '#1a9ef7'
    }

    

def change_theme(root, theme):
        root.config(bg=theme['bg'])

        # Apply to widgets
        for widget in root.winfo_children():
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