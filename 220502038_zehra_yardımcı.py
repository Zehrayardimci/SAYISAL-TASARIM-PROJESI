import tkinter as tk
from tkinter import ttk

# Mantık kapısı temel sınıfı
class LogicGate:
    def __init__(self, canvas, x, y, gate_type):
        self.canvas = canvas
        self.gate_type = gate_type
        self.x, self.y = x, y
        self.id = canvas.create_rectangle(x, y, x + 60, y + 40, fill="lightgray")
        self.text_id = canvas.create_text(x + 30, y + 20, text=gate_type, font=("Arial", 12))
        self.input_ids = []
        self.output = None
        self.connected_gates = []

        self.create_input_output_ports()
        # Taşıma ve özellikleri gösterme işlemleri
        self.canvas.tag_bind(self.id, '<B1-Motion>', self.move)
        self.canvas.tag_bind(self.text_id, '<B1-Motion>', self.move)
        self.canvas.tag_bind(self.id, '<ButtonPress-1>', self.on_start_drag)
        self.canvas.tag_bind(self.text_id, '<ButtonPress-1>', self.on_start_drag)
        self.canvas.tag_bind(self.id, '<ButtonRelease-1>', self.on_drop)
        self.canvas.tag_bind(self.text_id, '<ButtonRelease-1>', self.on_drop)

        self.canvas.tag_bind(self.id, '<ButtonPress-3>', self.show_properties)
        self.canvas.tag_bind(self.text_id, '<ButtonPress-3>', self.show_properties)

    def create_input_output_ports(self):
        # Kapı için giriş ve çıkış portları oluşturur
        for input_id in self.input_ids:
            self.canvas.delete(input_id)
        self.input_ids = []

        input_count = 2 if isinstance(self, BinaryGate) else 1
        for i in range(input_count):
            input_id = self.canvas.create_oval(self.x - 10, self.y + 10 + i*20, self.x, self.y + 20 + i*20, fill="white")
            self.input_ids.append(input_id)
            self.canvas.tag_bind(input_id, '<ButtonPress-3>', self.start_connection)

        self.output_id = self.canvas.create_oval(self.x + 60, self.y + 20, self.x + 70, self.y + 30, fill="white")
        self.canvas.tag_bind(self.output_id, '<ButtonPress-3>', self.start_connection)

    def on_start_drag(self, event):
        # Sürüklemeye başlama işlemi
        self.drag_data = {'x': event.x, 'y': event.y}

    def move(self, event):
        # Sürükleme işlemi
        dx = event.x - self.drag_data['x']
        dy = event.y - self.drag_data['y']
        self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        for input_id in self.input_ids:
            self.canvas.move(input_id, dx, dy)
        self.canvas.move(self.output_id, dx, dy)
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def on_drop(self, event):
        # Sürükleme işlemini bitirme
        self.drag_data = None

    def show_properties(self, event):
        # Özellikleri gösterme penceresi oluşturma
        self.properties_window = tk.Toplevel(self.canvas)
        self.properties_window.title("Özellikler")

        tk.Label(self.properties_window, text="Etiket:").grid(row=0, column=0)
        self.label_entry = tk.Entry(self.properties_window)
        self.label_entry.grid(row=0, column=1)
        self.label_entry.insert(0, self.gate_type)

        tk.Label(self.properties_window, text="Giriş Bağlantı Sayısı:").grid(row=1, column=0)
        self.input_count_entry = tk.Entry(self.properties_window)
        self.input_count_entry.grid(row=1, column=1)
        self.input_count_entry.insert(0, "2" if isinstance(self, BinaryGate) else "1")

        tk.Button(self.properties_window, text="Kaydet", command=self.save_properties).grid(row=2, column=0, columnspan=2)

    def save_properties(self):
        # Özellikleri kaydetme işlemi
        self.gate_type = self.label_entry.get()
        self.canvas.itemconfig(self.text_id, text=self.gate_type)
        try:
            input_count = int(self.input_count_entry.get())
            if input_count != len(self.input_ids):
                if input_count == 1:
                    self.__class__ = UnaryGate
                    self.perform_gate_logic = UnaryGate.perform_gate_logic
                elif input_count == 2:
                    self.__class__ = BinaryGate
                    self.perform_gate_logic = BinaryGate.perform_gate_logic
                self.create_input_output_ports()
        except ValueError:
            pass
        self.properties_window.destroy()

    def get_output(self):
        # Çıkış değerini döndürme
        return self.output

    def start_connection(self, event):
        # Bağlantı başlatma işlemi
        self.start_x, self.start_y = event.x, event.y
        self.line = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y)
        self.canvas.bind("<Motion>", self.draw_connection)
        self.canvas.bind("<ButtonRelease-3>", self.finish_connection)

    def draw_connection(self, event):
        # Bağlantı çizme işlemi
        self.canvas.coords(self.line, self.start_x, self.start_y, event.x, event.y)

    def finish_connection(self, event):
        # Bağlantı bitirme işlemi
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<ButtonRelease-3>")
        self.end_x, self.end_y = event.x, event.y
        self.canvas.coords(self.line, self.start_x, self.start_y, self.end_x, self.end_y)
        connection = Connection(self.canvas, self.start_x, self.start_y, self.end_x, self.end_y, label_visible=False)
        self.connected_gates.append(connection)

