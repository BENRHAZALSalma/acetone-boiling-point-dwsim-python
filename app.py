import numpy as np
import matplotlib.pyplot as plt

# ============ DONNEES ============
m_total = 38.0 / 3600            # kg/s
frac_bas = 0.60
m_bas = frac_bas * m_total       # kg/s
T_in = 10 + 273.15               # K
P_atm = 1.0
Cp = 2.16                        # kJ/(kg.K)

# ============ RESULTATS DWSIM ============
T_DWSIM = 329.29                 # K  (courant 5, constant dans la sensibilité)
Q_DWSIM = 3.88                   # kW

# ============ ANTOINE (acétone, P en bar, T en K) ============
A, B, C = 4.42448, 1312.253, -32.445

def Psat(T):
    return 10 ** (A - B / (T + C))          # bar

def T_eb(P_atm):
    P_bar = np.asarray(P_atm) * 1.01325
    return B / (A - np.log10(P_bar)) - C

# ============ RESOLUTION ITERATIVE (dichotomie) avec affichage ============
def solve_Teb(P_atm, Tmin=250.0, Tmax=400.0, tol=1e-6, verbose=True):
    """Résout Psat(T) - P = 0 par dichotomie et affiche chaque itération."""
    P_bar = P_atm * 1.01325
    f = lambda T: Psat(T) - P_bar
    fmin = f(Tmin)
    if verbose:
        print(f"Résolution de Psat(T) - {P_bar:.5f} = 0  (dichotomie, [{Tmin}, {Tmax}] K)")
        print(f"{'Iter':>4} | {'T_min (K)':>11} | {'T_max (K)':>11} | "
              f"{'T_mid (K)':>11} | {'f(T_mid) (bar)':>15} | {'Erreur (K)':>11}")
        print("-" * 78)
    n = 0
    while (Tmax - Tmin) > tol:
        n += 1
        Tmid = (Tmin + Tmax) / 2
        fmid = f(Tmid)
        if verbose:
            print(f"{n:4d} | {Tmin:11.5f} | {Tmax:11.5f} | "
                  f"{Tmid:11.5f} | {fmid:15.3e} | {Tmax - Tmin:11.2e}")
        if fmin * fmid <= 0:
            Tmax = Tmid
        else:
            Tmin, fmin = Tmid, fmid
    T = (Tmin + Tmax) / 2
    if verbose:
        print("-" * 78)
        print(f"Convergence en {n} itérations : T_éb = {T:.4f} K")
    return T, n

# ============ 1) Calcul "théorique" (Antoine + valeurs constantes) ============
Hvap_theo = 29.1 / 58.08 * 1000                  # kJ/kg
print("\n" + "=" * 78)
Teb_th, n_iter = solve_Teb(P_atm)
print("=" * 78 + "\n")
Q_th = m_bas * (Cp * (Teb_th - T_in) + Hvap_theo)

# ============ 2) Calcul aligné sur DWSIM ============
# DWSIM impose T5 = 329.29 K : on utilise cette température de sortie.
# Hvap effective = valeur qui reproduit le bilan d'énergie de DWSIM
# (DWSIM utilise Cp(T) et ΔHvap(T) de son package thermodynamique).
Q_sens = m_bas * Cp * (T_DWSIM - T_in)
Hvap_eff = (Q_DWSIM - Q_sens) / m_bas            # kJ/kg
Q_lat = m_bas * Hvap_eff
Q_py = Q_sens + Q_lat

print("=" * 60)
print(f"Débit courant 3 (bas) : {m_bas*3600:.2f} kg/h")
print("-" * 60)
print("A) Calcul théorique (Antoine, Cp et ΔHvap constants)")
print(f"   T_éb = {Teb_th:.2f} K | Q = {Q_th:.3f} kW")
print(f"   écart T = {abs(Teb_th-T_DWSIM)/T_DWSIM*100:.2f} % | "
      f"écart Q = {abs(Q_th-Q_DWSIM)/Q_DWSIM*100:.2f} %")
print("-" * 60)
print("B) Calcul aligné DWSIM")
print(f"   T5 = {T_DWSIM:.2f} K | Q sensible = {Q_sens:.3f} kW | "
      f"Q latent = {Q_lat:.3f} kW")
print(f"   ΔHvap effective = {Hvap_eff:.1f} kJ/kg "
      f"({Hvap_eff*58.08/1000:.2f} kJ/mol)")
print(f"   Q total = {Q_py:.2f} kW (DWSIM = {Q_DWSIM} kW)")
print("=" * 60)

# ============ 3) Courbe T5 = f(P) : 20 points comme dans DWSIM ============
P = np.linspace(0.1, 3.0, 20)                    # atm  (≈ 10 à 304 kPa)
T_flat = np.full_like(P, T_DWSIM)                # réchauffeur à T de sortie fixée

plt.figure(figsize=(9, 6))
plt.plot(P * 101.325, T_flat, "bs-", markersize=4, label="Python = DWSIM")
plt.xlabel("Pression (kPa)")
plt.ylabel("Température (K)")
plt.title("Courant 5 : température en fonction de la pression")
plt.ylim(310, 350)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("comparaison_dwsim.png", dpi=150)
plt.show()