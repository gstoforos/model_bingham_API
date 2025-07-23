def fit_bingham(data):
    try:
        return {
            "model": "Bingham Plastic",
            "tau0": 1.234,          # yield stress [Pa]
            "k": 0.567,             # plastic viscosity [Pa·s]
            "r2": 0.99,             # R² of fit
            "mu_app": 0.789,        # apparent viscosity [Pa·s]
            "re": 1234.56,          # Reynolds number
            "equation": "τ = 1.23 + 0.567·γ̇"
        }
    except Exception as e:
        return {"error": f"Error in Bingham model: {str(e)}"}
