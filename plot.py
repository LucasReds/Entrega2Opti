import pandas as pd
import matplotlib.pyplot as plt

eficiencias = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25]
resultados = []

# Cargar resultados por eficiencia
for ef in eficiencias:
    fname = f"Resultados_eficiencia_{ef:.2f}.xlsx"
    df = pd.read_excel(fname, sheet_name="Contaminantes")
    total_conc = df["Concentración"].sum()
    df["Eficiencia"] = ef
    resultados.append((ef, total_conc, df.copy()))

# Dataframe total concentración
df_total_conc = pd.DataFrame({
    "Eficiencia": [r[0] for r in resultados],
    "Concentración Total": [r[1] for r in resultados]
})

# Dataframe valor objetivo
valores_objetivo = []
for ef in eficiencias:
    fname = f"Resultados_eficiencia_{ef:.2f}.xlsx"
    info_df = pd.read_excel(fname, sheet_name="Info")
    objetivo = info_df["Objetivo"].iloc[0]
    valores_objetivo.append({"Eficiencia": ef, "Valor Objetivo": objetivo})

df_objetivos = pd.DataFrame(valores_objetivo)

# --------- GRAFICOS ---------

# 1. Valor Objetivo
plt.figure(figsize=(8, 5))
plt.plot(df_objetivos["Eficiencia"], df_objetivos["Valor Objetivo"], marker='o', color='steelblue')
plt.title("Valor Objetivo vs Eficiencia")
plt.xlabel("Eficiencia")
plt.ylabel("Valor Objetivo")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot_valor_objetivo_vs_eficiencia.png")
plt.show()

# 2. Concentración Total
plt.figure(figsize=(8, 5))
plt.plot(df_total_conc["Eficiencia"], df_total_conc["Concentración Total"], marker='o', color='darkgreen')
plt.title("Concentración Total vs Eficiencia")
plt.xlabel("Eficiencia")
plt.ylabel("Concentración Total")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot_concentracion_total_vs_eficiencia.png")
plt.show()

# 3. Por contaminante
df_all = pd.concat([r[2] for r in resultados], ignore_index=True)

plt.figure(figsize=(10, 6))
for contaminante in df_all["Contaminante"].unique():
    df_sub = df_all[df_all["Contaminante"] == contaminante]
    plt.plot(df_sub["Eficiencia"], df_sub["Concentración"], marker='o', label=f"Contaminante {contaminante}")

plt.title("Concentración por Contaminante vs Eficiencia")
plt.xlabel("Eficiencia")
plt.ylabel("Concentración")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plot_concentracion_por_contaminante_vs_eficiencia.png")
plt.show()
