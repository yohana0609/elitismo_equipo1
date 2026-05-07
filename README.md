# Olimpiada AG 2026 - Equipo 1

## Integrantes
- Ibarra Facio Pedro Antonio
- Yohana Ornelas Ochoa
- Alejandro Andrade Romero
- Isaac Antonio Rojas Gutierrez
- Miguel Angel Gomez Candelario
- Jean Carlo 
- Oliver Lael Galvez Martinez

## Descripción
Implementación de un algoritmo genético para minimizar la función **Rastrigin en 10 dimensiones**, comparando 3 transformaciones de fitness × 3 niveles de elitismo (matriz 3×3 de 9 configuraciones), correspondiente a la Sesión 1 de la Olimpiada AG 2026.

Materia: Algoritmos Genéticos y Evolutivos
Profesor: Gonzalez Zepeda Sebastian
Universidad de Colima — FIME

## Estructura del Proyecto
```
olimpiada-ag-2026-equipo-1/
├── README.md
├── .gitignore
├── sesion1/
│   ├── equipo_1_codigo.py        # Implementación principal
│   ├── equipo_1_resultados.csv   # Matriz 3×3 de resultados
│   ├── equipo_1_grafica.png      # Visualización comparativa
│   └── requirements.txt          # Dependencias
└── docs/
    └── decisiones.md             # Documentación de decisiones técnicas
```

## Requisitos
Para instalar las dependencias necesarias:
```bash
pip install -r sesion1/requirements.txt
```

## Ejecución
```bash
cd sesion1
python equipo_1_codigo.py
```
Esto regenera `equipo_1_resultados.csv` y `equipo_1_grafica.png` en la misma carpeta.

## Configuración del AG
| Parámetro | Valor |
|---|---|
| Población | 50 |
| Generaciones | 100 |
| Longitud cromosoma | 10 (valores reales) |
| Prob. cruzamiento | 0.8 (un punto) |
| Prob. mutación | 0.01 (uniforme) |
| Selección | Torneo (k=3) |
| Semilla | 42 |

## Transformaciones implementadas
1. **Inversión simple:** `fitness = 1 / (1 + f(x))`
2. **Negación con desplazamiento:** `fitness = max(0, C_max - f(x))` con `C_max = max(f) × 1.1`
3. **Ranking lineal:** `fitness = 2 - sp + 2(sp-1)(rank-1)/(N-1)` con `sp = 1.5`

## Niveles de elitismo
- k = 0 (sin elitismo)
- k = 2 (bajo)
- k = 5 (moderado)

## Resultados principales
La gráfica `equipo_1_grafica.png` muestra la convergencia de las 9 configuraciones. Hallazgos:
- En este problema multimodal, niveles bajos de elitismo facilitan la exploración.
- Mayor `k` reduce sistemáticamente la diversidad poblacional.
- El ranking lineal mantiene una distribución de fitness constante (invariante a la población), por lo que su diversidad de fitness no decae con el elitismo.
- En la gráfica las configuraciones de ranking pueden superponerse porque el mejor fitness por ranking es 1.5 por construcción.

Detalles completos en `docs/decisiones.md`.
