import tkinter as tk
from tkinter import ttk, messagebox
import random
import os

# Intento de importar Firebase (Manejo de entorno)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

# ==========================================
# MOTOR DE BASE DE DATOS (FIREBASE / MOCK)
# ==========================================
class MotorBaseDatos:
    def __init__(self):
        self.usar_mock = True
        self.db = None
        
        # Base de datos simulada en memoria (Mock) por si no hay credenciales
        self.mock_db = {
            "cursos": [
                {"id": 101, "nombre": "Matemáticas Básicas", "relevancia": 85, "dificultad": 3},
                {"id": 102, "nombre": "Programación en Python", "relevancia": 95, "dificultad": 5},
                {"id": 103, "nombre": "Historia del Arte", "relevancia": 60, "dificultad": 2},
                {"id": 104, "nombre": "Física Cuántica", "relevancia": 90, "dificultad": 9},
                {"id": 105, "nombre": "Estructuras de Datos", "relevancia": 99, "dificultad": 8}
            ],
            "progresos": []
        }

        if FIREBASE_AVAILABLE and os.path.exists("serviceAccountKey.json"):
            try:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.usar_mock = False
                print("Conectado a Firebase exitosamente.")
            except Exception as e:
                print(f"Error al conectar a Firebase: {e}. Usando modo simulado.")
        else:
            print("No se encontró serviceAccountKey.json o firebase_admin no está instalado. Usando BD simulada.")

    def obtener_cursos(self):
        if not self.usar_mock:
            # Lógica real de Firebase
            docs = self.db.collection('cursos').stream()
            return [doc.to_dict() for doc in docs]
        return self.mock_db["cursos"]

    def guardar_progreso(self, estudiante, modulo):
        if not self.usar_mock:
            # Lógica real de Firebase
            self.db.collection('progresos').add({"estudiante": estudiante, "modulo": modulo})
        else:
            self.mock_db["progresos"].append({"estudiante": estudiante, "modulo": modulo})

# ==========================================
# 1. ESTRUCTURA LINEAL: COLA (QUEUE)
# Para guardar progresos en tiempo real (FIFO)
# ==========================================
class ColaProgreso:
    def __init__(self):
        self.items = []

    def encolar(self, progreso):
        self.items.insert(0, progreso) # Inserta al principio

    def desencolar(self):
        if not self.esta_vacia():
            return self.items.pop() # Saca del final (El más antiguo)
        return None

    def esta_vacia(self):
        return len(self.items) == 0

# ==========================================
# 2. ESTRUCTURA NO LINEAL: GRAFO (GRAPH)
# Para detectar patrones de abandono
# ==========================================
class GrafoRendimiento:
    def __init__(self):
        # Diccionario de adyacencia {modulo: {modulo_siguiente: tasa_abandono}}
        self.grafo = {}

    def agregar_transicion(self, modulo_origen, modulo_destino, tasa_abandono):
        if modulo_origen not screening in self.grafo:
            self.grafo[modulo_origen] = {}
        self.grafo[modulo_origen][modulo_destino] = tasa_abandono

    def detectar_cuellos_botella(self, umbral=50):
        # Busca aristas (transiciones) con una tasa de abandono mayor al umbral
        alertas = []
        for origen, destinos in self.grafo.items():
            for destino, abandono in destinos.items():
                if abandono >= umbral:
                    alertas.append(f"Alerta: {abandono}% de abandono entre '{origen}' y '{destino}'")
        return alertas

