from __future__ import annotations

import json
import sys
import yaml
import typing

from functools import partial
import webbrowser

import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askopenfilenames
from PIL import Image
from tkscrolledframe import ScrolledFrame




class WidgetRow(typing.NamedTuple):
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
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Sprite Sheet Packer')
        self.root.geometry("1280x680")
        self.root.resizable(width=True, height=True)
        try:
            self.root.iconbitmap("./../ssm2.ico") # type: ignore
        except Exception as e:
            print(e)
        try:
            self.root.iconbitmap('./ssm2.ico') # type: ignore
        except Exception as e:
            print(e)
        sf: ScrolledFrame = ScrolledFrame(self.root, width=680, height=680)
        sf.pack(side="top", expand=1, fill="both") # type: ignore
        # sf.bind_arrow_keys(self.root)
        sf.bind_scroll_wheel(self.root) # type: ignore

        self.inner_frame: tk.Frame = typing.cast(tk.Frame, sf.display_widget(tk.Frame)) # type: ignore
        self.offset = 0

        self.controlers: dict[int, WidgetRow] = {}
        self.list_frame_id: list[str] = []

        self.total_width_of_save_image, self.total_height_of_save_image = 0, 0

        self.add_multiple = tk.Button(self.inner_frame, command=self.add_rows, text='Add images')
        self.update = tk.Button(self.inner_frame, command=self.update_cells, text='Update')
        self.save = tk.Button(self.inner_frame, command=self.save_img, text='Save image!')
        self.save_yaml_json = tk.Button(self.inner_frame, command=self.save_yaml_or_json, text='Export yaml or json!')
        self.view = tk.Button(self.inner_frame, command=self.view_image, text='View')
        self.autoupdate_int = tk.IntVar()
        self.auto_update_checkbox = tk.Checkbutton(self.inner_frame, text='auto update', variable=self.autoupdate_int)

        self.add_multiple.grid(row=self.offset, column=4, columnspan=2)
        self.update.grid(row=self.offset, column=8, columnspan=2)
        self.auto_update_checkbox.grid(row=self.offset, column=10, columnspan=6)

        self.save.grid(row=self.offset + 1, column=0, columnspan=2)
        self.save_yaml_json.grid(row=self.offset + 1, column=4, columnspan=2)
        self.view.grid(row=self.offset + 1, column=8, columnspan=4)

        self.rows_added = 0
        self.addrows_column = 0
        self.row_image_y: list[int] = []

        self.last_number_in_file: None | str = None
        self.addedbundle_row = 0
        self.mb = MenuBar(self)

        self.focus_row = 0
        self.focus_col = 0
        self.root.bind("<Up>", lambda _: self._arrow_move_row(-1))
        self.root.bind("<Down>", lambda _: self._arrow_move_row(1))

        self.root.bind("<Left>", lambda _: self._arrow_move_col(0))
        self.root.bind("<Right>", lambda _: self._arrow_move_col(1))

        self.bottom_stripe = tk.Label(self.root, text='http://www.paypal.me/', relief=tk.SUNKEN, anchor=tk.W, fg='blue')
        self.bottom_stripe.bind("<Button-1>", lambda _: webbrowser.open_new("http://www.paypal.me/JikoUnderscore/1"))
        self.bottom_stripe.place(anchor=tk.S, relx=0.50, rely=1, relwidth=1)

    def _arrow_move_row(self, direction: int):
        self._get_curent_focuss()

        row: int = self.focus_row + direction
        if row < 0:
            row = 0
        if row > (len_rows := len(self.controlers) - 1):
            row = len_rows

        wig: WidgetRow = self.controlers[row]
        if self.focus_col == 0:
            wig.row_entry.focus_set()
            wig.row_entry.selection_range(0, tk.END)
        elif self.focus_col == 1:
            wig.col_entry.focus_set()
            wig.col_entry.selection_range(0, tk.END)

    def _arrow_move_col(self, direction: int):
        self._get_curent_focuss()

        wig: WidgetRow = self.controlers[self.focus_row]

        if direction == 0:
            wig.row_entry.focus_set()
            wig.row_entry.selection_range(0, tk.END)
        elif direction == 1:
            wig.col_entry.focus_set()
            wig.col_entry.selection_range(0, tk.END)

    def _get_curent_focuss(self):
        for index, wig in enumerate(self.controlers.values()):
            if wig.col_entry is self.root.focus_get() or wig.row_entry is self.root.focus_get():
                self.focus_row = index
                if wig.col_entry is self.root.focus_get():
                    self.focus_col = 1
                if wig.row_entry is self.root.focus_get():
                    self.focus_col = 0

    def view_image(self) -> None:
        if self.controlers:
            new_image: Image.Image = self._proses_img()
            new_image.show()

    def add_rows(self) -> None:
        filez = askopenfilenames(title='Choose a file')

        self.addrows_column = 0
        self.row_image_y.append(0)
        for path in filez:
            self._add_row(path)
        self.addedbundle_row += 1

        if self.autoupdate_int.get():
            self.update_cells()


    def _add_row(self, imgLoc: str) -> None:
        self.update_buttons_locatons()

        file_name: str = imgLoc.split(r'/')[-1]

        row = tk.Label(self.inner_frame, text='row')
        image_row = tk.Entry(self.inner_frame, width=5)
        image_row.insert(0, str(self.addedbundle_row))
        row.grid(row=self.rows_added, column=0)
        image_row.grid(row=self.rows_added, column=1)


        col = tk.Label(self.inner_frame, text='col')
        image_col = tk.Entry(self.inner_frame, width=5)
        image_col.insert(0, str(self.addrows_column))
        col.grid(row=self.rows_added, column=2)
        image_col.grid(row=self.rows_added, column=3)


        image_path = tk.Entry(self.inner_frame, width=len(imgLoc))
        image_path.insert(0, imgLoc)
        image_path.grid(row=self.rows_added, column=4, columnspan=3)

        x_l = tk.Label(self.inner_frame, text='x')
        x = tk.Entry(self.inner_frame, width=5)
        x.insert(0, "0")
        x_l.grid(row=self.rows_added, column=8)
        x.grid(row=self.rows_added, column=9)

        y_l = tk.Label(self.inner_frame, text='y')
        y = tk.Entry(self.inner_frame, width=5)
        y.insert(0, "0")
        y_l.grid(row=self.rows_added, column=11)
        y.grid(row=self.rows_added, column=12)

        pop_b = tk.Button(self.inner_frame, text='pop', command=partial(self.remove_row, self.rows_added), font=('Helvetica', '7'), width=5)
        pop_b.grid(row=self.rows_added, column=14)

        frames_l = tk.Label(self.inner_frame, text="frames")
        frame_name = tk.Entry(self.inner_frame, width=30)
        frame_name.insert(0, f"{file_name.split('.')[0]}_n{self.addrows_column+1}")
        frames_l.grid(row=self.rows_added, column=15)
        frame_name.grid(row=self.rows_added, column=16)



        image: Image.Image = Image.open(imgLoc)
        _, height = image.size
        image.close()
        last_height = self.row_image_y[self.addedbundle_row] if self.row_image_y else 0


        self.row_image_y[self.addedbundle_row] = max(last_height, height)
        self.controlers[self.rows_added] = WidgetRow(row, image_row, col, image_col, image_path, x_l, x, y_l, y, pop_b, frames_l, frame_name)
        self.rows_added += 1
        self.addrows_column += 1

    def remove_row(self, row: int) -> None:
        ele: tk.Entry | tk.Button | tk.Label | tk.Checkbutton

        for ele in self.controlers[row]:
            ele.destroy()
        del self.controlers[row]
        self.rows_added -= 1

    def update_buttons_locatons(self) -> None:
        self.offset += 1
        self.add_multiple.grid(row=self.offset, column=4, columnspan=2)
        self.update.grid(row=self.offset, column=8, columnspan=2)
        self.auto_update_checkbox.grid(row=self.offset, column=10, columnspan=6)

        self.save.grid(row=self.offset + 1, column=0, columnspan=2)
        self.save_yaml_json.grid(row=self.offset + 1, column=4, columnspan=2)
        self.view.grid(row=self.offset + 1, column=8, columnspan=2)

    def update_cells(self, replace_xy_values:bool=True) -> None:
        if not self.controlers:
            return
        self.list_frame_id.clear()
        self.total_width_of_save_image = 0
        self.total_height_of_save_image = 0


        for row in self.controlers.values():
            row_pos = int(row.row_entry.get())
            col_pos = int(row.col_entry.get())

            image_path: str = row.img_path.get()

            self.list_frame_id.append(row.frames_entry.get())

            image: Image.Image = Image.open(image_path)
            width, height = image.size
            image.close()


            y = sum(self.row_image_y[0:row_pos]) if row_pos >= 1 else row_pos * height

            if replace_xy_values:
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



    def _proses_img(self) -> Image.Image:
        if self.autoupdate_int.get():
            self.update_cells()

        if self.total_height_of_save_image == 0 or self.total_width_of_save_image == 0:
            self.update_cells(replace_xy_values=False)

        new_output_image = Image.new('RGBA', (self.total_width_of_save_image, self.total_height_of_save_image))
        for row in self.controlers.values():
            img: str = row.img_path.get()

            one_sprite = Image.open(img)

            new_output_image.paste(one_sprite, (int(row.x_entry.get()), int(row.y_entry.get())))

            one_sprite.close()
        return new_output_image

    def save_img(self) -> None:
        if not self.controlers:
            return
        new_image: Image.Image = self._proses_img()
        saveimgage_location: str = asksaveasfilename(
            initialfile="Untitle.png",
            defaultextension=".png",
            filetypes=[("All files", "*.*"),
                       ("PNG files", "*.png"),
                       ("JPG files", "*.jpg")])
        if saveimgage_location != '':
            new_image.save(saveimgage_location)

    def save_yaml_or_json(self) -> None:
        if not self.controlers:
            return

        if self.autoupdate_int.get():
            self.update_cells()
        ymalfile: dict[str, dict[str, dict[str, int]]] = {non: {} for non in self.list_frame_id}

        for row in self.controlers.values():
            img_path: str = row.img_path.get()
            img: str = img_path.split(r'/')[-1].rsplit('.', 1)[0]

            width, height = Image.open(img_path).size

            x_start = int(row.x_entry.get())
            y_start = int(row.y_entry.get())

            ymalfile[row.frames_entry.get()][img] = {
                'h': height,
                'w': width,
                'y': y_start,
                'x': x_start,
            }

        saveimgage_location: str = asksaveasfilename(
            initialfile="Untitle.yaml",
            defaultextension=".yaml",
            filetypes=[("All files", "*.*"),
                       ("YAML files", "*.yaml"),
                       ("JSON files", "*.json")])
        if saveimgage_location != '':
            with open(saveimgage_location, "w") as f:
                if saveimgage_location.endswith(".yaml"):
                    yaml.dump(ymalfile, f, default_flow_style=None)
                else:
                    json.dump(ymalfile, f, ensure_ascii=False, indent=4)


