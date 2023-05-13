import json
import sys
import yaml
import typing
import functools
import webbrowser
import tkscrolledframe as tksf

import tkinter as tk
import tkinter.filedialog as tkfd
import PIL.Image as PILImage


class WidgetRow(typing.NamedTuple):
    wingets_id: int
    bundles_id: int
    row_l: tk.Label
    row_entry: tk.Entry
    col_l: tk.Label
    col_entry: tk.Entry
    img_path: tk.Entry
    x_l: tk.Label
    x_entry: tk.Entry
    y_l: tk.Label
    y_entry: tk.Entry
    pop: tk.Button
    frames_l: tk.Label
    frames_entry: tk.Entry



class Window:
    root = tk.Tk()

    def __init__(self):
        Window.root.title("Sprite sheet Packer")
        Window.root.geometry("1280x680")
        Window.root.resizable(width=True, height=True)

        try:
            Window.root.iconbitmap('./ssm2.ico') # type: ignore
        except Exception as e:
            print(e)

        sf = tksf.ScrolledFrame(Window.root, width=680, height=680)
        sf.pack(side=tk.TOP ,expand=1, fill=tk.BOTH)

        self.inner_frame = typing.cast(tk.Frame, sf.display_widget(tk.Frame)) # type: ignore
        self.offset = 0
        self.widgets_row: dict[int, dict[int, WidgetRow]] = dict(dict())
        self.wingets_unique_id = 0
        self.total_width_of_save_image = 0
        self.total_height_of_save_image = 0
        self.max_row_height: list[int] = []

        self.add_multi = tk.Button(self.inner_frame, text="Add images", command=self.add_rows)
        self.update = tk.Button(self.inner_frame, text="Update", command=self.update_cells)
        self.save = tk.Button(self.inner_frame, text="Save image!", command=lambda: save_image(self))
        self.save_yaml_json = tk.Button(self.inner_frame, text="Export yaml or json!", command=lambda: save_yaml_or_json(self))
        self.view = tk.Button(self.inner_frame, text="View", command=lambda: view_image(self))
        self.autoupdate_int = tk.IntVar()
        self.auto_update_checkbox = tk.Checkbutton(self.inner_frame, text="auto update", variable=self.autoupdate_int)
        self.show_top_and_bottom_line = tk.IntVar()
        self.show_top_and_bottom_line_checkbox = tk.Checkbutton(self.inner_frame, text="Show top(blue) and bottom(red) borders", variable=self.show_top_and_bottom_line)

        # list_items = tk.Variable(value=self.max_row_height)
        self.list_of_row_max_y = tk.Listbox(self.inner_frame, width=10, height=5, state=tk.DISABLED, exportselection=False) # listvariable=list_items
        self.list_of_row_max_y.bind("<<ListboxSelect>>", lambda event: onselect(event, self.max_row_height, (Window.root.winfo_x() + Window.root.winfo_width()) // 2, (Window.root.winfo_y() + Window.root.winfo_height()) // 2))
        self.overide_col_heights = tk.IntVar()
        self.overide_col_heights_checkbox = tk.Checkbutton(self.inner_frame, text="Overide images y(height) with values of the table", variable=self.overide_col_heights)

        self.add_multi.grid(row=self.offset, column=0, columnspan=2)
        self.update.grid(row=self.offset, column=4, columnspan=2)
        self.auto_update_checkbox.grid(row=self.offset, column=6, columnspan=3)
        self.show_top_and_bottom_line_checkbox.grid(row=self.offset, column=10, columnspan=10)

        self.save.grid(row=self.offset + 1, column=0, columnspan=2)
        self.save_yaml_json.grid(row=self.offset + 1, column=4, columnspan=2)
        self.view.grid(row=self.offset + 1, column=8, columnspan=4)
        self.list_of_row_max_y.grid(row=self.offset+2, column=0, columnspan=4)
        self.overide_col_heights_checkbox.grid(row=self.offset+3, column=0, columnspan=5)

        begining_menu_bar(Window.root, self)

        bottom_stripe = tk.Label(Window.root, text='http://www.paypal.me/', relief=tk.SUNKEN, anchor=tk.W, fg='blue')
        bottom_stripe.bind("<Button-1>", lambda _: webbrowser.open_new("http://www.paypal.me/JikoUnderscore/1"))
        bottom_stripe.place(anchor=tk.S, relx=0.50, rely=1, relwidth=1)


    def update_buttons_locatons(self):
        self.offset += 1
        self.add_multi.grid(row=self.offset , column=0, columnspan=2)
        self.update.grid(row=self.offset , column=4, columnspan=2)
        self.auto_update_checkbox.grid(row=self.offset , column=6, columnspan=3)
        self.show_top_and_bottom_line_checkbox.grid(row=self.offset, column=10, columnspan=10)

        self.save.grid(row=self.offset + 1, column=0, columnspan=2)
        self.save_yaml_json.grid(row=self.offset + 1, column=4, columnspan=2)
        self.view.grid(row=self.offset + 1, column=8, columnspan=2)
        self.list_of_row_max_y.grid(row=self.offset+2, column=0, columnspan=4)
        self.overide_col_heights_checkbox.grid(row=self.offset+3, column=0, columnspan=5)


    def remove_row(self, wingets_unique_id: int, bundles_id: int):
        for wig in  self.widgets_row[wingets_unique_id][bundles_id]:
            if not isinstance(wig, int) :
                wig.destroy()

        del self.widgets_row[wingets_unique_id][bundles_id]
        self.offset -= 1


    def add_rows(self):
        frame_files = tkfd.askopenfilenames(title="Choose a file")

        bundles_id = 0
        self.widgets_row[self.wingets_unique_id] = {}
        for path in frame_files:
            file_name = path.split(r"/")[-1]

            first_number = len(file_name)
            for i, n in enumerate(file_name):
                if n.isdigit():
                    first_number = i
                    break

            row_set_all_wigets(self, str(self.wingets_unique_id), str(bundles_id), path, "0", "0", self.wingets_unique_id, bundles_id, f"{file_name[:first_number]}_n{self.wingets_unique_id}")
            bundles_id += 1
            self.update_buttons_locatons()

        self.wingets_unique_id += 1


    def update_cells(self):
        if not self.widgets_row:
            return
        self.total_width_of_save_image = 0
        self.total_height_of_save_image = 0
        self.max_row_height.clear()

        for i, bundle in enumerate(self.widgets_row.values()):
            self.max_row_height.append(0)
            for row in bundle.values():
                row_pos = int(row.row_entry.get())
                col_pos = int(row.col_entry.get())

                image_path: str = row.img_path.get()

                image = PILImage.open(image_path)
                width, height = image.size
                image.close()

                last_height = self.max_row_height[i]
                self.max_row_height[i] = max(last_height, height)

                y = sum(self.max_row_height[0:row_pos]) if row_pos >= 1 else row_pos * height

                row.x_entry.delete(0, tk.END)
                row.x_entry.insert(0, str(col_pos * width))

                row.y_entry.delete(0, tk.END)
                row.y_entry.insert(0, str(y))

                h = int(row.y_entry.get()) + height
                w = int(row.x_entry.get()) + width

                if h > self.total_height_of_save_image:
                    self.total_height_of_save_image = h
                if w > self.total_width_of_save_image:
                    self.total_width_of_save_image = w

        items_string = [str(s) for s in self.max_row_height]
        self.list_of_row_max_y.config(state=tk.NORMAL)
        self.list_of_row_max_y.delete(0,tk.END)
        self.list_of_row_max_y.config(height=len(items_string) + 1)
        for i, s in enumerate(items_string):
            self.list_of_row_max_y.insert(i, s)



def onselect(event: "tk.Event[tk.Listbox]", max_row_height: list[int], top_level_offset_x: int, top_level_offset_y: int):
    wiget = event.widget

    enter_window = tk.Toplevel()
    enter_window.geometry(f"300x100+{top_level_offset_x}+{top_level_offset_y}")
    tk.Label(enter_window, text="Enter the new value and close the window.").pack()

    entry = tk.Entry(enter_window)
    entry.focus()
    entry.pack()

    index = typing.cast(tuple[int], wiget.curselection()) # type: ignore
    data = typing.cast(str, wiget.get(index[0])) # type: ignore
    event.widget.config(state=tk.DISABLED)
    # event.widget.focus_set()
    entry.insert(0, data)


    def enter_window_destroy():
        event.widget.config(state=tk.NORMAL)
        wiget.delete(index[0])
        wiget.insert(index[0], entry.get())
        max_row_height[index[0]] = int(entry.get())
        enter_window.destroy()

    enter_window.protocol("WM_DELETE_WINDOW", enter_window_destroy)
    enter_window.mainloop()


def row_set_all_wigets(w: Window, row_n: str, col_n: str, path: str, x_n: str, y_n: str, wingets_unique_id: int, bundles_id: int, name_f: str):
        row_l = tk.Label(w.inner_frame, text="row")
        image_row = tk.Entry(w.inner_frame, width=5)
        image_row.insert(0, row_n)
        row_l.grid(row=w.offset, column=0)
        image_row.grid(row=w.offset, column=1)

        col_l = tk.Label(w.inner_frame, text="col")
        image_col = tk.Entry(w.inner_frame, width=5)
        image_col.insert(0, col_n)
        col_l.grid(row=w.offset, column=2)
        image_col.grid(row=w.offset, column=3)

        image_path = tk.Entry(w.inner_frame, width=len(path))
        image_path.insert(0, path)
        image_path.grid(row=w.offset, column=4, columnspan=3)

        x_l = tk.Label(w.inner_frame, text="x")
        x = tk.Entry(w.inner_frame, width=5)
        x.insert(0, x_n)
        x_l.grid(row=w.offset, column=8)
        x.grid(row=w.offset, column=9)

        y_l = tk.Label(w.inner_frame, text="y")
        y = tk.Entry(w.inner_frame, width=5)
        y.insert(0, y_n)
        y_l.grid(row=w.offset, column=11)
        y.grid(row=w.offset, column=12)


        pop_b = tk.Button(w.inner_frame, text="pop", command=functools.partial(w.remove_row, wingets_unique_id, bundles_id), font=('Helvetica', '7'), width=5)
        pop_b.grid(row=w.offset, column=14)

        frames_l = tk.Label(w.inner_frame, text="frames")
        frame_name = tk.Entry(w.inner_frame, width=30)
        frame_name.insert(0, name_f)
        frames_l.grid(row=w.offset, column=15)
        frame_name.grid(row=w.offset, column=16)

        w.widgets_row[wingets_unique_id][bundles_id] = WidgetRow(w.wingets_unique_id, bundles_id, row_l, image_row, col_l, image_col, image_path, x_l, x, y_l, y, pop_b, frames_l, frame_name)




def view_image(w: Window):
    if not w.widgets_row:
        return
    new_image = proses_image(w)
    new_image.show()


    # fotoimg =  ImageTk.PhotoImage(proses_image(w))
    # image_window = tk.Toplevel(Window.root)
    # image_window.title("The Rules")
    # image_window.geometry(f"{w.total_width_of_save_image*2}x{w.total_height_of_save_image*2}")

    # # rule_window.pack()
    # # the_rules = tk.Label(rule_window, text="Here are the rules...", foreground="black")
    # # the_rules.grid(row=0, column=0, columnspan=3)

    # # file_format = 'png' # The file extension of the sourced data
    # canvas = tk.Canvas(image_window, width=w.total_width_of_save_image, height=w.total_height_of_save_image, bg="white")
    # canvas.pack()
    # canvas.create_image(0, 0, anchor=tk.NW, image=fotoimg) # type: ignore
    # # canvas.create_rectangle(0, 0, 300, 300, fill="red")
    # # canvas.bind("<MouseWheel>", lambda e: do_zoom(e, canvas))
    # canvas.bind('<ButtonPress-1>', lambda event: canvas.scan_mark(event.x, event.y)) # type: ignore
    # canvas.bind("<B1-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1)) # type: ignore


    # image_window.mainloop()


def proses_image(w: Window) -> PILImage.Image:
    if w.autoupdate_int.get():
        w.update_cells()

    if w.total_height_of_save_image == 0 or w.total_width_of_save_image == 0:
        w.update_cells()

    new_output_image = PILImage.new('RGBA', (w.total_width_of_save_image, w.total_height_of_save_image))
    # new_output_image = pilimage.alpha_composite(pilimage.new("RGBA", (w.total_width_of_save_image, w.total_height_of_save_image)), new_output_image.convert("RGBA"))

    for i, bundle in enumerate(w.widgets_row.values()):
        for row in bundle.values():
            img: str = row.img_path.get()

            one_sprite = PILImage.open(img).convert("RGBA")
            width, height = one_sprite.size


            if w.show_top_and_bottom_line.get():
                for x in range(width):
                    pixl = typing.cast(int, one_sprite.getpixel((x, height-1))) # type: ignore
                    if pixl != 0:
                        one_sprite.putpixel((x, height-1), (255,0,0))
                for xx in range(width):
                    pixl = typing.cast(int ,one_sprite.getpixel((xx-1, 0))) # type: ignore
                    if pixl != 0:
                        one_sprite.putpixel((xx, 0), (0,0,255))


            y_pos = sum(w.max_row_height[:i] ) if w.overide_col_heights.get() else int(row.y_entry.get())
            new_output_image.paste(one_sprite, (int(row.x_entry.get()), y_pos), one_sprite) # type: ignore

            one_sprite.close()
    return new_output_image


def save_image(w: Window):
    if not w.widgets_row:
        return

    new_image = proses_image(w)
    saveimgage_location: str = tkfd.asksaveasfilename(
        initialfile="Untitle.png",
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"),
                   ("JPG files", "*.jpg")])
    if saveimgage_location != '':
        new_image.save(saveimgage_location)


def save_yaml_or_json(w: Window):
    if not w.widgets_row:
        return

    if w.autoupdate_int.get():
        w.update_cells()
    outerdict: dict[str, dict[str, dict[str, int]]] = dict(dict(dict()))



    for bundle in w.widgets_row.values():
        middle: dict[str, dict[str, int]] = dict(dict())
        for row in bundle.values():
            img_path: str = row.img_path.get()
            file_name = img_path.split(r"/")[-1]

            first_number = len(file_name)
            for i, n in enumerate(file_name):
                if n.isdigit():
                    first_number = i
                    break

            img = f"{file_name[:first_number]}_n{row.bundles_id}"

            width, height = PILImage.open(img_path).size

            x_start = int(row.x_entry.get())
            y_start = int(row.y_entry.get())

            most_inner = {
                'h': height,
                'w': width,
                'y': y_start,
                'x': x_start,
            }

            middle[img] = most_inner

            outerdict[row.frames_entry.get()] = middle
        del middle


    saveimgage_location: str = tkfd.asksaveasfilename(
        initialfile="Untitle.yaml",
        defaultextension=".yaml",
        filetypes=[("YAML files", "*.yaml"),
                   ("JSON files", "*.json"),
                   ("All files", "*.*")])
    if saveimgage_location != '':
        with open(saveimgage_location, "w") as f:
            if saveimgage_location.endswith(".yaml"):
                yaml.dump(outerdict, f, default_flow_style=None)
            else:
                json.dump(outerdict, f, ensure_ascii=False, indent=4)


def begining_menu_bar(root: tk.Tk, w: Window):
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file = tk.Menu(menubar, tearoff=0)
    file.add_command(label="Save to CSV", command=lambda: save_table(w))
    file.add_command(label="Load from CSV", command=lambda: load_table(w))
    file.add_separator()
    file.add_command(label="Exit", command=sys.exit)

    menubar.add_cascade(label="File", menu=file)

    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: root.focus_get().event_generate('<<Cut>>')) # type: ignore
    editmenu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: root.focus_get().event_generate('<<Copy>>')) # type: ignore
    editmenu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: root.focus_get().event_generate('<<Paste>>')) # type: ignore
    editmenu.add_command(label="Select all", accelerator="Ctrl+A", command=lambda: root.focus_get().event_generate('<<SelectAll>>')) # type: ignore
    menubar.add_cascade(label="Edit", menu=editmenu)

    options = tk.Menu(menubar, tearoff=0)
    # sort = tk.Menu(options, tearoff=0)
    # sort.add_command(label="Sort by row")
    # sort.add_command(label="Sort by col")
    # options.add_cascade(label="Sorting...", menu=sort)
    options.add_separator()
    options.add_command(label='Add rows!', accelerator="F2", command=w.add_rows)
    options.add_command(label='Update!', accelerator="F5", command=w.update_cells)
    options.add_separator()
    options.add_command(label='View!', command=lambda: view_image(w))
    options.add_separator()
    options.add_command(label='Save image!', command=lambda: save_image(w))
    options.add_command(label='Export json or yaml', command=lambda: save_yaml_or_json(w))
    menubar.add_cascade(label="Options", menu=options)

    root.bind('<F2>', lambda _: w.add_rows())
    root.bind('<F5>', lambda _: w.update_cells())


