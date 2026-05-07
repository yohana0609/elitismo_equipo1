# Decisiones Técnicas — Sesión 1

## Representación del individuo
Se usa una clase `Individuo` con tres atributos: `cromosoma` (vector NumPy de 10 reales), `valor_objetivo` (resultado de Rastrigin) y `fitness` (resultado de la transformación). Esto permite separar conceptualmente el valor objetivo del fitness, lo cual hace el código más legible y fácil de auditar al cambiar transformaciones.

## Codificación
Codificación real directa: cada gen es un float en `[-5.12, 5.12]`. No se usa codificación binaria porque el enunciado especifica `LONGITUD_CROMOSOMA = 10` y mutación uniforme para valores reales.

## Operadores
- **Selección:** Torneo de tamaño k=3. En cada torneo se eligen 3 índices sin reemplazo y gana el de mayor fitness.
- **Cruzamiento:** Un punto sobre el vector real, probabilidad 0.8. El punto de corte se elige aleatoriamente en `[1, 10)`.
- **Mutación:** Uniforme con probabilidad 0.01 por gen. Si un gen muta, se reemplaza por un valor aleatorio uniforme dentro del dominio.
- **Clipping:** Tras el cruzamiento y mutación se aplica `np.clip` para garantizar que los cromosomas se mantengan en el dominio.

## Transformaciones

### Inversión
`fitness = 1 / (1 + f(x))`. Mapea valores objetivo en `[0, ∞)` a fitness en `(0, 1]`. Maneja sin problema el caso `f(x) = 0` (óptimo global → fitness = 1).

### Negación con desplazamiento
`C_max = max(f_obj de la población) * 1.1`, luego `fitness = max(0, C_max - f(x))`. El factor 1.1 garantiza que ningún individuo tenga fitness exactamente 0 (lo que rompería la selección por torneo si todos cayeran ahí). El recálculo dinámico de `C_max` por generación es necesario porque la magnitud de los valores objetivo cambia con el tiempo.

### Ranking lineal
Se ordena la población de peor a mejor f_obj (mayor a menor) y se asigna `fitness(rank) = 2 - sp + 2(sp-1)(rank-1)/(N-1)` con `sp = 1.5`. El peor recibe fitness 0.5 y el mejor 1.5. Es invariante a la magnitud absoluta del valor objetivo, lo que evita que un superindividuo domine la selección.

## Elitismo
Se preservan los k mejores de la población actual y se reemplazan los k peores de la nueva población. La preservación es estricta — los élites pasan sin alteración.

**Detalle importante:** después de aplicar elitismo se vuelve a llamar a `asignar_fitness` sobre la población combinada. Esto es crítico para el ranking lineal, donde los rangos cambian al mezclar dos poblaciones; sin este paso, élites y nuevos individuos tendrían fitness asignados bajo rangos distintos. Para inversión también ayuda mantener consistencia, y para negación se recalcula `C_max` con la población final.

## Métrica de diversidad
Se reporta la **desviación estándar del fitness** en la generación 100, tal como pide el enunciado. Para ranking esta métrica es constante por construcción (los fitness son siempre los mismos N valores); para inversión y negación decrece a medida que la población converge.

## Reproducibilidad
Cada una de las 9 configuraciones se ejecuta con `np.random.seed(42)` al inicio. Esto garantiza que la población inicial sea idéntica entre configuraciones, de modo que las diferencias observadas se deban exclusivamente a la transformación y al elitismo, no a la estocasticidad inicial.

## Hallazgos del experimento
- En problemas multimodales como Rastrigin, niveles bajos de elitismo (k=0 o k=2) tienden a escapar mejor de óptimos locales que k=5, porque conservan más diversidad.
- La diversidad final disminuye sistemáticamente con k creciente para Inversión y Negación.
- El ranking lineal genera la misma distribución de fitness en cada generación, por lo que su métrica de diversidad std no varía con k. La diversidad genotípica sí varía, pero la fenotípica de fitness no.
- La negación arroja valores de fitness mayores en magnitud absoluta debido al desplazamiento `C_max`, pero la presión selectiva relativa es comparable a la inversión.
