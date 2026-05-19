import numpy as np
from scipy.integrate import solve_ivp

def lotka_volterra(t, y, birth_rate, predation_rate, efficiency, death_rate, winter_severity=1.0):
    moose, wolves = y

    effective_predation = predation_rate * winter_severity
    effective_birth = birth_rate / winter_severity

    dmoose = (effective_birth * moose) - (effective_predation * wolves * moose)
    dwolves = (efficiency * effective_predation * wolves * moose) - (death_rate * wolves)

    return [dmoose, dwolves]


def run_simulation(years=50, initial_moose=600, initial_wolves=20,
                   birth_rate=0.4, predation_rate=0.01,
                   efficiency=0.075, death_rate=0.5,
                   winter_severity=1.0):

    t_span = (0, years)
    t_eval = np.linspace(0, years, years * 12)
    y0 = [initial_moose, initial_wolves]
    params = (birth_rate, predation_rate, efficiency, death_rate, winter_severity)

    result = solve_ivp(
        lotka_volterra,
        t_span,
        y0,
        args=params,
        t_eval=t_eval,
        method='RK45'
    )

    return result.t, result.y[0], result.y[1]