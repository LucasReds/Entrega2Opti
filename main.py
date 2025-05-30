import pandas as pd
from gurobipy import Model, GRB, quicksum

# Correr el main teniendo la carpeta Datos en la misma carpeta que este script.
# Asegurarse de tener instaladas las librerías necesarias.

# 1. Costo instalación de procesos
i_df = pd.read_excel("Datos/costo_instalacion_proceso.xlsx", header=None, names=["valor"])
i_df["p"] = i_df.index
i_df = i_df[["p", "valor"]]
i = dict(zip(i_df["p"], i_df["valor"]))

# 2. Costo mantención de procesos
d_df = pd.read_excel("Datos/costo_mantencion_proceso.xlsx", header=None, names=["valor"])
d_df["p"] = d_df.index
d_df = d_df[["p", "valor"]]
d = dict(zip(d_df["p"], d_df["valor"]))

# 3. Eficiencia de procesos (matriz: contaminante x proceso)
eta_df = pd.read_excel("Datos/Eficiencias.xlsx", header=None)
eta_df["c"] = eta_df.index
eta_df = eta_df.melt(id_vars="c", var_name="p", value_name="eta")
eta = {(int(row["c"]), int(row["p"])): row["eta"] for _, row in eta_df.iterrows()}

# 4. Volumen a piscina (f)
f_df = pd.read_excel("Datos/tiempo_duracion_proceso.xlsx", header=None, names=["valor"])
f_df["p"] = f_df.index
f_df = f_df[["p", "valor"]]
f = dict(zip(f_df["p"], f_df["valor"]))

# 5. Volumen de rebalse (g)
g = pd.read_excel("Datos/g_vol_proceso_piscina.xlsx", header=None).iloc[0, 0]

# 6. Lluvia por periodo (alpha)
alpha_df = pd.read_excel("Datos/litros_agua_llueve.xlsx", header=None, names=["alpha"])
alpha_df["t"] = alpha_df.index
alpha_df = alpha_df[["t", "alpha"]]
alpha = dict(zip(alpha_df["t"], alpha_df["alpha"]))

# 7. Rebalse (r)
r = pd.read_excel("Datos/rp_vol_salida_proceso.xlsx", header=None).iloc[0, 0]

# 8. Volumen máximo proceso (v)
v = pd.read_excel("Datos/volumen_maximo_proceso_p.xlsx", header=None).iloc[0, 0]

# 9 . Concentración de contaminantes en el agua
concentration_df = pd.read_excel("Datos/concentraciones_contaminantes.xlsx", header=None, names=["concentration"])
concentration_df["c"] = concentration_df.index
concentration_df = concentration_df[["c", "concentration"]]
concentration = dict(zip(concentration_df["c"], concentration_df["concentration"]))

print("Datos concentraciones:", concentration)

# 9. Parámetros individuales

# presupuesto
presupuesto_df = pd.read_excel("Datos/Presupuesto_industria.xlsx", header=None)
presupuesto = presupuesto_df.iloc[0, 0]

# N volumen industria proceso
N_df = pd.read_excel("Datos/N_volumen_industria_proceso.xlsx", header=None)
N = N_df.iloc[0, 0]

# mu volumen piscina proceso
mu_df = pd.read_excel("Datos/mu_vol_piscina_proceso.xlsx", header=None)
mu = mu_df.iloc[0, 0]

# volumen de emergencia
vol_em_df = pd.read_excel("Datos/Volumen_piscina_emergencia.xlsx", header=None)
volumen_emergencia = vol_em_df.iloc[0, 0]

# area de piscina
area_df = pd.read_excel("Datos/area_proceso.xlsx", header=None)
a = area_df.iloc[0, 0]

# Constantes
eps = 1e-4
M = 1e10  

# Rangos
P = sorted(i_df["p"].unique())
T = sorted(alpha_df["t"].unique())
C = sorted(eta_df["c"].unique())

# Tamaños
P_ = len(P)
T_ = len(T)
C_ = len(C)

# Debug cargar datos
# print("Cantidad de procesos:", P_)
# print("Cantidad de tiempos:", T_)
# print("Cantidad de contaminantes:", C_)
# print("Presupuesto:", presupuesto)
# print("Volumen emergencia:", volumen_emergencia)
# print("mu:", mu, "N:", N)
# print("g:", g, "r:", r)
# print("f:", f)
# print("i:", i)
# print("d:", d)
# print("eta:", eta)
# print("f:", f)
# print("v:", v)

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
            m.addConstr((1 - eta[c, p]) * r * Y[p, t] * concentration[c] == Z[c, p, t], name=f"R1_{c}_{p}_{t}")

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

# R5: No solapamiento de procesos
for p in P:
    for t in T:
        if t + f[p] <= T[-1] + 1:
            m.addConstr(quicksum(X[p, t2] for t2 in range(t, t + f[p])) <= 1, name=f"R5_{p}_{t}")

# R6: Inventario proceso t=1
for p in P:
    m.addConstr(H[p, T[0]] == N + alpha[T[0]]*a - Q[T[0]] * g - r + S[T[0]] * mu, name=f"R6_{p}")

