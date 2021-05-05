filter_settings = {
    "time_stretch": {
        "range": (0.8, 1.5),
        "probability": 0.3
    },
    "harmonic_remove": {
        "range": (1, 5),  # margin_range
        "probability": 0.05
    },
    "percussive_remove": {
        "range": (1, 5),  # margin
        "probability": 0.05
    },
    "randon_noise": {
        "range": (0.96, 1),  # PSNR range
        "probability": 0.05
    },
    "realse_noise": {
        "range": (0.15, 0.65),
        "probability": 0.25,
    },
    "reverb": {
        "range": (5, 50),
        "probability": 0.15,
    },
    "bandpass": {
        "range": (0, 1000),
        "probability": 0.1
    },
    "tremolo": {
        "range": (100, 8000),
        "probability": 0.1
    }
}

assert not False in [0 <= filter_settings[key]["probability"] <= 1 for key in
                     filter_settings.keys()], "Probability Range = 0..1"
