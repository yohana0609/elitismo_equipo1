"""
Sesion 1 - Reto Practico: El Optimizador Perfecto

Implementa y compara 3 transformaciones de fitness con 3 niveles de
elitismo para minimizar la funcion Rastrigin en 10 dimensiones.

Archivos generados:
- equipo_1_resultados.csv
- equipo_1_grafica.png
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib
# Configura el backend de Matplotlib para generar archivos sin abrir ventanas
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==========================================
# PARÁMETROS FIJOS (Configuración del AG)
# ==========================================
POBLACION = 50
GENERACIONES = 100
LONGITUD_CROMOSOMA = 10  # Número de variables/genes por individuo
PROB_CRUZAMIENTO = 0.8
PROB_MUTACION = 0.01
TIPO_SELECCION = "torneo"
TIPO_CRUZAMIENTO = "un_punto"
TIPO_MUTACION = "uniforme"
TAMANO_TORNEO = 3
SEMILLA = 42

# Límites del espacio de búsqueda (Rango de los genes)
LIMITE_INFERIOR = -5.12
LIMITE_SUPERIOR = 5.12

# Opciones para experimentación
TRANSFORMACIONES = ("Inversion", "Negacion", "Ranking")
NIVELES_ELITISMO = (0, 2, 5)

# Gestión de rutas de archivos
BASE_DIR = Path(__file__).resolve().parent
CSV_SALIDA = BASE_DIR / "equipo_1_resultados.csv"
GRAFICA_SALIDA = BASE_DIR / "equipo_1_grafica.png"


@dataclass
class Individuo:
    """Representa una solucion candidata del algoritmo genetico."""

    cromosoma: np.ndarray
    valor_objetivo: float = 0.0
    fitness: float = 0.0

    def copiar(self) -> "Individuo":
        return Individuo(
            cromosoma=self.cromosoma.copy(),
            valor_objetivo=self.valor_objetivo,
            fitness=self.fitness,
        )


def rastrigin(x):
    """
    Funcion Rastrigin para minimizacion.

    Args:
        x: array de 10 valores en el rango [-5.12, 5.12]

    Returns:
        float: valor de la funcion (menor es mejor)
    """
    A = 10
    n = len(x)
    return A * n + sum(x**2 - A * np.cos(2 * np.pi * x))


def fitness_inversion(valor_objetivo):
    """
    Transforma minimizacion en maximizacion usando inversion.

    Args:
        valor_objetivo (float): Valor de la funcion Rastrigin

    Returns:
        float: Fitness transformado (mayor es mejor)
    """
    return 1.0 / (1.0 + valor_objetivo)


def fitness_negacion(valor_objetivo, c_max):
    """
    Transforma usando negacion con desplazamiento.

    Args:
        valor_objetivo (float): Valor de la funcion Rastrigin
        c_max (float): Constante maxima (max de la poblacion * 1.1)

    Returns:
        float: Fitness transformado
    """
    return max(0, c_max - valor_objetivo)


def fitness_ranking(poblacion, sp=1.5):
    """
    Asigna fitness basado en ranking de la poblacion.

    Args:
        poblacion (list): Lista de individuos ordenados por valor objetivo,
            del peor al mejor para que el mejor reciba mayor fitness.
        sp (float): Presion selectiva (1 < sp <= 2)

    Returns:
        dict: Mapeo de indice a fitness
    """
    N = len(poblacion)
    fitness_dict = {}

    if N == 1:
        fitness_dict[0] = 1.0
        return fitness_dict

    for rank in range(1, N + 1):
        fitness = 2 - sp + 2 * (sp - 1) * (rank - 1) / (N - 1)
        fitness_dict[rank - 1] = fitness
    return fitness_dict


def crear_poblacion_inicial():
    """Genera la poblacion inicial con codificacion real directa."""
    return [
        Individuo(
            cromosoma=np.random.uniform(
                LIMITE_INFERIOR,
                LIMITE_SUPERIOR,
                LONGITUD_CROMOSOMA,
            )
        )
        for _ in range(POBLACION)
    ]


def evaluar_objetivo(poblacion):
    """Calcula el valor objetivo de Rastrigin para cada individuo."""
    for individuo in poblacion:
        individuo.valor_objetivo = float(rastrigin(individuo.cromosoma))


def asignar_fitness(poblacion, transformacion):
    """Evalua el objetivo y asigna el fitness segun la transformacion."""
    evaluar_objetivo(poblacion)

    if transformacion == "Inversion":
        for individuo in poblacion:
            individuo.fitness = float(fitness_inversion(individuo.valor_objetivo))
        return

    if transformacion == "Negacion":
        c_max = max(ind.valor_objetivo for ind in poblacion) * 1.1
        for individuo in poblacion:
            individuo.fitness = float(
                fitness_negacion(individuo.valor_objetivo, c_max)
            )
        return

    if transformacion == "Ranking":
        # Rastrigin se minimiza: el peor tiene mayor valor objetivo.
        poblacion_ordenada = sorted(
            poblacion,
            key=lambda ind: ind.valor_objetivo,
            reverse=True,
        )
        fitness_por_rank = fitness_ranking(poblacion_ordenada, sp=1.5)
        for rank, individuo in enumerate(poblacion_ordenada):
            individuo.fitness = float(fitness_por_rank[rank])
        return

    raise ValueError(f"Transformacion no reconocida: {transformacion}")


def seleccion_torneo(poblacion, k=TAMANO_TORNEO):
    """Selecciona un padre por torneo de tamano k=3."""
    indices = np.random.choice(len(poblacion), size=k, replace=False)
    candidatos = [poblacion[indice] for indice in indices]
    ganador = max(candidatos, key=lambda ind: ind.fitness)
    return ganador.copiar()


def cruzamiento_un_punto(padre_1, padre_2):
    """Aplica cruzamiento de un punto a cromosomas reales."""
    if np.random.random() >= PROB_CRUZAMIENTO:
        return padre_1.copy(), padre_2.copy()

    punto = np.random.randint(1, LONGITUD_CROMOSOMA)
    hijo_1 = np.concatenate((padre_1[:punto], padre_2[punto:]))
    hijo_2 = np.concatenate((padre_2[:punto], padre_1[punto:]))
    return hijo_1, hijo_2


def mutacion_uniforme(cromosoma):
    """Reemplaza genes por valores uniformes dentro del dominio."""
    mutado = cromosoma.copy()
    mascara = np.random.random(LONGITUD_CROMOSOMA) < PROB_MUTACION
    mutado[mascara] = np.random.uniform(
        LIMITE_INFERIOR,
        LIMITE_SUPERIOR,
        int(np.sum(mascara)),
    )
    return np.clip(mutado, LIMITE_INFERIOR, LIMITE_SUPERIOR)


def aplicar_elitismo(poblacion_actual, nueva_poblacion, k):
    """
    Preserva los k mejores individuos de la generacion actual.

    Args:
        poblacion_actual: Poblacion antes de operadores geneticos
        nueva_poblacion: Poblacion despues de operadores geneticos
        k: Numero de elites a preservar

    Returns:
        list: Nueva poblacion con elites preservados
    """
    if k == 0:
        return [ind.copiar() for ind in nueva_poblacion]

    k = min(k, len(poblacion_actual), len(nueva_poblacion))

    poblacion_actual_ordenada = sorted(
        poblacion_actual,
        key=lambda ind: ind.fitness,
        reverse=True,
    )
    elites = [ind.copiar() for ind in poblacion_actual_ordenada[:k]]

    nueva_poblacion_ordenada = sorted(
        nueva_poblacion,
        key=lambda ind: ind.fitness,
        reverse=True,
    )
    sobrevivientes = [
        ind.copiar() for ind in nueva_poblacion_ordenada[: len(nueva_poblacion) - k]
    ]

    return elites + sobrevivientes


def crear_nueva_poblacion(poblacion):
    """Genera descendencia usando seleccion, cruzamiento y mutacion."""
    nueva_poblacion = []

    while len(nueva_poblacion) < POBLACION:
        padre_1 = seleccion_torneo(poblacion)
        padre_2 = seleccion_torneo(poblacion)

        cromosoma_1, cromosoma_2 = cruzamiento_un_punto(
            padre_1.cromosoma,
            padre_2.cromosoma,
        )
        cromosoma_1 = mutacion_uniforme(cromosoma_1)
        cromosoma_2 = mutacion_uniforme(cromosoma_2)

        nueva_poblacion.append(Individuo(cromosoma_1))
        if len(nueva_poblacion) < POBLACION:
            nueva_poblacion.append(Individuo(cromosoma_2))

    return nueva_poblacion


def ejecutar_experimento(transformacion, elitismo):
    """Ejecuta una configuracion durante 100 generaciones."""
    np.random.seed(SEMILLA)
    inicio = time.perf_counter()

    poblacion = crear_poblacion_inicial()
    asignar_fitness(poblacion, transformacion)

    historial_fitness = [max(ind.fitness for ind in poblacion)]

    for _ in range(GENERACIONES):
        nueva_poblacion = crear_nueva_poblacion(poblacion)
        asignar_fitness(nueva_poblacion, transformacion)

        poblacion = aplicar_elitismo(poblacion, nueva_poblacion, elitismo)
        asignar_fitness(poblacion, transformacion)

        historial_fitness.append(max(ind.fitness for ind in poblacion))

    tiempo_seg = time.perf_counter() - inicio
    fitness_final = np.array([ind.fitness for ind in poblacion], dtype=float)
    mejor_fitness = float(np.max(fitness_final))
    diversidad_final = float(np.std(fitness_final))

    resultado = {
        "Transformacion": transformacion,
        "Elitismo": elitismo,
        "Mejor_Fitness": round(mejor_fitness, 6),
        "Generaciones": GENERACIONES,
        "Tiempo_seg": round(tiempo_seg, 6),
        "Diversidad_Final": round(diversidad_final, 6),
    }
    return resultado, historial_fitness


def ejecutar_matriz_comparativa():
    """Ejecuta las 9 configuraciones requeridas por el reto."""
    resultados = []
    historiales = {}

    for transformacion in TRANSFORMACIONES:
        for elitismo in NIVELES_ELITISMO:
            resultado, historial = ejecutar_experimento(transformacion, elitismo)
            resultados.append(resultado)
            historiales[(transformacion, elitismo)] = historial

    return resultados, historiales


def guardar_resultados(resultados):
    """Guarda la matriz 3x3 de resultados en CSV."""
    columnas = [
        "Transformacion",
        "Elitismo",
        "Mejor_Fitness",
        "Generaciones",
        "Tiempo_seg",
        "Diversidad_Final",
    ]
    df = pd.DataFrame(resultados, columns=columnas)
    df.to_csv(CSV_SALIDA, index=False)
    return df


def guardar_grafica(historiales):
    """Genera la grafica comparativa de convergencia."""
    generaciones = np.arange(GENERACIONES + 1)
    colores = {
        "Inversion": "#1f77b4",
        "Negacion": "#d62728",
        "Ranking": "#2ca02c",
    }
    estilos = {
        0: "-",
        2: "--",
        5: ":",
    }
    marcadores = {
        0: "o",
        2: "s",
        5: "^",
    }

    plt.figure(figsize=(12, 8))
    for transformacion in TRANSFORMACIONES:
        for elitismo in NIVELES_ELITISMO:
            etiqueta = f"{transformacion} k={elitismo}"
            plt.plot(
                generaciones,
                historiales[(transformacion, elitismo)],
                label=etiqueta,
                color=colores[transformacion],
                linestyle=estilos[elitismo],
                marker=marcadores[elitismo],
                markevery=10,
                linewidth=2,
                markersize=4,
                alpha=0.9,
            )

    plt.xlabel("Generacion", fontsize=12)
    plt.ylabel("Mejor Fitness (escala log)", fontsize=12)
    plt.title("Convergencia: Transformaciones x Elitismo", fontsize=14)
    plt.yscale("log")
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=True)
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(GRAFICA_SALIDA, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    resultados, historiales = ejecutar_matriz_comparativa()
    df = guardar_resultados(resultados)
    guardar_grafica(historiales)

    print("Matriz comparativa generada:")
    print(df.to_string(index=False))
    print(f"\nCSV guardado en: {CSV_SALIDA}")
    print(f"Grafica guardada en: {GRAFICA_SALIDA}")


if __name__ == "__main__":
    main()