# İkili girişli mantık kapısı sınıfı
class BinaryGate(LogicGate):
    def __init__(self, canvas, x, y, gate_type):
        super().__init__(canvas, x, y, gate_type)
        self.input1 = None
        self.input2 = None

    def set_input1(self, value):
        self.input1 = value

    def set_input2(self, value):
        self.input2 = value

    def perform_gate_logic(self):
        # Mantık kapısı işlemi (ikili girişli kapılar için)
        pass

# Tek girişli mantık kapısı sınıfı
class UnaryGate(LogicGate):
    def __init__(self, canvas, x, y, gate_type):
        super().__init__(canvas, x, y, gate_type)
        self.input = None

    def set_input(self, value):
        # Giriş değerini ayarlama
        self.input = value

    def perform_gate_logic(self):
        # Mantık kapısı işlemi (tek girişli kapılar için)
        pass

# AND kapısı sınıfı
class ANDGate(BinaryGate):
    def perform_gate_logic(self):
        if self.input1 is not None and self.input2 is not None:
            self.output = int(self.input1 and self.input2)
        else:
            self.output = None

# OR kapısı sınıfı
class ORGate(BinaryGate):
    def perform_gate_logic(self):
        if self.input1 is not None and self.input2 is not None:
            self.output = int(self.input1 or self.input2)
        else:
            self.output = None

class NOTGate(UnaryGate):
    def perform_gate_logic(self):
        if self.input is not None:
            self.output = int(not self.input)
        else:
            self.output = None


class BufferGate(UnaryGate):
    def __init__(self, canvas, x, y, gate_type):
        super().__init__(canvas, x, y, gate_type)

    def perform_gate_logic(self):
        if self.input is not None:
            self.output = self.input
        else:
            self.output = None


class NANDGate(BinaryGate):
    def perform_gate_logic(self):
        if self.input1 is not None and self.input2 is not None:
            self.output = int(not (self.input1 and self.input2))
        else:
            self.output = None

class NORGate(BinaryGate):
    def perform_gate_logic(self):
        if self.input1 is not None and self.input2 is not None:
            self.output = int(not (self.input1 or self.input2))
        else:
            self.output = None

class XORGate(BinaryGate):
    def perform_gate_logic(self):
        if self.input1 is not None and self.input2 is not None:
            self.output = int(self.input1 != self.input2)
        else:
            self.output = None

class XNORGate(BinaryGate):
    def perform_gate_logic(self):
        if self.input1 is not None and self.input2 is not None:
            self.output = int(self.input1 == self.input2)
        else:
            self.output = None

