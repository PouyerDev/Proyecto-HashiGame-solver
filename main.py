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

        # Eventos de clic
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # Botón para resolver automáticamente
        self.backtrack_button = tk.Button(self, text="Resolver con Backtracking", command=self.solve_with_backtracking)
        self.backtrack_button.pack(pady=10)



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
        
        # Resaltar la isla seleccionada
        if self.selected_island:
            self.highlight_island(self.selected_island)
    
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
     
        # Verificar que cada isla tenga el número exacto de puentes conectados
        if not all(island.bridges_connected == island.bridges_needed for island in self.islands):
            return False

        # Verificar que todas las islas formen un único grafo conectado
        if not self.islands:  # Si no hay islas, el juego no puede estar completo
            return False

        # Comenzar desde la primera isla y verificar la conectividad
        visited = set()
        self.dfs(self.islands[0], visited)

        # Verificar si todas las islas han sido visitadas
        return len(visited) == len(self.islands)

    def dfs(self, island, visited):
        
        #Realiza una búsqueda en profundidad para marcar islas conectadas como visitadas.
        
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

    def is_valid_connection(self, island1, island2, existing_bridge=None):
        if existing_bridge:
            return True  # Si ya hay un puente, no es necesario verificar.

        # Verificar si hay islas intermedias entre las dos islas en línea recta
        if island1.x == island2.x:  # Conexión vertical
            min_y, max_y = sorted([island1.y, island2.y])
            for island in self.islands:
                if island.x == island1.x and min_y < island.y < max_y:
                    return False
        elif island1.y == island2.y:  # Conexión horizontal
            min_x, max_x = sorted([island1.x, island2.x])
            for island in self.islands:
                if island.y == island1.y and min_x < island.x < max_x:
                    return False

        # Verificar si el puente cruza otros puentes
        for bridge in self.bridges:
            if self.do_bridges_cross(island1, island2, bridge.island1, bridge.island2):
                return False

        return True


    def do_bridges_cross(self, island1, island2, other_island1, other_island2):
        # Verificar si los puentes son paralelos y no comparten un eje
        if (island1.x == island2.x and other_island1.x == other_island2.x and island1.x != other_island1.x) or \
        (island1.y == island2.y and other_island1.y == other_island2.y and island1.y != other_island1.y):
            return False

        # Verificar intersecciones en líneas horizontales o verticales
        if island1.x == island2.x:  # Puente vertical
            if other_island1.y == other_island2.y:  # Otro puente horizontal
                if min(island1.y, island2.y) < other_island1.y < max(island1.y, island2.y) and \
                min(other_island1.x, other_island2.x) < island1.x < max(other_island1.x, other_island2.x):
                    return True
        elif island1.y == island2.y:  # Puente horizontal
            if other_island1.x == other_island2.x:  # Otro puente vertical
                if min(island1.x, island2.x) < other_island1.x < max(island1.x, island2.x) and \
                min(other_island1.y, other_island2.y) < island1.y < max(other_island1.y, other_island2.y):
                    return True

        return False

    def is_game_complete(self):
        return all(island.bridges_connected == island.bridges_needed for island in self.islands)

    def highlight_island(self, island):
        # Método para resaltar la isla seleccionada
        x = island.x * self.cell_size + self.cell_size // 2
        y = island.y * self.cell_size + self.cell_size // 2
        radius = 10  # Ajusta el radio según sea necesario
        self.canvas.create_oval(x - radius - 5, y - radius - 5, x + radius + 5, y + radius + 5, outline="red", width=3)

    def on_island_click(self, clicked_island):
        if self.selected_island:
            try:
                bridge = self.find_bridge(self.selected_island, clicked_island)
                if bridge:
                    self.disconnect_islands(self.selected_island, clicked_island, bridge)
                else:
                    self.connect_islands(self.selected_island, clicked_island)
                self.selected_island = None
                self.draw_board()  # Mover la llamada aquí
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.selected_island = None  # Deseleccionar la isla en caso de error
        else:
            self.selected_island = clicked_island
            self.draw_board()  # Mover la llamada aquí para resaltar la isla seleccionada





################################### JUGADOR IA ###############################################


    def solve_with_backtracking(self):

        if self.backtrack():
            messagebox.showinfo("Jugador Sintético", "¡El jugador sintético ha resuelto el juego!")
        else:
            messagebox.showerror("Jugador Sintético", "No se pudo resolver el tablero.")
        self.draw_board()


    def backtrack(self, visited_states=None):

        # Inicializar el historial de estados
        if visited_states is None:
            visited_states = set()

        # Si el juego está completo, terminamos
        if self.is_game_complete():
            return True

        # Serializar el estado actual de los puentes como una tupla para evitar repetición
        current_state = tuple(sorted((bridge.island1.x, bridge.island1.y, bridge.island2.x, bridge.island2.y, bridge.count)
                                    for bridge in self.bridges))

        # Si este estado ya fue visitado, ignorarlo
        if current_state in visited_states:
            return False

        # Marcar el estado como visitado
        visited_states.add(current_state)

        # Intentar todas las conexiones posibles
        for island1 in self.islands:
            if island1.bridges_connected == island1.bridges_needed:
                continue  # Saltar islas completas

            for island2 in self.islands:
                if island1 == island2 or island2.bridges_connected == island2.bridges_needed:
                    continue

                # Verificar conexiones horizontales y verticales válidas
                if (island1.x == island2.x or island1.y == island2.y) and self.is_valid_connection(island1, island2):
                    bridge = self.find_bridge(island1, island2)
                    try:
                        # Intentar agregar un puente
                        if not bridge:
                            self.connect_islands(island1, island2)
                        elif bridge.count < 2:
                            self.connect_islands(island1, island2, bridge)

                        # Mostrar el paso actual en la interfaz
                        self.draw_board()
                        self.update()
                        self.after(200)  # Pausa breve para visualizar el cambio

                        # Llamada recursiva
                        if self.backtrack(visited_states):
                            return True

                        # Si no fue exitoso, retroceder
                        self.disconnect_islands(island1, island2, bridge)

                        # Mostrar la retrocesión en la interfaz
                        self.draw_board()
                        self.update()
                        self.after(200)
                    except Exception:
                        continue

        # Si no hay soluciones, retroceder
        return False



######################################## MAIN ####################################################
if __name__ == "__main__":
    game = HashiGame.load_from_file("tablero.txt")
    game.mainloop()
