import tkinter as tk
from tkinter import messagebox

class Island:
    def __init__(self, x, y, bridges_needed):
        self.x = x
        self.y = y
        self.bridges_needed = bridges_needed
        self.bridges_connected = 0

    def can_add_bridge(self):
        return self.bridges_connected < self.bridges_needed
    
    def add_bridge(self):
        if self.can_add_bridge():
            self.bridges_connected += 1
        else:
            raise Exception(f"Island at ({self.x}, {self.y}) ya tiene suficientes puentes.")
    
    def remove_bridge(self):
        if self.bridges_connected > 0:
            self.bridges_connected -= 1
        else:
            raise Exception(f"Island at ({self.x}, {self.y}) no tiene puentes para eliminar.")

class Bridge:
    def __init__(self, island1, island2, count=1):
        self.island1 = island1
        self.island2 = island2
        self.count = count

class HashiGame(tk.Tk):
    def __init__(self, islands, n_rows, n_cols):
        super().__init__()
        self.title("Hashi Game")
        self.islands = islands
        self.bridges = []
        self.selected_island = None
        self.cell_size = 50  # Tamaño de cada celda
        self.canvas_width = n_cols * self.cell_size
        self.canvas_height = n_rows * self.cell_size
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.draw_board()
        
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

    @classmethod
    def load_from_file(cls, file_path):
        islands = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
            dimensions = lines[0].strip().split(',')
            n_rows = int(dimensions[0])
            n_cols = int(dimensions[1])

            if n_rows <= 0 or n_cols <= 0:
                raise ValueError("Las dimensiones del tablero deben ser mayores que cero.")

            for i in range(n_rows):
                if i + 1 >= len(lines):
                    raise ValueError(f"Faltan filas en el archivo para la fila {i + 1}.")
                
                row = list(map(int, lines[i + 1].strip()))

                if len(row) != n_cols:
                    raise ValueError(f"La fila {i + 1} no tiene el número correcto de columnas. Esperado: {n_cols}, Encontrado: {len(row)}")

                for j in range(n_cols):
                    if row[j] < 0:
                        raise ValueError(f"La isla en ({j}, {i}) tiene un número negativo de puentes.")
                    if row[j] > 0:
                        islands.append(Island(j, i, row[j]))

        return cls(islands, n_rows, n_cols)

    def draw_board(self):
        self.canvas.delete("all")
        for island in self.islands:
            x, y = island.x * self.cell_size + self.cell_size // 2, island.y * self.cell_size + self.cell_size // 2
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="lightblue")
            self.canvas.create_text(x, y, text=str(island.bridges_needed), font=("Arial", 14))
        
        for bridge in self.bridges:
            self.draw_bridge(bridge.island1, bridge.island2, bridge.count)
    
    def draw_bridge(self, island1, island2, count):
        x1, y1 = island1.x * self.cell_size + self.cell_size // 2, island1.y * self.cell_size + self.cell_size // 2
        x2, y2 = island2.x * self.cell_size + self.cell_size // 2, island2.y * self.cell_size + self.cell_size // 2
        offset = 5 if count == 2 else 0

        if island1.x == island2.x:
            self.canvas.create_line(x1 - offset, y1, x2 - offset, y2, fill="black", width=5)
            if count == 2:
                self.canvas.create_line(x1 + offset, y1, x2 + offset, y2, fill="black", width=5)
        elif island1.y == island2.y:
            self.canvas.create_line(x1, y1 - offset, x2, y2 - offset, fill="black", width=5)
            if count == 2:
                self.canvas.create_line(x1, y1 + offset, x2, y2 + offset, fill="black", width=5)
    
    def draw_bridge(self, island1, island2, count):
        x1, y1 = island1.x * self.cell_size + self.cell_size // 2, island1.y * self.cell_size + self.cell_size // 2
        x2, y2 = island2.x * self.cell_size + self.cell_size // 2, island2.y * self.cell_size + self.cell_size // 2
        offset = 5 if count == 2 else 0

        if island1.x == island2.x:
            self.canvas.create_line(x1 - offset, y1, x2 - offset, y2, fill="black", width=5)
            if count == 2:
                self.canvas.create_line(x1 + offset, y1, x2 + offset, y2, fill="black", width=5)
        elif island1.y == island2.y:
            self.canvas.create_line(x1, y1 - offset, x2, y2 - offset, fill="black", width=5)
            if count == 2:
                self.canvas.create_line(x1, y1 + offset, x2, y2 + offset, fill="black", width=5)
    
    def find_island(self, x, y):
        for island in self.islands:
            ix, iy = island.x * self.cell_size + self.cell_size // 2, island.y * self.cell_size + self.cell_size // 2
            if (x - ix) ** 2 + (y - iy) ** 2 <= 400:
                return island
        return None
    
    def find_bridge(self, island1, island2):
        for bridge in self.bridges:
            if (bridge.island1 == island1 and bridge.island2 == island2) or \
               (bridge.island1 == island2 and bridge.island2 == island1):
                return bridge
        return None

    def on_left_click(self, event):
        x, y = event.x, event.y
        clicked_island = self.find_island(x, y)
        if clicked_island:
            if self.selected_island:
                try:
                    if self.selected_island == clicked_island:
                        self.selected_island = None
                        return

                    bridge = self.find_bridge(self.selected_island, clicked_island)
                    if bridge:
                        if bridge.count < 2 and self.is_valid_connection(self.selected_island, clicked_island, bridge):
                            self.connect_islands(self.selected_island, clicked_island, bridge)
                    elif self.is_valid_connection(self.selected_island, clicked_island, None):
                        self.connect_islands(self.selected_island, clicked_island)

                    self.selected_island = None
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            else:
                self.selected_island = clicked_island

    def on_right_click(self, event):
        x, y = event.x, event.y
        clicked_island = self.find_island(x, y)
        if clicked_island:
            if self.selected_island:
                try:
                    if self.selected_island == clicked_island:
                        self.selected_island = None
                        return

                    bridge = self.find_bridge(self.selected_island, clicked_island)
                    if bridge and self.is_valid_connection(self.selected_island, clicked_island, bridge):
                        self.disconnect_islands(self.selected_island, clicked_island, bridge)

                    self.selected_island = None
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            else:
                self.selected_island = clicked_island

    def connect_islands(self, island1, island2, existing_bridge=None):
        if not self.is_valid_connection(island1, island2, existing_bridge):
            raise Exception("No se pueden conectar estas islas: Puente cruzado no permitido.")
        
        if existing_bridge:
            if existing_bridge.count < 2:
                existing_bridge.count += 1
                island1.add_bridge()
                island2.add_bridge()
            else:
                raise Exception("Ya hay dos puentes entre estas islas.")
        else:
            island1.add_bridge()
            island2.add_bridge()
            self.bridges.append(Bridge(island1, island2, count=1))
        
        self.draw_board()


    
    def is_game_complete(self):
            """Verifica si todas las islas están conectadas y tienen el número correcto de puentes."""
            # Verifica si cada isla tiene el número correcto de puentes
            if not all(island.bridges_connected == island.bridges_needed for island in self.islands):
                return False

            # Verificar conectividad de islas
            if not self.islands:  # Si no hay islas, el juego no puede estar completo
                return False

            # Comenzar desde la primera isla
            visited = set()
            self.dfs(self.islands[0], visited)

            # Verificar si todas las islas han sido visitadas
            return len(visited) == len(self.islands)

        def dfs(self, island, visited):
            """Realiza una búsqueda en profundidad para marcar islas conectadas como visitadas."""
            visited.add(island)

            # Recorrer todos los puentes para encontrar islas conectadas
            for bridge in self.bridges:
                if bridge.island1 == island and bridge.island2 not in visited:
                    self.dfs(bridge.island2, visited)
                elif bridge.island2 == island and bridge.island1 not in visited:
                    self.dfs(bridge.island1, visited)

        def check_game_completion(self):
            if self.is_game_complete():
                messagebox.showinfo("¡Ganaste!", "¡Felicidades, has completado el juego!")
    
    def disconnect_islands(self, island1, island2, bridge):
        if bridge.count > 1:
            bridge.count -= 1
        else:
            self.bridges.remove(bridge)
        island1.remove_bridge()
        island2.remove_bridge()
        self.draw_board()

    def is_valid_connection(self, island1, island2, existing_bridge):
        # Si ya hay un puente entre estas dos islas, permite un segundo puente (puente doble)
        if existing_bridge:
            return existing_bridge.count < 2  # Permitir solo hasta dos puentes entre las mismas islas

        # Validación de puentes verticales (mismo x)
        if island1.x == island2.x:
            min_y = min(island1.y, island2.y)
            max_y = max(island1.y, island2.y)
            # Comprobar si hay islas intermedias en la columna
            for island in self.islands:
                if island.x == island1.x and min_y < island.y < max_y:
                    return False

        # Validación de puentes horizontales (mismo y)
        elif island1.y == island2.y:
            min_x = min(island1.x, island2.x)
            max_x = max(island1.x, island2.x)
            # Comprobar si hay islas intermedias en la fila
            for island in self.islands:
                if island.y == island1.y and min_x < island.x < max_x:
                    return False

        return True

    def is_game_complete(self):
        return all(island.bridges_connected == island.bridges_needed for island in self.islands)

if __name__ == "__main__":
    game = HashiGame.load_from_file("tablero.txt")
    game.mainloop()