class LED:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x, self.y = x, y
        self.id = canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="yellow")
        self.label_id = canvas.create_text(x, y - 20, text="LED")  # Etiket yazısını daha yukarı taşındı
        self.value = 0

        self.canvas.tag_bind(self.id, '<ButtonPress-3>', self.show_properties)
        self.canvas.tag_bind(self.label_id, '<ButtonPress-3>', self.show_properties)

    def set_value(self, value):
        # LED değerini ayarlama
        self.value = value
        color = "red" if value == 1 else "yellow"
        self.canvas.itemconfig(self.id, fill=color)

    def show_properties(self, event):
        # Özellikleri gösterme penceresi oluşturma
        self.properties_window = tk.Toplevel(self.canvas)
        self.properties_window.title("Özellikler")

        tk.Label(self.properties_window, text="Etiket:").grid(row=0, column=0)
        self.label_entry = tk.Entry(self.properties_window)
        self.label_entry.grid(row=0, column=1)
        self.label_entry.insert(0, self.canvas.itemcget(self.label_id, 'text'))

        tk.Label(self.properties_window, text="Renk:").grid(row=1, column=0)
        self.color_entry = tk.Entry(self.properties_window)
        self.color_entry.grid(row=1, column=1)
        self.color_entry.insert(0, "yellow")

        tk.Button(self.properties_window, text="Kaydet", command=self.save_properties).grid(row=2, column=0, columnspan=2)

    def save_properties(self):
        # Özellikleri kaydetme işlemi
        label_text = self.label_entry.get()
        self.canvas.itemconfig(self.label_id, text=label_text)
        color = self.color_entry.get()
        self.canvas.itemconfig(self.id, fill=color)
        self.properties_window.destroy()

# Giriş kutusu sınıfı
class InputBox:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x, self.y = x, y
        self.entry = tk.Entry(canvas, width=5)
        self.window_id = canvas.create_window(x, y, window=self.entry)
        self.label_id = canvas.create_text(x, y - 20, text="Giriş Kutusu")  # Etiket yazısını daha yukarı taşındı
        self.canvas.tag_bind(self.window_id, '<ButtonPress-3>', self.show_properties)
        self.canvas.tag_bind(self.label_id, '<ButtonPress-3>', self.show_properties)

    def show_properties(self, event):
        # Özellikleri gösterme penceresi oluşturma
        self.properties_window = tk.Toplevel(self.canvas)
        self.properties_window.title("Özellikler")

        tk.Label(self.properties_window, text="Etiket:").grid(row=0, column=0)
        self.label_entry = tk.Entry(self.properties_window)
        self.label_entry.grid(row=0, column=1)
        self.label_entry.insert(0, self.canvas.itemcget(self.label_id, 'text'))

        tk.Label(self.properties_window, text="Renk:").grid(row=1, column=0)
        self.color_entry = tk.Entry(self.properties_window)
        self.color_entry.grid(row=1, column=1)
        self.color_entry.insert(0, "white")

        tk.Label(self.properties_window, text="Başlangıç Değeri:").grid(row=2, column=0)
        self.value_entry = tk.Entry(self.properties_window)
        self.value_entry.grid(row=2, column=1)
        self.value_entry.insert(0, self.entry.get())

        tk.Button(self.properties_window, text="Kaydet", command=self.save_properties).grid(row=3, column=0, columnspan=2)

    def save_properties(self):
        # Özellikleri kaydetme işlemi
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.value_entry.get())
        color = self.color_entry.get()
        self.entry.config(bg=color)
        label_text = self.label_entry.get()
        self.canvas.itemconfig(self.label_id, text=label_text)
        self.properties_window.destroy()

