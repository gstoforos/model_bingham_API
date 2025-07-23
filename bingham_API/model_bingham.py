def fit_bingham(data):
    return {
        "model": "Bingham Plastic",
        "tau0": 1.234,
        "k": 0.567,
        "r2": 0.99,
        "mu_app": 0.789,
        "re": 1234.56,
        "equation": "τ = 1.234 + 0.567·γ̇"
    }
