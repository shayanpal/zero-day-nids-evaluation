import os
import json
import time
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
import joblib

# GA v4: clean data (processed_v2), fitness measured on the REAL validation split
# (no synthetic SMOTE samples), macro-F1, cold start, fixed seeds, fitness cache.

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

d = os.path.expanduser("~/thesis/data/processed_v2")
X_tr = np.load(os.path.join(d, "X_train_bal.npy"))
y_tr = np.load(os.path.join(d, "y_train_bal.npy"))
X_val = np.load(os.path.join(d, "X_val_scaled.npy"))
le = joblib.load(os.path.join(d, "label_encoder.pkl"))
y_val = le.transform(pd.read_parquet(os.path.join(d, "y_val.parquet"))["Label"])

feature_names = [c for c in pd.read_parquet(os.path.join(d, "train.parquet")).columns if c != "Label"]
N_FEATURES = X_tr.shape[1]
assert len(feature_names) == N_FEATURES

# Classes with fewer than 10 validation samples are excluded from the fitness
# metric (too noisy); they are still present in training.
val_counts = pd.Series(y_val).value_counts()
FIT_LABELS = sorted(int(c) for c in val_counts[val_counts >= 10].index)
excluded = [str(le.classes_[c]) for c in range(len(le.classes_)) if c not in FIT_LABELS]
print(f"Train (balanced): {X_tr.shape}, Val (real): {X_val.shape}", flush=True)
print(f"Classes used in fitness: {len(FIT_LABELS)}, excluded (<10 val samples): {excluded}", flush=True)

ALPHA, BETA = 0.9, 0.1
POP_SIZE = 50
N_GENERATIONS = int(os.environ.get("GA_MAX_GEN", 120))
TOURNAMENT_K = 3
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.02
ELITISM = 3
PATIENCE = 20

cache = {}

def fitness(chrom):
    key = chrom.tobytes()
    if key in cache:
        return cache[key][0]
    sel = np.where(chrom == 1)[0]
    if len(sel) == 0:
        cache[key] = (0.0, 0.0)
        return 0.0
    clf = RandomForestClassifier(n_estimators=60, max_depth=16, n_jobs=-1, random_state=SEED)
    clf.fit(X_tr[:, sel], y_tr)
    pred = clf.predict(X_val[:, sel])
    f1 = f1_score(y_val, pred, labels=FIT_LABELS, average="macro", zero_division=0)
    fit = ALPHA * f1 + BETA * (1 - len(sel) / N_FEATURES)
    cache[key] = (fit, f1)
    return fit

def random_chromosome():
    c = np.random.randint(0, 2, size=N_FEATURES)
    if c.sum() == 0:
        c[random.randrange(N_FEATURES)] = 1
    return c

def tournament(pop, fits):
    idx = random.sample(range(len(pop)), TOURNAMENT_K)
    return pop[max(idx, key=lambda i: fits[i])].copy()

def crossover(p1, p2):
    if random.random() > CROSSOVER_RATE:
        return p1.copy(), p2.copy()
    pt = random.randint(1, N_FEATURES - 1)
    return np.concatenate([p1[:pt], p2[pt:]]), np.concatenate([p2[:pt], p1[pt:]])

def mutate(c):
    for i in range(N_FEATURES):
        if random.random() < MUTATION_RATE:
            c[i] = 1 - c[i]
    if c.sum() == 0:
        c[random.randrange(N_FEATURES)] = 1
    return c

population = [random_chromosome() for _ in range(POP_SIZE)]
best_fit, best_chrom, no_improve = -1.0, None, 0
history = []
t0 = time.time()

for gen in range(N_GENERATIONS):
    fits = [fitness(c) for c in population]
    i_best = int(np.argmax(fits))
    if fits[i_best] > best_fit:
        best_fit, best_chrom, no_improve = fits[i_best], population[i_best].copy(), 0
    else:
        no_improve += 1
    mins = (time.time() - t0) / 60
    best_f1 = cache[best_chrom.tobytes()][1]
    history.append({"gen": gen + 1, "minutes": round(mins, 2), "gen_best": fits[i_best],
                    "gen_mean": float(np.mean(fits)), "best_ever": best_fit,
                    "best_macro_f1": best_f1, "n_features": int(best_chrom.sum())})
    pd.DataFrame(history).to_csv(os.path.join(d, "ga_v4_history.csv"), index=False)
    print(f"Gen {gen+1:03d} | {mins:6.1f} min | gen best {fits[i_best]:.4f} | mean {np.mean(fits):.4f} | "
          f"best ever {best_fit:.4f} (macroF1 {best_f1:.4f}, {int(best_chrom.sum())} feats) | no-improve {no_improve}",
          flush=True)
    if no_improve >= PATIENCE:
        print(f"\nEarly stop: no improvement for {PATIENCE} generations (natural convergence)", flush=True)
        break
    order = np.argsort(fits)[::-1]
    new_pop = [population[i].copy() for i in order[:ELITISM]]
    while len(new_pop) < POP_SIZE:
        c1, c2 = crossover(tournament(population, fits), tournament(population, fits))
        new_pop.append(mutate(c1))
        if len(new_pop) < POP_SIZE:
            new_pop.append(mutate(c2))
    population = new_pop

selected = [feature_names[i] for i in range(N_FEATURES) if best_chrom[i] == 1]
print(f"\n=== GA v4 result ({(time.time()-t0)/60:.1f} min, {len(history)} generations) ===")
print(f"Best fitness: {best_fit:.4f} | val macro-F1: {cache[best_chrom.tobytes()][1]:.4f}")
print(f"Selected {len(selected)} / {N_FEATURES} features: {selected}")

with open(os.path.join(d, "selected_features.json"), "w") as f:
    json.dump(selected, f, indent=2)
np.save(os.path.join(d, "best_chromosome.npy"), best_chrom)
print("Saved to", d)
