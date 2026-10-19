# ============================================================
# CONCEPT-LEVEL INTERACTIONS OF BOTH MODEL FAMILIES
# Reads the cached runs written by 01_AIA_SkinCon_tuned_models.ipynb and 02_AIA_SkinCon_baseline_models.ipynb
# (masked tables and predicted states of every seed) and writes two tables for the nonlinear heads on V12.
#   concept_loads.csv  For each concept, the share of images with the concept predicted present, its mean load in
#                      the odd part and in the even part of the removal game, and the certified sign of its mean
#                      removal effect with the images that an unresolved sign would need.
#   pair_labels.csv    For each concept pair, the certified sign of its mean Banzhaf interaction index and the
#                      label of Section 5.1: overlapping evidence (negative index) or evidence that matters only in
#                      combination (positive index), given only when both mean removal effects are certified positive.
# One union bound covers the 66 pair indices and the 12 removal effects of one head, model, game and population.
# The library functions are taken verbatim from the code cells of the experiment notebook.
# ============================================================
import ast, glob, json, os, pickle
import numpy as np
import pandas as pd

NOTEBOOK_DIR = os.environ.get("AIA_NOTEBOOK_DIR", "/content/drive/MyDrive/Notebooks/SkinCon/notebooks")  # folder of the package notebooks
EXPERIMENT_NOTEBOOK = os.path.join(NOTEBOOK_DIR, "01_AIA_SkinCon_tuned_models.ipynb")
FAMILIES = json.loads(os.environ.get("AIA_FAMILIES", json.dumps({
    "tuned": "/content/drive/MyDrive/Notebooks/SkinCon/outputs",
    "baseline": "/content/drive/MyDrive/Notebooks/SkinCon/AIA_outputs"})))
STAMPS = json.loads(os.environ["AIA_STAMPS"]) if "AIA_STAMPS" in os.environ else None
TARGET_DIR = os.environ.get("AIA_TARGET_DIR", os.path.join(FAMILIES["tuned"], "concept_level"))
os.makedirs(TARGET_DIR, exist_ok=True)
DELTA = 0.05
NUMERICAL_FLOOR = 1e-9

_nb = json.load(open(EXPERIMENT_NOTEBOOK))
_cells = ["".join(c["source"]) for c in _nb["cells"]]


def _definitions_only(src):
    tree = ast.parse(src)
    keep = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))]
    return ast.Module(body=keep, type_ignores=[])


exec(compile(_cells[9], "library cell", "exec"), globals())                            # Walsh and certificate library
exec(compile(_definitions_only(_cells[11]), "heads and games cell", "exec"), globals())  # games, tables and ranges
_ALLPROF = {}                                                                          # memo of the profile grid


class _Tolerant(pickle.Unpickler):
    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except Exception:
            return type(name, (), {"__setstate__": lambda self, st: self.__dict__.update(st if isinstance(st, dict) else {})})


POPS = {"malignant": 1, "non_malignant": 0}
GAMES = {"V12_mlp": ("zero", "marginal", "expected_zero"), "V12_deep": ("zero", "marginal")}
lat = lattice(12)
pl = pair_list(12)
sz = lat.size
member = np.zeros((lat.N, 12))
for T in range(1, lat.N):
    for j in range(12):
        if (T >> j) & 1:
            member[T, j] = 1.0 / sz[T]
odd_mask = (sz % 2 == 1).astype(float)
even_mask = ((sz % 2 == 0) & (sz >= 2)).astype(float)