# ==========================================
# 3. MÉTODO DE ORDENAMIENTO: QUICK SORT
# Para sugerir cursos personalizados (por relevancia)
# ==========================================
def quicksort_cursos(arr, clave="relevancia"):
    if len(arr) <= 1:
        return arr
    pivote = arr[len(arr) // 2]
    izq = [x for x in arr if x[clave] > pivote[clave]] # Mayor a menor
    medio = [x for x in arr if x[clave] == pivote[clave]]
    der = [x for x in arr if x[clave] < pivote[clave]]
    return quicksort_cursos(izq, clave) + medio + quicksort_cursos(der, clave)

# ==========================================
# 4. MÉTODO DE BÚSQUEDA: BÚSQUEDA BINARIA
# ==========================================
def busqueda_binaria_curso(arr, id_curso):
    # Requiere que el arreglo esté ordenado por ID previamente (menor a mayor)
    inicio = 0
    fin = len(arr) - 1
    
    while inicio <= fin:
        medio = (inicio + fin) // 2
        if arr[medio]['id'] == id_curso:
            return arr[medio]
        elif arr[medio]['id'] < id_curso:
            inicio = medio + 1
        else:
            fin = medio - 1
    return None

# ==========================================
# 5. RECURSIVIDAD
# Para recuperar tareas o módulos completados en forma de árbol de dependencias
# ==========================================
def recuperar_historial_recursivo(modulo_actual, historial_completo, nivel=0):
    """
    Simula la búsqueda recursiva de módulos completados (ej. pre-requisitos).
    'historial_completo' es un diccionario simulado de dependencias.
    """
    resultado = "  " * nivel + f"- Módulo Completado: {modulo_actual}\n"
    if modulo_actual in historial_completo:
        for sub_modulo in historial_completo[modulo_actual]:
            resultado += recuperar_historial_recursivo(sub_modulo, historial_completo, nivel + 1)
    return resultado


# ==========================================
# INTERFAZ GRÁFICA (TKINTER)
# ==========================================
class AplicacionAprendizaje(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Plataforma Educativa Personalizada")
        self.geometry("700x500")
        
        self.db = MotorBaseDatos()
        self.cola_progreso = ColaProgreso()
        
        # Inicializar Grafo con datos dummy para detectar abandonos
        self.grafo_rendimiento = GrafoRendimiento()
        self.grafo_rendimiento.agregar_transicion("Módulo 1", "Módulo 2", 10)
        self.grafo_rendimiento.agregar_transicion("Módulo 2", "Módulo 3", 65) # Cuello de botella
        self.grafo_rendimiento.agregar_transicion("Módulo 3", "Módulo 4", 15)

        self.crear_widgets()

    def crear_widgets(self):
        # Crear sistema de pestañas
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, expand=True, fill='both')

        # Pestañas
        frame_cursos = ttk.Frame(notebook)
        frame_progreso = ttk.Frame(notebook)
        frame_abandono = ttk.Frame(notebook)
        frame_historial = ttk.Frame(notebook)

        notebook.add(frame_cursos, text="Cursos (Orden/Búsqueda)")
        notebook.add(frame_progreso, text="Progreso (Cola/Lineal)")
        notebook.add(frame_abandono, text="Análisis (Grafo/No Lineal)")
        notebook.add(frame_historial, text="Historial (Recursividad)")

        self.construir_pestana_cursos(frame_cursos)
        self.construir_pestana_progreso(frame_progreso)
        self.construir_pestana_abandono(frame_abandono)
        self.construir_pestana_historial(frame_historial)

        # Footer con la información personalizada
        footer = tk.Label(self, text="¿Dudas con tu inscripción? Recursos Humanos Universidad Cesun - Ext 330", 
                          fg="gray", font=("Arial", 9, "italic"))
        footer.pack(side="bottom", pady=10)

    # --- PESTAÑA 1: CURSOS (SORT & SEARCH) ---
    def construir_pestana_cursos(self, frame):
        lbl = tk.Label(frame, text="Sugerencias de Cursos (Ordenados por QuickSort)", font=("Arial", 12, "bold"))
        lbl.pack(pady=5)

        self.lista_cursos = tk.Listbox(frame, width=70, height=8)
        self.lista_cursos.pack(pady=5)

        btn_ordenar = tk.Button(frame, text="Cargar y Ordenar por Relevancia", command=self.mostrar_cursos_ordenados)
        btn_ordenar.pack(pady=5)

        frame_busqueda = tk.Frame(frame)
        frame_busqueda.pack(pady=10)
        
        tk.Label(frame_busqueda, text="Buscar ID de Curso (Búsqueda Binaria):").pack(side="left")
        self.entry_busqueda = tk.Entry(frame_busqueda, width=10)
        self.entry_busqueda.pack(side="left", padx=5)
        
        btn_buscar = tk.Button(frame_busqueda, text="Buscar", command=self.buscar_curso)
        btn_buscar.pack(side="left")

    def mostrar_cursos_ordenados(self):
        self.lista_cursos.delete(0, tk.END)
        cursos = self.db.obtener_cursos()
        # Ordenar usando QuickSort
        cursos_ordenados = quicksort_cursos(cursos, "relevancia")
        
        for c in cursos_ordenados:
            self.lista_cursos.insert(tk.END, f"ID: {c['id']} | {c['nombre']} | Relevancia: {c['relevancia']}")

    def buscar_curso(self):
        id_buscar = self.entry_busqueda.get()
        if not id_buscar.isdigit():
            messagebox.showwarning("Error", "Ingrese un ID numérico válido.")
            return

        cursos = self.db.obtener_cursos()
        # Para búsqueda binaria, primero debemos ordenar por ID (menor a mayor)
        cursos_ordenados_id = sorted(cursos, key=lambda x: x['id']) 
        
        resultado = busqueda_binaria_curso(cursos_ordenados_id, int(id_buscar))
        if resultado:
            messagebox.showinfo("Resultado", f"Curso Encontrado:\n{resultado['nombre']}\nDificultad: {resultado['dificultad']}")
        else:
            messagebox.showinfo("Resultado", "Curso no encontrado.")

    # --- PESTAÑA 2: PROGRESO (LINEAR - QUEUE) ---
    def construir_pestana_progreso(self, frame):
        lbl = tk.Label(frame, text="Cola de Guardado en Tiempo Real (FIFO)", font=("Arial", 12, "bold"))
        lbl.pack(pady=5)

        self.txt_cola = tk.Text(frame, width=60, height=10, state="disabled")
        self.txt_cola.pack(pady=5)

        frame_botones = tk.Frame(frame)
        frame_botones.pack(pady=10)

        btn_simular = tk.Button(frame_botones, text="Simular Actividad (Encolar)", command=self.encolar_actividad)
        btn_simular.pack(side="left", padx=5)

        btn_procesar = tk.Button(frame_botones, text="Sincronizar a BD (Desencolar)", command=self.procesar_cola)
        btn_procesar.pack(side="left", padx=5)

    def actualizar_vista_cola(self):
        self.txt_cola.config(state="normal")
        self.txt_cola.delete("1.0", tk.END)
        for i, item in enumerate(self.cola_progreso.items):
            self.txt_cola.insert(tk.END, f"Posición {i+1}: {item['estudiante']} completó {item['modulo']}\n")
        self.txt_cola.config(state="disabled")

    def encolar_actividad(self):
        modulo_random = f"Módulo {random.randint(1, 10)}"
        self.cola_progreso.encolar({"estudiante": "Juan_Perez", "modulo": modulo_random})
        self.actualizar_vista_cola()

    def procesar_cola(self):
        if self.cola_progreso.esta_vacia():
            messagebox.showinfo("Cola Vacia", "No hay progresos pendientes por sincronizar.")
            return

        elemento = self.cola_progreso.desencolar()
        # Guardar en base de datos
        self.db.guardar_progreso(elemento["estudiante"], elemento["modulo"])
        self.actualizar_vista_cola()
        messagebox.showinfo("Sincronización Exitosa", f"Sincronizado en Firebase:\n{elemento}")

    # --- PESTAÑA 3: ABANDONO (NON-LINEAR - GRAPH) ---
    def construir_pestana_abandono(self, frame):
        lbl = tk.Label(frame, text="Detección de Patrones (Grafo No Lineal)", font=("Arial", 12, "bold"))
        lbl.pack(pady=5)
        
        info = tk.Label(frame, text="El sistema modela los cursos como nodos de un grafo.\nEl peso de las aristas es la tasa de abandono entre un módulo y otro.", justify="center")
        info.pack(pady=5)

        self.txt_alertas = tk.Text(frame, width=60, height=8, fg="red")
        self.txt_alertas.pack(pady=5)

        btn_analizar = tk.Button(frame, text="Analizar Cuellos de Botella (>50% Abandono)", command=self.analizar_grafo)
        btn_analizar.pack(pady=5)

    def analizar_grafo(self):
        alertas = self.grafo_rendimiento.detectar_cuellos_botella(umbral=50)
        self.txt_alertas.delete("1.0", tk.END)
        if alertas:
            for alerta in alertas:
                self.txt_alertas.insert(tk.END, alerta + "\n")
        else:
            self.txt_alertas.insert(tk.END, "El flujo de estudiantes es óptimo. Sin alertas.")

    # --- PESTAÑA 4: HISTORIAL (RECURSION) ---
    def construir_pestana_historial(self, frame):
        lbl = tk.Label(frame, text="Recuperación de Historial (Algoritmo Recursivo)", font=("Arial", 12, "bold"))
        lbl.pack(pady=5)

        btn_recuperar = tk.Button(frame, text="Generar Árbol de Módulos Completados", command=self.mostrar_historial)
        btn_recuperar.pack(pady=5)

        self.txt_historial = tk.Text(frame, width=60, height=12)
        self.txt_historial.pack(pady=5)

    def mostrar_historial(self):
        # Diccionario simulando un árbol de dependencias de módulos completados
        dependencias_completadas = {
            "Proyecto Final": ["Desarrollo Backend", "Desarrollo Frontend"],
            "Desarrollo Backend": ["Bases de Datos", "Lógica de Programación"],
            "Desarrollo Frontend": ["Diseño UI/UX"]
        }
        
        self.txt_historial.delete("1.0", tk.END)
        resultado_recursivo = recuperar_historial_recursivo("Proyecto Final", dependencias_completadas)
        self.txt_historial.insert(tk.END, "Ruta de aprendizaje completada:\n\n" + resultado_recursivo)

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    app = AplicacionAprendizaje()
    app.mainloop()