# R7: Inventario proceso t > 1
for p in P:
    for t in T[1:]:
        m.addConstr(H[p, t] == H[p, t-1] + N + alpha[t]*a - Q[t] * g - r + S[t] * mu, name=f"R7_{p}_{t}")

# R8: Rebalse de proceso
for p in P:
    for t in T:
        m.addConstr(H[p, t] - v <= M * Q[t], name=f"R8a_{p}_{t}")
        m.addConstr(H[p, t] - v >= eps - M * (1 - Q[t]), name=f"R8b_{p}_{t}")

# R9: Inventario piscina t=1
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
m.addConstr(quicksum(Y[p, t] * d[p] for p in P for t in T) + i[p] <= presupuesto, name="R12")

# R13: Activación inmediata
for p in P:
    for t in T:
        m.addConstr(X[p, t] <= Y[p, t], name=f"R13_{p}_{t}")

# Optimize

m.optimize()

# Debugging: uncomment to print model status

#if m.status == GRB.INF_OR_UNBD or m.status == GRB.INFEASIBLE:
#    m.computeIIS()
#    m.write("modelo.ilp")  # debug

# if m.status == GRB.OPTIMAL:
#     print("\nResultados optimal:")
#     for p in P:
#         for t in T:
#             if X[p, t].X > 0.5:
#                 print(f"Proceso {p} activado en t={t}")
#             if Y[p, t].X > 0.5:
#                 print(f"Proceso {p} en operación en t={t}")
#     for t in T:
#         if Q[t].X > 0.5:
#             print(f"Rebalse de proceso en t={t}")
#         if S[t].X > 0.5:
#             print(f"Rebalse de piscina en t={t}")
#     total_Z = {}
#     for c in C:
#         total = sum(Z[key].X for key in Z.keys() if key[0] == int(c))
#         total_Z[c] = total
#         print(f"Total Z for contaminant {c}: {total}")
#     # Concentration of wahts leaving:
#     total_outflow = r * 365
#     print(f"Total outflow of contaminants: {total_outflow}")
#     for c in C:
#         concentration_out = total_Z[c] / total_outflow
#         print(f"Concentration of contaminant {c} in outflow: {concentration_out}")
#else:
#    print("No se encontró solución óptima. Status:", m.status)

if m.status == GRB.OPTIMAL:
    activated = []
    in_operation = []
    rebalse_proceso = []
    rebalse_piscina = []

    info_modelo = {
        "Valor objetivo": [m.ObjVal],
        "GAP": [m.MIPGap],
        "Tiempo de resolución (segundos)": [m.Runtime],
        "Cantidad de variables": [m.NumVars],
        "Cantidad de restricciones": [m.NumConstrs],
        "Cantidad de variables binarias": [sum(1 for v in m.getVars() if v.VType == GRB.BINARY)],
        "Cantidad de variables continuas": [sum(1 for v in m.getVars() if v.VType == GRB.CONTINUOUS)],
    }
    df_info_modelo = pd.DataFrame(info_modelo)

    for p in P:
        for t in T:
            if X[p, t].X > 0.5:
                activated.append({"Proceso": p, "Tiempo": t})
            if Y[p, t].X > 0.5:
                in_operation.append({"Proceso": p, "Tiempo": t})

    for t in T:
        if Q[t].X > 0.5:
            rebalse_proceso.append({"Tiempo": t, "Tipo": "Proceso"})
        if S[t].X > 0.5:
            rebalse_piscina.append({"Tiempo": t, "Tipo": "Piscina"})

    total_Z = []
    for c in C:
        total = sum(Z[key].X for key in Z.keys() if key[0] == int(c))
        total_Z.append({"Contaminante": c, "Total_Z": total})

    # Concentration
    total_outflow = r * 365
    concentration_out = []
    for z in total_Z:
        c = z["Contaminante"]
        concentration_out.append({
            "Contaminante": c,
            "Concentración en salida": z["Total_Z"] / total_outflow
        })

    # Write to Excel
    with pd.ExcelWriter("Resultados_Optimizacion.xlsx") as writer:
        df_info_modelo.to_excel(writer, sheet_name="Información Modelo", index=False, float_format="%.6f")
        pd.DataFrame(activated).to_excel(writer, sheet_name="Procesos Activados", index=False,float_format="%.6f")
        pd.DataFrame(in_operation).to_excel(writer, sheet_name="Procesos en Operación", index=False,float_format="%.6f")
        pd.DataFrame(rebalse_proceso + rebalse_piscina).to_excel(writer, sheet_name="Rebalses", index=False,float_format="%.6f")
        pd.DataFrame(total_Z).to_excel(writer, sheet_name="Total Contaminantes Z", index=False,float_format="%.6f")
        pd.DataFrame(concentration_out).to_excel(writer, sheet_name="Concentraciones", index=False,float_format="%.6f")

    print("Resultados exportados a 'Resultados_Optimizacion.xlsx'")
