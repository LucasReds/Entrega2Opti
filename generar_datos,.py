import csv
import random

P = 8
T = 31
C = 5

# Crear procesos.csv, periodos.csv, contaminantes.csv
with open("Datos/procesos.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["p"])
    for p in range(1, P + 1):
        writer.writerow([p])

with open("Datos/periodos.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t"])
    for t in range(1, T + 1):
        writer.writerow([t])

with open("Datos/contaminantes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["c"])
    for c in range(1, C + 1):
        writer.writerow([c])

# Parámetros por proceso
def guardar_parametro_por_proceso(nombre, valores):
    with open(nombre, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["p", "valor"])
        for p in range(1, P + 1):
            writer.writerow([p, valores[p]])

i = {p: random.randint(10, 30) for p in range(1, P + 1)}
d = {p: random.randint(5, 30) for p in range(1, P + 1)}
v = {p: random.randint(10, 60) for p in range(1, P + 1)}
f_param = {p: random.randint(1, 15) for p in range(1, P + 1)}
r = {p: random.randint(5, 50) for p in range(1, P + 1)}
for p in range(1, P + 1):
    d[p] = random.randint(5, 20)
    max_r = 365 // d[p]
    r[p] = random.randint(1, max_r)

total_cost = 0
for p in range(1, P + 1):
    max_r = 365 // d[p]
    r[p] = random.randint(1, max_r)
    total_cost += f_param[p] * r[p]

# Asegura que B sea suficiente
B = int(total_cost * 1.2)  # margen del 20%

#nombre,valor
#B,83993
#E,20000
#N,400
#g,10
#mu,120

guardar_parametro_por_proceso("Datos/i.csv", i)
guardar_parametro_por_proceso("Datos/d.csv", d)
guardar_parametro_por_proceso("Datos/v.csv", v)
guardar_parametro_por_proceso("Datos/f.csv", f_param)
guardar_parametro_por_proceso("Datos/r.csv", r)

# Assign each process a "target" contaminant
targets = {p: random.randint(1, C) for p in range(1, P + 1)}

with open("Datos/eta.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["c", "p", "eta"])
    for c in range(1, C + 1):
        for p in range(1, P + 1):
            if c == targets[p]:
                eta_val = round(random.uniform(0.5, 0.8), 2)  # High efficiency for target
            else:
                eta_val = round(random.uniform(0.0, 0.3), 2)  # Low efficiency otherwise
            writer.writerow([c, p, eta_val])

# Lluvia por periodo (alpha)
with open("Datos/alpha.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t", "alpha"])
    for t in range(1, T + 1):
        lluvia = 0  # lluvia baja y decimal
        writer.writerow([t, lluvia])

# Parámetros escalares
with open("Datos/parametros.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["nombre", "valor"])
    writer.writerow(["B", 83993])   # presupuesto
    writer.writerow(["E", 20000])     # volumen emergencia
    writer.writerow(["N", 400])      # flujo a proceso
    writer.writerow(["g", 10])       # litros de rebalse proceso
    writer.writerow(["mu", 120])      # rebalse piscina
