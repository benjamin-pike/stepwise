import libpysal
import numpy as np
import pandas as pd
from scipy.sparse.linalg import factorized


def moran_i(values, weights):
    centred = np.asarray(values) - np.mean(values)

    return float((weights.n / weights.s0) * (centred @ (weights.sparse @ centred)) / (centred @ centred))


def rank_match_columns(fields, target):
    order = np.argsort(fields, axis = 0)
    matched = np.empty_like(fields, dtype = float)
    matched[order, np.arange(fields.shape[1])] = np.sort(target)[:, None]

    return matched


def residualise(values, design_q):
    return values - design_q @ (design_q.T @ values)


def repaired_queen_weights(frame, id_column = 'LSOA21CD', x_column = 'centroid_x', y_column = 'centroid_y'):
    queen = libpysal.weights.Queen.from_dataframe(frame, use_index = False)
    neighbours = {i: list(values) for i, values in queen.neighbors.items()}
    weights = {i: [1.0] * len(values) for i, values in neighbours.items()}
    coordinates = frame[[x_column, y_column]].to_numpy()
    ids = frame[id_column].to_numpy() if id_column in frame.columns else frame.index.to_numpy()

    island_rows = []
    for island in queen.islands:
        squared_distance = ((coordinates - coordinates[island]) ** 2).sum(axis = 1)
        squared_distance[island] = np.inf
        neighbour = int(np.argmin(squared_distance))
        distance_km = float(np.sqrt(squared_distance[neighbour]) / 1000)
        neighbours[island].append(neighbour)
        weights[island].append(1.0)

        if island not in neighbours[neighbour]:
            neighbours[neighbour].append(island)
            weights[neighbour].append(1.0)

        island_rows.append(
            {
                'island_row': island,
                'island_lsoa': ids[island],
                'nearest_neighbour_row': neighbour,
                'nearest_neighbour_lsoa': ids[neighbour],
                'link_distance_km': distance_km
            }
        )

    repaired = libpysal.weights.W(neighbours, weights, id_order = list(range(len(frame))), silence_warnings = True)
    repaired.transform = 'r'

    return repaired, pd.DataFrame(island_rows)


def conditioned_residuals(fields, target, gradient_q, iterations = 3):
    candidate = rank_match_columns(fields, target)
    target_sd = np.std(target, ddof = 1)

    for _ in range(iterations):
        candidate = residualise(candidate, gradient_q)
        candidate *= target_sd / np.std(candidate, axis = 0, ddof = 1)
        candidate = rank_match_columns(candidate, target)

    candidate = residualise(candidate, gradient_q)
    candidate *= target_sd / np.std(candidate, axis = 0, ddof = 1)

    return candidate


def calibrate_rho(identity, weight_matrix, target_residual, gradient_q, weights, rng):
    target_i = moran_i(target_residual, weights)
    innovations = rng.standard_normal((len(target_residual), 60))

    def evaluate(rhos):
        records = []

        for rho in rhos:
            solver = factorized(identity - rho * weight_matrix)
            fields = solver(innovations)
            residuals = conditioned_residuals(fields, target_residual, gradient_q)
            values = [moran_i(residuals[:, draw], weights) for draw in range(fields.shape[1])]
            records.append((float(rho), float(np.mean(values)), float(np.std(values, ddof = 1))))

        return pd.DataFrame(records, columns = ['rho', 'expected_residual_moran_i', 'calibration_sd'])

    coarse = evaluate(np.arange(0.84, 0.981, 0.02))
    coarse_best = coarse.iloc[(coarse.expected_residual_moran_i - target_i).abs().argmin()].rho
    fine_lower, fine_upper = max(0.0, coarse_best - 0.025), min(0.999, coarse_best + 0.025)
    fine = evaluate(np.linspace(fine_lower, fine_upper, 21))

    calibration = pd.concat([coarse.assign(stage = 'coarse'), fine.assign(stage = 'fine')], ignore_index = True)
    selected = calibration.iloc[(calibration.expected_residual_moran_i - target_i).abs().argmin()]

    return float(selected.rho), float(selected.expected_residual_moran_i), target_i, calibration
