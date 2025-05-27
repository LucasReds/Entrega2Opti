import csv
import random

P = 30
T = 365
C = 20

# Crear procesos.csv, periodos.csv, contaminantes.csv
with open("procesos.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["p"])
    for p in range(1, P + 1):
        writer.writerow([p])

with open("periodos.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t"])
    for t in range(1, T + 1):
        writer.writerow([t])

with open("contaminantes.csv", "w", newline="") as f:
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

i = {p: random.randint(10, 50) for p in range(1, P + 1)}
d = {p: random.randint(5, 30) for p in range(1, P + 1)}
v = {p: random.randint(30, 100) for p in range(1, P + 1)}
f_param = {p: random.randint(1, 5) for p in range(1, P + 1)}
r = {p: random.randint(5, 15) for p in range(1, P + 1)}

guardar_parametro_por_proceso("i.csv", i)
guardar_parametro_por_proceso("d.csv", d)
guardar_parametro_por_proceso("v.csv", v)
guardar_parametro_por_proceso("f.csv", f_param)
guardar_parametro_por_proceso("r.csv", r)

# Eficiencia de filtrado eta[c, p]
with open("eta.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["c", "p", "eta"])
    for c in range(1, C + 1):
        for p in range(1, P + 1):
            eta_val = round(random.uniform(0.1, 0.6), 2)
            writer.writerow([c, p, eta_val])

# Lluvia por periodo (alpha)
with open("alpha.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t", "alpha"])
    for t in range(1, T + 1):
        lluvia = random.randint(0, 2)  # lluvia baja
        writer.writerow([t, lluvia])

# Parámetros escalares
with open("parametros.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["nombre", "valor"])
    writer.writerow(["B", 50000])   # presupuesto
    writer.writerow(["E", 200])     # volumen emergencia
    writer.writerow(["N", 20])      # lluvia normal
    writer.writerow(["g", 3])       # litros de rebalse proceso
    writer.writerow(["mu", 5])      # rebalse piscina