# Çıkış kutusu sınıfı
class OutputBox:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x, self.y = x, y
        self.entry = tk.Entry(canvas, width=5)
        self.window_id = canvas.create_window(x, y, window=self.entry)
        self.label_id = canvas.create_text(x, y - 20, text="Çıkış Kutusu")  # Etiket yazısını daha yukarı taşındı
        self.canvas.tag_bind(self.window_id, '<ButtonPress-3>', self.show_properties)
        self.canvas.tag_bind(self.label_id, '<ButtonPress-3>', self.show_properties)

    def show_properties(self, event):
        self.properties_window = tk.Toplevel(self.canvas)
        self.properties_window.title("Özellikler")

        tk.Label(self.properties_window, text="Etiket:").grid(row=0, column=0)
        self.label_entry = tk.Entry(self.properties_window)
        self.label_entry.grid(row=0, column=1)
        self.label_entry.insert(0, self.canvas.itemcget(self.label_id, 'text'))

        tk.Label(self.properties_window, text="Renk:").grid(row=1, column=0)
        self.color_entry = tk.Entry(self.properties_window)
        self.color_entry.grid(row=1, column=1)
        self.color_entry.insert(0, "white")

        tk.Button(self.properties_window, text="Kaydet", command=self.save_properties).grid(row=2, column=0, columnspan=2)

    def save_properties(self):
        color = self.color_entry.get()
        self.entry.config(bg=color)
        label_text = self.label_entry.get()
        self.canvas.itemconfig(self.label_id, text=label_text)
        self.properties_window.destroy()

# Bağlantı sınıfı
class Connection:
    def __init__(self, canvas, x1, y1, x2, y2, label_visible=True):
        self.canvas = canvas
        self.line_id = canvas.create_line(x1, y1, x2, y2, fill="black")
        self.label_id = None
        if label_visible:
            self.label_id = canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="Bağlantı")
            self.canvas.tag_bind(self.label_id, '<ButtonPress-3>', self.show_properties)
        self.canvas.tag_bind(self.line_id, '<ButtonPress-3>', self.show_properties)

    def show_properties(self, event):
        self.properties_window = tk.Toplevel(self.canvas)
        self.properties_window.title("Özellikler")

        tk.Label(self.properties_window, text="Etiket:").grid(row=0, column=0)
        self.label_entry = tk.Entry(self.properties_window)
        self.label_entry.grid(row=0, column=1)
        if self.label_id:
            self.label_entry.insert(0, self.canvas.itemcget(self.label_id, 'text'))
        else:
            self.label_entry.insert(0, "")

        tk.Label(self.properties_window, text="Renk:").grid(row=1, column=0)
        self.color_entry = tk.Entry(self.properties_window)
        self.color_entry.grid(row=1, column=1)
        self.color_entry.insert(0, self.canvas.itemcget(self.line_id, 'fill'))

        tk.Button(self.properties_window, text="Kaydet", command=self.save_properties).grid(row=2, column=0, columnspan=2)

    def save_properties(self):
        if self.label_id:
            label_text = self.label_entry.get()
            self.canvas.itemconfig(self.label_id, text=label_text)
        else:
            label_text = self.label_entry.get()
            self.label_id = self.canvas.create_text((self.canvas.coords(self.line_id)[0] + self.canvas.coords(self.line_id)[2]) // 2,
                                                    (self.canvas.coords(self.line_id)[1] + self.canvas.coords(self.line_id)[3]) // 2,
                                                    text=label_text)
            self.canvas.tag_bind(self.label_id, '<ButtonPress-3>', self.show_properties)
        color = self.color_entry.get()
        self.canvas.itemconfig(self.line_id, fill=color)
        self.properties_window.destroy()

# Düğüm sınıfı
class Node:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x, self.y = x, y
        self.id = canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue")
        self.label_id = canvas.create_text(x, y - 15, text="Düğüm")  # Etiket ekledik
        self.canvas.tag_bind(self.id, '<ButtonPress-3>', self.show_properties)
        self.canvas.tag_bind(self.label_id, '<ButtonPress-3>', self.show_properties)

    def show_properties(self, event):
        self.properties_window = tk.Toplevel(self.canvas)
        self.properties_window.title("Özellikler")

        tk.Label(self.properties_window, text="Etiket:").grid(row=0, column=0)
        self.label_entry = tk.Entry(self.properties_window)
        self.label_entry.grid(row=0, column=1)
        self.label_entry.insert(0, self.canvas.itemcget(self.label_id, 'text'))

        tk.Label(self.properties_window, text="Renk:").grid(row=1, column=0)
        self.color_entry = tk.Entry(self.properties_window)
        self.color_entry.grid(row=1, column=1)
        self.color_entry.insert(0, self.canvas.itemcget(self.id, 'fill'))

        tk.Button(self.properties_window, text="Kaydet", command=self.save_properties).grid(row=2, column=0, columnspan=2)

    def save_properties(self):
        label_text = self.label_entry.get()
        self.canvas.itemconfig(self.label_id, text=label_text)
        color = self.color_entry.get()
        self.canvas.itemconfig(self.id, fill=color)
        self.properties_window.destroy()

