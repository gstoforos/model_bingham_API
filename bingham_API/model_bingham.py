import numpy as np
from scipy.optimize import curve_fit

def bingham_model(gamma, tau0, mu_p):
    return tau0 + mu_p * gamma

def fit_bingham(data):
    try:
        # Extract inputs from JSON
        shear_rates = np.array(data.get("shear_rates", []), dtype=float)
        shear_stresses = np.array(data.get("shear_stresses", []), dtype=float)

        flow_rate = float(data.get("flow_rate", 1))
        diameter = float(data.get("diameter", 1))
        density = float(data.get("density", 1))

        if len(shear_rates) != len(shear_stresses) or len(shear_rates) < 2:
            raise ValueError("Mismatched or insufficient data points.")

        # Step 1: Fit Bingham model
        popt, _ = curve_fit(bingham_model, shear_rates, shear_stresses, maxfev=10000)
        tau0, mu_p = popt

        # Step 2: Velocity and wall shear rate
        area = np.pi * (diameter ** 2) / 4
        velocity = flow_rate / area if area > 0 else 1.0
        gamma_w = 8 * velocity / diameter if diameter > 0 else 1.0

        # Step 3: Safe values for Reynolds number calc
        safe_mu_p = mu_p if mu_p and mu_p > 0 else 1.0
        safe_gamma_w = gamma_w if gamma_w and gamma_w > 0 else 1.0
        safe_tau0 = tau0 if tau0 and tau0 >= 0 else 0.0

        # Step 4: Reynolds number
        Re_B = (density * velocity * diameter / safe_mu_p) * (1 + safe_tau0 / (safe_mu_p * safe_gamma_w)) ** -1

        # Step 5: R²
        predicted = bingham_model(shear_rates, tau0, mu_p)
        ss_res = np.sum((shear_stresses - predicted) ** 2)
        ss_tot = np.sum((shear_stresses - np.mean(shear_stresses)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        # Step 6: Apparent viscosity
        mean_gamma = np.mean(shear_rates)
        tau_avg = bingham_model(mean_gamma, tau0, mu_p)
        mu_app = tau_avg / mean_gamma if mean_gamma != 0 else safe_mu_p

        return {
            "model": "Bingham Plastic",
            "tau0": round(float(np.nan_to_num(tau0, nan=0.0)), 6),
            "mu": round(float(np.nan_to_num(mu_p, nan=1.0)), 6),
            "mu_app": round(float(np.nan_to_num(mu_app, nan=1.0)), 6),
            "r2": round(float(np.nan_to_num(r2, nan=0.0)), 6),
            "re": round(float(np.nan_to_num(Re_B, nan=0.0)), 2),
            "equation": f"τ = {round(tau0, 2)} + {round(mu_p, 2)}·γ̇"
        }

    except Exception as e:
        # Forced dummy values on failure
        return {
            "model": "Bingham Plastic",
            "tau0": 0.0,
            "mu": 1.0,
            "mu_app": 1.0,
            "r2": 1.0,
            "re": 1.0,
            "equation": "τ = 0 + 1·γ̇",
            "error": f"Fitting failed: {str(e)}"
        }
