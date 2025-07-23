import numpy as np
from scipy.optimize import curve_fit

def bingham_model(gamma, tau0, mu_p):
    return tau0 + mu_p * gamma

def fit_bingham(data):
    shear_rates = np.array(data.get("shear_rates", []), dtype=float)
    shear_stresses = np.array(data.get("shear_stresses", []), dtype=float)

    flow_rate = float(data.get("flow_rate", 1))
    diameter = float(data.get("diameter", 1))
    density = float(data.get("density", 1))

    if len(shear_rates) != len(shear_stresses):
        return {"error": "Mismatched data lengths."}

    try:
        # Fit Bingham model
        params, _ = curve_fit(bingham_model, shear_rates, shear_stresses, maxfev=10000)
        tau0, mu_p = params

        # Calculate area and velocity
        area = np.pi * (diameter ** 2) / 4
        velocity = flow_rate / area if area > 0 else 1.0  # fallback

        # Wall shear rate
        gamma_w = 8 * velocity / diameter if diameter > 0 else 1.0

        # Fallbacks to avoid division by 0 or NaNs
        safe_mu_p = mu_p if mu_p and mu_p > 0 else 1.0
        safe_gamma_w = gamma_w if gamma_w and gamma_w > 0 else 1.0
        safe_tau0 = tau0 if tau0 and tau0 >= 0 else 0.0

        # Reynolds number
        try:
            Re_B = (density * velocity * diameter / safe_mu_p) * (1 + safe_tau0 / (safe_mu_p * safe_gamma_w)) ** -1
        except:
            Re_B = 0.0

        # R²
        predicted = bingham_model(shear_rates, tau0, mu_p)
        ss_res = np.sum((shear_stresses - predicted) ** 2)
        ss_tot = np.sum((shear_stresses - np.mean(shear_stresses)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        # Apparent viscosity
        mean_gamma = np.mean(shear_rates)
        tau_avg = bingham_model(mean_gamma, tau0, mu_p)
        mu_app = tau_avg / mean_gamma if mean_gamma != 0 else safe_mu_p

        return {
            "model": "Bingham Plastic",
            "tau0": round(float(np.nan_to_num(tau0, nan=0.0)), 6),
            "mu": round(float(np.nan_to_num(mu_p, nan=1.0)), 6),
            "mu_app": round(float(np.nan_to_num(mu_app, nan=1.0)), 6),
            "r2": round(float(np.nan_to_num(r_squared, nan=0.0)), 6),
            "re": round(float(np.nan_to_num(Re_B, nan=0.0)), 2),
            "equation": f"τ = {tau0:.3g} + {mu_p:.3g}·γ̇"
        }

    except Exception as e:
        return {
            "error": f"Bingham model fitting failed: {str(e)}"
        }