# Sayısal tasarım uygulaması sınıfı
class LogicDesignApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sayısal Tasarım Projesi")

        self.selected_tool = None
        self.elements = []
        self.connections = []
        self.gates = []
        self.inputs = []
        self.outputs = []
        self.leds = []
        self.nodes = []

        self.tools_frame = ttk.Frame(root, padding="10")
        self.tools_frame.grid(row=0, column=0, sticky="nw")

        self.design_area_frame = ttk.Frame(root, padding="10", borderwidth=2, relief="sunken")
        self.design_area_frame.grid(row=0, column=1, sticky="nsew")

        self.design_area = tk.Canvas(self.design_area_frame, width=800, height=600, bg="white")
        self.design_area.pack()

        self.control_frame = ttk.Frame(root, padding="10")
        self.control_frame.grid(row=0, column=2, rowspan=2, sticky="nsew")

        self.create_tools()
        self.create_control_buttons()

        self.design_area.bind("<Button-1>", self.place_element)
        self.design_area.bind("<Button-3>", self.start_connection)

    def create_tools(self):
        # Araç çubuğunu oluşturur
        ttk.Label(self.tools_frame, text="Araçlar").grid(row=0, column=0, pady=5)

        ttk.Label(self.tools_frame, text="Mantık Kapıları").grid(row=1, column=0, pady=5)
        self.add_tool_button("AND Gate", 2)
        self.add_tool_button("OR Gate", 3)
        self.add_tool_button("NOT Gate", 4)
        self.add_tool_button("Buffer", 5)
        self.add_tool_button("NAND Gate", 6)
        self.add_tool_button("NOR Gate", 7)
        self.add_tool_button("XOR Gate", 8)
        self.add_tool_button("XNOR Gate", 9)

        ttk.Label(self.tools_frame, text="Giriş/Çıkış Elemanları").grid(row=10, column=0, pady=5)
        self.add_tool_button("Giriş Kutusu", 11)
        self.add_tool_button("Çıkış Kutusu", 12)
        self.add_tool_button("Led", 13)

        ttk.Label(self.tools_frame, text="Bağlantı Elemanları").grid(row=14, column=0, pady=5)
        self.add_tool_button("Çizgi Çizme", 15)
        self.add_tool_button("Bağlantı Düğümü", 16)

    def add_tool_button(self, text, row):
        # Araç butonu ekler
        button = ttk.Button(self.tools_frame, text=text, command=lambda t=text: self.select_tool(t))
        button.grid(row=row, column=0, pady=2)

    def select_tool(self, tool):
        # Seçilen aracı ayarla
        self.selected_tool = tool
        print(f"Seçili araç: {self.selected_tool}")

    def place_element(self, event):
        # Elemanları yerleştirir
        if self.selected_tool:
            x, y = event.x, event.y
            gate = None
            if self.selected_tool == "AND Gate":
                gate = ANDGate(self.design_area, x, y, self.selected_tool)
            elif self.selected_tool == "OR Gate":
                gate = ORGate(self.design_area, x, y, self.selected_tool)
            elif self.selected_tool == "NOT Gate":
                gate = NOTGate(self.design_area, x, y, self.selected_tool)
            elif self.selected_tool == "Buffer":
                gate = BufferGate(self.design_area, x, y, self.selected_tool)
            elif self.selected_tool == "NAND Gate":
                gate = NANDGate(self.design_area, x, y, self.selected_tool)
            elif self.selected_tool == "NOR Gate":
                gate = NORGate(self.design_area, x, y, self.selected_tool)
            elif self.selected_tool == "XOR Gate":
                gate = XORGate(self.design_area, x, y, self.selected_tool)
            elif self.selected_tool == "XNOR Gate":
                gate = XNORGate(self.design_area, x, y, self.selected_tool)
            if gate:
                self.gates.append(gate)
            elif self.selected_tool == "Giriş Kutusu":
                input_box = InputBox(self.design_area, x, y)
                self.inputs.append(input_box)
            elif self.selected_tool == "Çıkış Kutusu":
                output_box = OutputBox(self.design_area, x, y)
                self.outputs.append(output_box)
            elif self.selected_tool == "Led":
                led = LED(self.design_area, x, y)
                self.leds.append(led)
            elif self.selected_tool == "Bağlantı Düğümü":
                node = Node(self.design_area, x, y)
                self.nodes.append(node)
            self.selected_tool = None

    def start_connection(self, event):
        # Bağlantıyı başlatır
        if self.selected_tool == "Çizgi Çizme":
            self.start_x, self.start_y = event.x, event.y
            self.line = self.design_area.create_line(self.start_x, self.start_y, self.start_x, self.start_y)

            self.design_area.bind("<Motion>", self.draw_connection)
            self.design_area.bind("<ButtonRelease-1>", self.finish_connection)
        elif event.widget.find_withtag("current"):
            self.start_x, self.start_y = event.x, event.y
            self.line = self.design_area.create_line(self.start_x, self.start_y, self.start_x, self.start_y)

            self.design_area.bind("<Motion>", self.draw_connection)
            self.design_area.bind("<ButtonRelease-3>", self.finish_connection)

    def draw_connection(self, event):
        # Bağlantıyı çizer
        self.design_area.coords(self.line, self.start_x, self.start_y, event.x, event.y)

    def finish_connection(self, event):
        # Bağlantıyı bitirir
        self.design_area.unbind("<Motion>")
        self.design_area.unbind("<ButtonRelease-1>")
        self.design_area.unbind("<ButtonRelease-3>")

        self.end_x, self.end_y = event.x, event.y
        self.design_area.coords(self.line, self.start_x, self.start_y, self.end_x, self.end_y)
        connection = Connection(self.design_area, self.start_x, self.start_y, self.end_x, self.end_y, label_visible=self.selected_tool == "Çizgi Çizme")
        self.connections.append(connection)

    def create_control_buttons(self):
        # Kontrol tuşlarını oluşturur
        ttk.Label(self.control_frame, text="Kontrol Tuşları").grid(row=0, column=0, pady=5)

        ttk.Button(self.control_frame, text="Çalıştır", command=self.run_simulation).grid(row=1, column=0, pady=2)
        ttk.Button(self.control_frame, text="Reset", command=self.reset_simulation).grid(row=2, column=0, pady=2)
        ttk.Button(self.control_frame, text="Durdur", command=self.stop_simulation).grid(row=3, column=0, pady=2)

    def run_simulation(self):
        # Simülasyonu başlatır
        print("Simülasyon başlatıldı.")
        input_values = [int(entry.entry.get()) for entry in self.inputs]
        print("Giriş değerleri: ", input_values)

        for gate in self.gates:
            if isinstance(gate, BinaryGate):
                if len(input_values) >= 2:
                    gate.set_input1(input_values.pop(0))
                    gate.set_input2(input_values.pop(0))
            elif isinstance(gate, UnaryGate):
                if len(input_values) >= 1:
                    gate.set_input(input_values.pop(0))

            gate.perform_gate_logic()
            print(f"{gate.gate_type} çıkışı: {gate.get_output()}")

        output_values = [gate.get_output() for gate in self.gates]
        print("Çıkış değerleri: ", output_values)

        for entry, value in zip(self.outputs, output_values):
            entry.entry.delete(0, tk.END)
            entry.entry.insert(0, str(value))

        for led, value in zip(self.leds, output_values):
            led.set_value(value)

    def reset_simulation(self):
        # Simülasyonu sıfırlar
        print("Simülasyon sıfırlandı.")
        self.design_area.delete("all")
        self.elements = []
        self.gates = []
        self.inputs = []
        self.outputs = []
        self.leds = []
        self.connections = []
        self.nodes = []

    def stop_simulation(self):
        print("Simülasyon durduruldu.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicDesignApp(root)
    root.mainloop()
