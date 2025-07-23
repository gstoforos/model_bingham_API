import numpy as np
from scipy.optimize import curve_fit

# Bingham Plastic model: τ = τ₀ + μp·γ̇
def bingham_model(gamma_dot, tau0, mu_p):
    return tau0 + mu_p * gamma_dot

def fit_bingham(data):
    shear_rates = np.array(data.get("shear_rates", []))
    shear_stresses = np.array(data.get("shear_stresses", []))

    flow_rate = float(data.get("flow_rate", 1))
    diameter = float(data.get("diameter", 1))
    density = float(data.get("density", 1))

    if len(shear_rates) != len(shear_stresses):
        return {"error": "Mismatched data lengths."}

    try:
        # Fit the model: τ = τ₀ + μp·γ̇
        popt, _ = curve_fit(bingham_model, shear_rates, shear_stresses, maxfev=10000)
        tau0, mu_p = popt

        predictions = bingham_model(shear_rates, tau0, mu_p)
        residuals = shear_stresses - predictions
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((shear_stresses - np.mean(shear_stresses)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        # Apparent viscosity at average shear rate
        mean_gamma = np.mean(shear_rates)
        tau_avg = bingham_model(mean_gamma, tau0, mu_p)
        mu_app = tau_avg / mean_gamma if mean_gamma != 0 else mu_p

        # Reynolds number (Bingham Plastic)
        if flow_rate > 0 and diameter > 0 and density > 0 and mu_p > 0:
            area = np.pi * (diameter ** 2) / 4
            velocity = flow_rate / area
            gamma_w = 8 * velocity / diameter
            Re = (density * velocity * diameter / mu_p) * (1 + tau0 / (mu_p * gamma_w)) ** -1
        else:
            Re = None

        return {
            "model": "Bingham Plastic",
            "tau0": round(tau0, 6),
            "mu": round(mu_p, 6),
            "r_squared": round(r_squared, 6),
            "mu_app": round(mu_app, 6),
            "re": round(Re, 2) if Re is not None else None,
            "equation": f"τ = {tau0:.3g} + {mu_p:.3g}·γ̇"
        }

    except Exception as e:
        return {"error": f"Fitting failed: {str(e)}"}
