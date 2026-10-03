import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from CoolProp.CoolProp import PropsSI


# ============================================================
# 1. DONNEES DU PROBLEME
# ============================================================

FLUID = "Acetone"

# Alimentation
m_total = 38.0          # kg/h
T_in_C = 10.0           # °C
P_in_atm = 1.0          # atm

# Conversion
ATM_TO_PA = 101325.0

T_in_K = T_in_C + 273.15
P_in_Pa = P_in_atm * ATM_TO_PA


# ============================================================
# 2. SEPARATION DU DEBIT
# ============================================================

fraction_1 = 0.40
fraction_2 = 0.60

m_1 = m_total * fraction_1
m_2 = m_total * fraction_2

print("=" * 60)
print("BILAN MATIERE")
print("=" * 60)

print(f"Débit total       : {m_total:.2f} kg/h")
print(f"Débit flux 40 %   : {m_1:.2f} kg/h")
print(f"Débit flux 60 %   : {m_2:.2f} kg/h")


# ============================================================
# 3. TEMPERATURE D'EBULLITION A 1 atm
# ============================================================

# Température de saturation de l'acétone à 1 atm
T_boil_K = PropsSI("T", "P", P_in_Pa, "Q", 0, FLUID)
T_boil_C = T_boil_K - 273.15

print("\n" + "=" * 60)
print("TEMPERATURE D'EBULLITION A 1 atm")
print("=" * 60)

print(f"Pression          : {P_in_atm:.2f} atm")
print(f"Température       : {T_boil_C:.3f} °C")
print(f"Température       : {T_boil_K:.3f} K")


# ============================================================
# 4. ENERGIE NECESSAIRE POUR VAPORISER LE FLUX 60 %
# ============================================================

# Enthalpie du liquide à l'entrée
h_in = PropsSI("H", "T", T_in_K, "P", P_in_Pa, FLUID)

# Enthalpie de la vapeur saturée à la pression de 1 atm
h_vapor = PropsSI("H", "P", P_in_Pa, "Q", 1, FLUID)

# Energie spécifique nécessaire
delta_h = h_vapor - h_in       # J/kg

# Puissance thermique
# m_2 est en kg/h → conversion en kg/s
m_2_kg_s = m_2 / 3600

Q_W = m_2_kg_s * delta_h
Q_kW = Q_W / 1000

# Energie par heure
Q_kJ_h = Q_kW * 3600

print("\n" + "=" * 60)
print("VAPORISATION DU FLUX 60 %")
print("=" * 60)

print(f"Débit à vaporiser : {m_2:.2f} kg/h")
print(f"Enthalpie liquide : {h_in / 1000:.2f} kJ/kg")
print(f"Enthalpie vapeur  : {h_vapor / 1000:.2f} kJ/kg")
print(f"Delta H           : {delta_h / 1000:.2f} kJ/kg")

print(f"\nEnergie nécessaire : {Q_kJ_h:.2f} kJ/h")
print(f"Puissance thermique: {Q_kW:.4f} kW")


# ============================================================
# 5. VARIATION DE LA TEMPERATURE D'EBULLITION
#    0.1 atm → 3 atm
#    25 POINTS
# ============================================================

P_min_atm = 0.1
P_max_atm = 3.0
n_points = 25

pressures_atm = np.linspace(
    P_min_atm,
    P_max_atm,
    n_points
)

pressures_Pa = pressures_atm * ATM_TO_PA

boiling_temperatures_K = []
boiling_temperatures_C = []

for P in pressures_Pa:

    # Température de saturation
    T_sat_K = PropsSI(
        "T",
        "P", P,
        "Q", 0,
        FLUID
    )

    boiling_temperatures_K.append(T_sat_K)
    boiling_temperatures_C.append(T_sat_K - 273.15)


# ============================================================
# 6. TABLEAU DES RESULTATS
# ============================================================

results = pd.DataFrame({
    "Point": np.arange(1, n_points + 1),
    "Pressure (atm)": pressures_atm,
    "Pressure (Pa)": pressures_Pa,
    "Boiling Temperature (K)": boiling_temperatures_K,
    "Boiling Temperature (°C)": boiling_temperatures_C
})

print("\n" + "=" * 60)
print("COURBE DE TEMPERATURE D'EBULLITION")
print("=" * 60)

print(results.to_string(index=False))


# ============================================================
# 7. VERIFICATION DU POINT A 1 atm
# ============================================================

T_1atm = PropsSI(
    "T",
    "P", ATM_TO_PA,
    "Q", 0,
    FLUID
) - 273.15

print("\n" + "=" * 60)
print("VERIFICATION A 1 atm")
print("=" * 60)

print(f"T ébullition à 1 atm = {T_1atm:.3f} °C")


# ============================================================
# 8. TRACE DE LA COURBE
# ============================================================

plt.figure(figsize=(9, 6))

plt.plot(
    pressures_atm,
    boiling_temperatures_C,
    marker="o"
)

plt.xlabel("Pression (atm)")
plt.ylabel("Température d'ébullition (°C)")
plt.title("Température d'ébullition de l'acétone en fonction de la pression")

plt.grid(True)
plt.tight_layout()

plt.show()


# ============================================================
# 9. SAUVEGARDE DU TABLEAU
# ============================================================

results.to_csv(
    "acetone_boiling_curve.csv",
    index=False
)

print("\nRésultats sauvegardés dans : acetone_boiling_curve.csv")