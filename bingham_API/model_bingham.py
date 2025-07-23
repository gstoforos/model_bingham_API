import numpy as np
from scipy.optimize import curve_fit

def bingham_model(gamma, tau0, mu_p):
    return tau0 + mu_p * gamma

def fit_bingham_model(shear_rates, shear_stresses, flow_rate, diameter, density):
    try:
        # Convert inputs to NumPy arrays
        shear_rates = np.array(shear_rates, dtype=float)
        shear_stresses = np.array(shear_stresses, dtype=float)

        # Fit Bingham model: τ = τ₀ + μp * γ̇
        params, _ = curve_fit(bingham_model, shear_rates, shear_stresses)
        tau0, mu_p = params

        # Calculate velocity
        area = np.pi * (diameter ** 2) / 4
        velocity = flow_rate / area if area > 0 else 0

        # Wall shear rate
        gamma_w = 8 * velocity / diameter if diameter > 0 else 1e-6

        # Reynolds number
        if mu_p > 0 and gamma_w > 0:
            Re_B = (density * velocity * diameter / mu_p) * (1 + tau0 / (mu_p * gamma_w)) ** -1
        else:
            Re_B = 0.0

        # R² value
        predicted = bingham_model(shear_rates, tau0, mu_p)
        ss_res = np.sum((shear_stresses - predicted) ** 2)
        ss_tot = np.sum((shear_stresses - np.mean(shear_stresses)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        # Apparent viscosity
        mean_gamma = np.mean(shear_rates)
        tau_avg = bingham_model(mean_gamma, tau0, mu_p)
        mu_app = tau_avg / mean_gamma if mean_gamma != 0 else mu_p

    except Exception as e:
        print("Error in Bingham model:", str(e))
        tau0, mu_p, Re_B, r2, mu_app = 0.0, 1.0, 0.0, 0.0, 1.0

    # Final safe return (no NaNs or None)
    return {
        "model": "Bingham Plastic",
        "tau0": round(float(np.nan_to_num(tau0, nan=0.0)), 6),
        "mu": round(float(np.nan_to_num(mu_p, nan=1.0)), 6),
        "mu_app": round(float(np.nan_to_num(mu_app, nan=1.0)), 6),
        "r2": round(float(np.nan_to_num(r2, nan=0.0)), 6),
        "re": round(float(np.nan_to_num(Re_B, nan=0.0)), 2),
        "equation": f"τ = {round(tau0, 2)} + {round(mu_p, 2)}·γ̇"
    }