class MenuBar:
    def __init__(self, windowObj: Window):
        menubar = tk.Menu(windowObj.root)
        windowObj.root.config(menu=menubar)

        self.windowObj = windowObj

        file = tk.Menu(menubar, tearoff=0)
        file.add_command(label='Save to CSV', command=self.save_table)
        file.add_command(label='Open CSV', command=self.load_tabel)
        file.add_separator()
        file.add_command(label="Exit", command=sys.exit)

        menubar.add_cascade(label="File", menu=file)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Cut", accelerator="Ctrl+X",
                             command=lambda: windowObj.root.focus_get().event_generate('<<Cut>>')) # type: ignore
        editmenu.add_command(label="Copy", accelerator="Ctrl+C",
                             command=lambda: windowObj.root.focus_get().event_generate('<<Copy>>')) # type: ignore
        editmenu.add_command(label="Paste", accelerator="Ctrl+V",
                             command=lambda: windowObj.root.focus_get().event_generate('<<Paste>>')) # type: ignore
        editmenu.add_command(label="Select all", accelerator="Ctrl+A",
                             command=lambda: windowObj.root.focus_get().event_generate('<<SelectAll>>')) # type: ignore
        menubar.add_cascade(label="Edit", menu=editmenu)

        options = tk.Menu(menubar, tearoff=0)
        sort = tk.Menu(options, tearoff=0)
        sort.add_command(label="Sort by row", command=self.sort_x)
        sort.add_command(label="Sort by col", command=self.sort_y)
        options.add_cascade(label="Sorting...", menu=sort)
        options.add_separator()
        options.add_command(label='Add rows!', accelerator="F2", command=windowObj.add_rows)
        options.add_command(label='Update!', accelerator="F5", command=windowObj.update_cells)
        options.add_separator()
        options.add_command(label='View!', command=windowObj.view_image)
        options.add_separator()
        options.add_command(label='Save image!', command=windowObj.save_img)
        options.add_command(label='Export json or yaml', command=windowObj.save_yaml_or_json)
        menubar.add_cascade(label="Options", menu=options)

        windowObj.root.bind('<F2>', lambda _: windowObj.add_rows())
        windowObj.root.bind('<F5>', lambda _: windowObj.update_cells())

    def save_table(self) -> None:
        if not self.windowObj.controlers:
            return
        save_file_name: str = asksaveasfilename(
            initialfile="Untitle.csv",
            defaultextension=".csv",
            filetypes=[("All files", "*.*"),
                       ("CSV files", "*.csv")]
        )
        with open(save_file_name, "w", encoding='utf-8') as sf:
            for row in self.windowObj.controlers.values():
                img_row = row.row_entry.get()
                img_col = row.col_entry.get()

                filepath = row.img_path.get()

                x_start: str = row.x_entry.get()
                y_start: str = row.y_entry.get()

                sprite_frame: str = row.frames_entry.get()

                sf.write(f'{img_row},{img_col},{filepath},{sprite_frame},{x_start},{y_start}\n')

    def load_tabel(self) -> None:
        csv_location: str = askopenfilename(title="Open CSV")
        if csv_location != '':
            self.windowObj.controlers.clear()
            self.windowObj.rows_added = 0

            with open(csv_location, 'r') as fr:
                for csvRow in fr:
                    csv = csvRow.split(',')
                    self.windowObj.update_buttons_locatons()

                    row = tk.Label(self.windowObj.inner_frame, text='row')
                    e1 = tk.Entry(self.windowObj.inner_frame, width=5)
                    e1.insert(0, csv[0])
                    row.grid(row=self.windowObj.rows_added, column=0)
                    e1.grid(row=self.windowObj.rows_added, column=1)

                    col = tk.Label(self.windowObj.inner_frame, text='col')
                    e2 = tk.Entry(self.windowObj.inner_frame, width=5)
                    e2.insert(0, csv[1])
                    col.grid(row=self.windowObj.rows_added, column=2)
                    e2.grid(row=self.windowObj.rows_added, column=3)

                    e3 = tk.Entry(self.windowObj.inner_frame, width=len(csv[2]))
                    e3.insert(0, csv[2])
                    e3.grid(row=self.windowObj.rows_added, column=4, columnspan=3)

                    l1 = tk.Label(self.windowObj.inner_frame, text='x')
                    e4 = tk.Entry(self.windowObj.inner_frame, width=5)
                    e4.insert(0, csv[4])
                    l1.grid(row=self.windowObj.rows_added, column=8)
                    e4.grid(row=self.windowObj.rows_added, column=9)

                    l2 = tk.Label(self.windowObj.inner_frame, text='y')
                    e6 = tk.Entry(self.windowObj.inner_frame, width=5)
                    e6.insert(0, csv[5])
                    l2.grid(row=self.windowObj.rows_added, column=11)
                    e6.grid(row=self.windowObj.rows_added, column=12)

                    b = tk.Button(self.windowObj.inner_frame, text='pop',
                                  command=partial(self.windowObj.remove_row, self.windowObj.rows_added),
                                  font=('Helvetica', '7'), width=5)
                    b.grid(row=self.windowObj.rows_added, column=14)

                    l3 = tk.Label(self.windowObj.inner_frame, text="frames")
                    ind = tk.Entry(self.windowObj.inner_frame, width=30)
                    ind.insert(0, csv[3])
                    l3.grid(row=self.windowObj.rows_added, column=15)
                    ind.grid(row=self.windowObj.rows_added, column=16)

                    self.windowObj.controlers[self.windowObj.rows_added] = WidgetRow(row, e1, col, e2, e3, l1, e4, l2, e6, b, l3, ind)
                    self.windowObj.rows_added += 1

    def sort_x(self):
        if not self.windowObj.controlers:
            return
        self._sort()

    def sort_y(self):
        if not self.windowObj.controlers:
            return
        self._sort(1)

    def _sort(self, sort_x=0):
        temp_container: list[tuple[int, int, str, str, str, str]] = []
        for row in self.windowObj.controlers.values():
            img_row: str = row.row_entry.get()
            img_col: str = row.col_entry.get()

            filepath: str = row.img_path.get()

            x_start: str = row.x_entry.get()
            y_start: str = row.y_entry.get()

            sprite_frame: str = row.frames_entry.get()

            temp_container.append((int(img_row), int(img_col), filepath, sprite_frame, x_start, y_start))

        ele: tk.Entry | tk.Button | tk.Label

        for widget_row in self.windowObj.controlers.values():
            for ele in widget_row:
                ele.destroy()

        self.windowObj.controlers.clear()
        self.windowObj.rows_added = 0

        other: int = 1 if sort_x == 0 else 0
        temp_container = sorted(temp_container, key=lambda x: (x[sort_x], x[other]))

        for tmp in temp_container:
            self.windowObj.update_buttons_locatons()

            row = tk.Label(self.windowObj.inner_frame, text='row')
            e1 = tk.Entry(self.windowObj.inner_frame, width=5)
            e1.insert(0, str(tmp[0]))
            row.grid(row=self.windowObj.rows_added, column=0)
            e1.grid(row=self.windowObj.rows_added, column=1)

            col = tk.Label(self.windowObj.inner_frame, text='col')
            e2 = tk.Entry(self.windowObj.inner_frame, width=5)
            e2.insert(0, str(tmp[1]))
            col.grid(row=self.windowObj.rows_added, column=2)
            e2.grid(row=self.windowObj.rows_added, column=3)

            e3 = tk.Entry(self.windowObj.inner_frame, width=len(tmp[2]))
            e3.insert(0, tmp[2])
            e3.grid(row=self.windowObj.rows_added, column=4, columnspan=3)

            l1 = tk.Label(self.windowObj.inner_frame, text='x')
            e4 = tk.Entry(self.windowObj.inner_frame, width=5)
            e4.insert(0, tmp[4])
            l1.grid(row=self.windowObj.rows_added, column=8)
            e4.grid(row=self.windowObj.rows_added, column=9)

            l2 = tk.Label(self.windowObj.inner_frame, text='y')
            e6 = tk.Entry(self.windowObj.inner_frame, width=5)
            e6.insert(0, tmp[5])
            l2.grid(row=self.windowObj.rows_added, column=11)
            e6.grid(row=self.windowObj.rows_added, column=12)

            b = tk.Button(self.windowObj.inner_frame, text='pop',
                          command=partial(self.windowObj.remove_row, self.windowObj.rows_added), font=('Helvetica', '7'),
                          width=5)
            b.grid(row=self.windowObj.rows_added, column=14)

            l3 = tk.Label(self.windowObj.inner_frame, text="frames")
            ind = tk.Entry(self.windowObj.inner_frame, width=30)
            ind.insert(0, tmp[3])
            l3.grid(row=self.windowObj.rows_added, column=15)
            ind.grid(row=self.windowObj.rows_added, column=16)

            self.windowObj.controlers[self.windowObj.rows_added] = WidgetRow(row, e1, col, e2, e3, l1, e4, l2, e6, b, l3,
                                                                             ind)
            self.windowObj.rows_added += 1