def save_table(w: Window):
    if not w.widgets_row:
        return
    save_file_name: str = tkfd.asksaveasfilename(
        initialfile="Untitle.csv",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    with open(save_file_name, "w", encoding='utf-8') as sf:
        for bundle in w.widgets_row.values():
            for row in bundle.values():
                img_row = row.row_entry.get()
                img_col = row.col_entry.get()

                filepath = row.img_path.get()

                x_start: str = row.x_entry.get()
                y_start: str = row.y_entry.get()

                sprite_frame: str = row.frames_entry.get()

                sf.write(f"{row.wingets_id},{row.bundles_id},{img_row},{img_col},{filepath},{sprite_frame},{x_start},{y_start}\n")


def load_table(w: Window):
        csv_location: str = tkfd.askopenfilename(title="Open CSV")
        if csv_location != '':
            w.widgets_row.clear()

            with open(csv_location, 'r') as rf:
                fr = rf.readlines()

                # w.max_row_height = [int(t.strip()) for t in fr[0].split(",")]
                # w.wingets_unique_id = int(fr[1].strip())
                w.wingets_unique_id = 0
                w.offset = 0

                list_of_bundles: list[list[tuple[str,str,str,str,str,int,int,str]]] = []

                curent_bundle: list[tuple[str,str,str,str,str,int,int,str]] = []

                for csvRow in fr:
                    csv = csvRow.split(',')
                    # file_name = path.split(r"/")[-1]
                    row_n=csv[2]
                    col_n=csv[3]
                    path=csv[4]
                    x_n=csv[6]
                    y_n=csv[7]
                    wingets_unique_id=int(csv[0].strip())
                    bundles_id=int(csv[1].strip())
                    name_f=csv[5]

                    if bundles_id == 0:
                        if curent_bundle:
                            list_of_bundles.append(curent_bundle.copy())
                        curent_bundle.clear()

                    curent_bundle.append((row_n, col_n, path, x_n, y_n, wingets_unique_id, bundles_id, name_f))

                for bundles in list_of_bundles:
                    bundles_id = 0
                    w.widgets_row[w.wingets_unique_id] = {}
                    for row in bundles:
                        row_set_all_wigets(w,
                         row_n=row[0],
                         col_n=row[1],
                         path=row[2],
                         x_n=row[3],
                         y_n=row[4],
                         wingets_unique_id=w.wingets_unique_id, # row[5],
                         bundles_id=row[6],
                         name_f=row[7]
                        )
                        bundles_id += 1
                        w.update_buttons_locatons()
                    w.wingets_unique_id += 1