loads, labels = [], []
_RANGES = {}
for fam, out_dir in FAMILIES.items():
    info = json.load(open(os.path.join(out_dir, "run_info.json")))
    names = [info["concept_names"][k] for k in info["vocabularies"]["V20"]]           # columns index V20
    for seed in info["seeds"]:
        if STAMPS is not None:
            path = os.path.join(out_dir, "cache", f"run_seed{seed}_{STAMPS[fam][str(seed)]}.pkl")
        else:                                        # the single cached run of this seed in the output folder
            found = glob.glob(os.path.join(out_dir, "cache", f"run_seed{seed}_*.pkl"))
            assert len(found) == 1, f"expected one cached run for {fam} seed {seed}, found {found}"
            path = found[0]
        with open(path, "rb") as fh:
            run = _Tolerant(fh).load()
        st = run["states"]
        for key, games in GAMES.items():
            h = run["heads"][key]
            cn = [names[c] for c in h["columns"]]
            for game in games:
                for pop, cls in POPS.items():
                    keep = h["pred"]["test"]["correct"] & (st["y_test"] == cls)
                    sign = 1.0 if cls == 1 else -1.0
                    tab = h["tables"]["zero" if game == "expected_zero" else game]
                    if game == "expected_zero":
                        probs = [np.stack([1 - st["prob_test"][keep][:, c], st["prob_test"][keep][:, c]], 1) for c in h["columns"]]
                        u = expected_hard_games(tab, probs, lat)
                        eps = float(np.abs(h["tables"]["zero"] - h["tables"]["zero32"]).max()) + NUMERICAL_FLOOR
                    else:
                        prof = st["hard_test"][keep][:, h["columns"]]
                        u = games_from_profiles(tab, prof, lat)
                        eps = float(np.abs(h["tables"][game] - h["tables"][game + "32"]).max()) + NUMERICAL_FLOOR \
                            if game + "32" in h["tables"] else NUMERICAL_FLOOR
                    u = sign * u
                    W = walsh_diagnostics(u, lat)
                    e2 = W["coef"] ** 2
                    V = np.where(W["V"] > 0, W["V"], 1.0)[:, None]
                    odd_load = (e2 * odd_mask) @ member / V
                    even_load = (e2 * even_mask) @ member / V
                    rkey = (fam, seed, key, "zero" if game == "expected_zero" else game, sign)
                    if rkey not in _RANGES:
                        _RANGES[rkey] = profile_ranges(sign * tab, [2] * 12, lat)
                    rng = _RANGES[rkey]
                    dl = DELTA / (len(pl) + 12)
                    base = {"family": fam, "seed": int(seed), "head": key, "game": game, "population": pop, "N": int(keep.sum())}
                    eff_sign = []
                    for j in range(12):
                        c = mean_certificate(W["effects"][:, j], rng["effects_min"][j], rng["effects_max"][j], dl)
                        s = c["bernstein_sign"] if abs(c["mean"]) > eps else 0
                        eff_sign.append(s)
                        loads.append({**base, "concept": cn[j], "present_share": float(st["hard_test"][keep][:, h["columns"][j]].mean()),
                                      "odd_load_mean": float(odd_load[:, j].mean()),
                                      "even_load_mean": float(even_load[:, j].mean()), "effect_mean": c["mean"],
                                      "effect_bernstein_radius": c["bernstein_radius"], "effect_sign": int(s),
                                      "effect_images_needed": c["images_needed_bernstein"]})
                    for i, (a, b) in enumerate(pl):
                        c = mean_certificate(W["I"][:, i], rng["I_min"][i], rng["I_max"][i], dl)
                        s = c["bernstein_sign"] if abs(c["mean"]) > eps else 0
                        lab = ""
                        if eff_sign[a] > 0 and eff_sign[b] > 0 and s != 0:
                            lab = "overlapping" if s < 0 else "combination"
                        labels.append({**base, "pair": f"{cn[a]} / {cn[b]}", "I_mean": c["mean"],
                                       "I_bernstein_radius": c["bernstein_radius"], "I_sign": int(s), "I_images_needed": c["images_needed_bernstein"],
                                       "effect_a_sign": int(eff_sign[a]), "effect_b_sign": int(eff_sign[b]), "label": lab})
            print(f"{fam} seed {seed}, {key}: done", flush=True)
pd.DataFrame(loads).to_csv(os.path.join(TARGET_DIR, "concept_loads.csv"), index=False)
pd.DataFrame(labels).to_csv(os.path.join(TARGET_DIR, "pair_labels.csv"), index=False)
print("Concept-level tables written to", TARGET_DIR)
