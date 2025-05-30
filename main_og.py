import pandas as pd
from gurobipy import Model, GRB, quicksum

# Leer datos desde carpeta Datos/
i_df = pd.read_csv("Datos/i.csv")
d_df = pd.read_csv("Datos/d.csv")
v_df = pd.read_csv("Datos/v.csv")
f_df = pd.read_csv("Datos/f.csv")
r_df = pd.read_csv("Datos/r.csv")
eta_df = pd.read_csv("Datos/eta.csv")
alpha_df = pd.read_csv("Datos/alpha.csv")
parametros_df = pd.read_csv("Datos/parametros.csv")

# Rango de parámetros
P = sorted(i_df['p'].unique())
T = sorted(alpha_df['t'].unique())
C = sorted(eta_df['c'].unique())

P_ = len(P)
T_ = len(T)
C_ = len(C)

# Parámetros numéricos
presupuesto = parametros_df[parametros_df['nombre'] == 'B']['valor'].values[0]
volumen_emergencia = parametros_df[parametros_df['nombre'] == 'E']['valor'].values[0]
N = parametros_df[parametros_df['nombre'] == 'N']['valor'].values[0]
g = parametros_df[parametros_df['nombre'] == 'g']['valor'].values[0]
mu = parametros_df[parametros_df['nombre'] == 'mu']['valor'].values[0]
M = 1e8
eps = 1e-3

# Asignar datos
i = dict(zip(i_df['p'], i_df['valor']))
d = dict(zip(d_df['p'], d_df['valor']))
v = dict(zip(v_df['p'], v_df['valor']))
f = dict(zip(f_df['p'], f_df['valor']))
r = dict(zip(r_df['p'], r_df['valor']))
eta = {(row['c'], row['p']): row['eta'] for _, row in eta_df.iterrows()}
alpha = dict(zip(alpha_df['t'], alpha_df['alpha']))

# Modelo

m = Model("Filtración")

# Variables
X = m.addVars(P, T, vtype=GRB.BINARY, name="X")
Y = m.addVars(P, T, vtype=GRB.BINARY, name="Y")
H = m.addVars(P, T, vtype=GRB.CONTINUOUS, lb=0, name="H")
Q = m.addVars(T, vtype=GRB.BINARY, name="Q")
S = m.addVars(T, vtype=GRB.BINARY, name="S")
Z = m.addVars(C, P, T, vtype=GRB.CONTINUOUS, name="Z")
A = m.addVars(T, vtype=GRB.CONTINUOUS, lb=0, name="A")

# Objetivo
m.setObjective(quicksum(Z[c, p, t] for c in C for p in P for t in T), GRB.MINIMIZE)

# Restricciones

# R1: Contaminante
for c in C:
    for p in P:
        for t in T:
            m.addConstr((1 - eta[c, p]) * r[p] * Y[p, t] == Z[c, p, t], name=f"R1_{c}_{p}_{t}")

# R2: Un proceso activo por t
for t in T:
    m.addConstr(quicksum(Y[p, t] for p in P) == 1, name=f"R2_{t}")

# R3: Continuidad hacia atrás
for p in P:
    for t in T:
        t_range = range(max(t - f[p] + 1, T[0]), t + 1)
        m.addConstr(quicksum(X[p, t2] for t2 in t_range) >= Y[p, t], name=f"R3_{p}_{t}")

# R4: Continuidad hacia adelante
for p in P:
    for t in T[:-f[p]+1]:
        m.addConstr(quicksum(Y[p, t2] for t2 in range(t, t + f[p])) >= f[p] * X[p, t], name=f"R4_{p}_{t}")

for p in P:
    for t in T:
        if t + f[p] <= T[-1] + 1:
            m.addConstr(quicksum(X[p, t2] for t2 in range(t, t + f[p])) <= 1, name=f"NoSolapamiento_{p}_{t}")


# R5: Inventario proceso t=1
for p in P:
    m.addConstr(H[p, T[0]] == N + alpha[T[0]] - Q[T[0]] * g - r[p] * Y[p, T[0]] + S[T[0]] * mu, name=f"R5_{p}")

# R6: Inventario proceso t > 1
for p in P:
    for t in T[1:]:
        m.addConstr(H[p, t] == H[p, t-1] + N + alpha[t] - Q[t] * g - r[p] * Y[p, t] + S[t] * mu, name=f"R6_{p}_{t}")

# R7: Rebalse de proceso
for p in P:
    for t in T:
        m.addConstr(H[p, t] - v[p] <= M * Q[t], name=f"R7a_{p}_{t}")
        m.addConstr(H[p, t] - v[p] >= eps - M * (1 - Q[t]), name=f"R7b_{p}_{t}")

# R8: Inventario piscina t=1
m.addConstr(A[T[0]] == Q[T[0]] * g - S[T[0]] * mu, name="R8")

# R9: Inventario piscina t > 1
for t in T[1:]:
    m.addConstr(A[t] == A[t-1] + Q[t] * g - S[t] * mu, name=f"R9_{t}")

# R10: Rebalse piscina
for t in T:
    m.addConstr(A[t] - volumen_emergencia <= M * S[t], name=f"R10a_{t}")
    m.addConstr(A[t] - volumen_emergencia >= eps - M * (1 - S[t]), name=f"R10b_{t}")

# R11: No rebalse simultáneo
for t in T:
    m.addConstr(S[t] + Q[t] <= 1, name=f"R11_{t}")

# R12: Presupuesto
m.addConstr(quicksum(Y[p, t] * d[p] for p in P for t in T) +
            quicksum(X[p, t] * i[p] for p in P for t in T) <= presupuesto, name="R12")

# R13: Activación inmediata
for p in P:
    for t in T:
        m.addConstr(X[p, t] <= Y[p, t], name=f"R13_{p}_{t}")

# Optimize

m.optimize()

# if m.status == GRB.INF_OR_UNBD or m.status == GRB.INFEASIBLE:
#     m.computeIIS()
#     m.write("modelo.ilp")  # Guardar el IIS para depuración

if m.status == GRB.OPTIMAL:
    print("\nResultados optimal:")
    for p in P:
        for t in T:
            if X[p, t].X > 0.5:
                print(f"Proceso {p} iniciado en t={t}")
            if Y[p, t].X > 0.5:
                print(f"Proceso {p} activo en t={t}")
    # for t in T:
    #     if Q[t].X > 0.5:
    #         print(f"Rebalse de proceso en t={t}")
    #     if S[t].X > 0.5:
    #         print(f"Rebalse de piscina en t={t}")
else:
    print("No se encontró solución óptima. Status:", m.status)
