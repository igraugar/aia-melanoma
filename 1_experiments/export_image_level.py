# ============================================================
# IMAGE-LEVEL TABLES OF THE TUNED MODELS
# Reads the cached runs written by 01_AIA_SkinCon_tuned_models.ipynb (masked tables and predicted states of every
# seed) and writes the image-level tables behind Figures 3 and 4 and several numbers of the Results section. It also
# writes the image-level Monte Carlo expected-hard table behind Figure 2d. The library functions are taken verbatim
# from the code cells of the experiment notebook, so no formula is duplicated here.
# ============================================================
import ast, json, os, pickle, sys
import numpy as np
import pandas as pd
import scipy.stats as sps

EXPERIMENT_NOTEBOOK = "01_AIA_SkinCon_tuned_models.ipynb"
OUTPUT_DIR = os.environ.get("AIA_OUTPUT_DIR", "/content/drive/MyDrive/Notebooks/SkinCon/outputs")
CACHE_DIR = os.path.join(OUTPUT_DIR, "cache")
TARGET_DIR = os.path.join(OUTPUT_DIR, "image_level")
os.makedirs(TARGET_DIR, exist_ok=True)

_nb = json.load(open(EXPERIMENT_NOTEBOOK))
_cells = ["".join(c["source"]) for c in _nb["cells"]]


def _definitions_only(src):
    """Function, class and import statements of a cell, without the code that runs the experiments."""
    tree = ast.parse(src)
    keep = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))]
    return ast.Module(body=keep, type_ignores=[])


exec(compile(_cells[9], "library cell", "exec"), globals())                          # ranking-law library
exec(compile(_definitions_only(_cells[11]), "heads and games cell", "exec"), globals())  # games and head classes

MODELS_DIR = os.environ.get("AIA_MODELS_DIR", "/content/drive/MyDrive/Notebooks/SkinCon/models")


def _function_named(src, name):
    tree = ast.parse(src)
    return ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name], type_ignores=[])


info = json.load(open(os.path.join(OUTPUT_DIR, "run_info.json")))
SEEDS = info["seeds"]
SELECTED = info["selected_seed"]
if "AIA_STAMPS" in os.environ:                       # only for checks outside Colab, e.g. {"42": "87489087ce", ...}
    STAMPS = {int(k): v for k, v in json.loads(os.environ["AIA_STAMPS"]).items()}
else:                                                # the fingerprint that the experiment notebook itself uses
    MANIFEST = json.load(open(os.path.join(MODELS_DIR, "manifest_skincon.json")))
    exec(compile(_function_named(_cells[7], "model_stamp"), "model_stamp", "exec"), globals())
    STAMPS = {s: model_stamp(s) for s in SEEDS}
print("Cached runs:", STAMPS)


class _Tolerant(pickle.Unpickler):
    """Loads the cached runs; objects that only serve model evaluation are not needed here."""
    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except Exception:
            return type(name, (), {"__setstate__": lambda self, st: self.__dict__.update(st if isinstance(st, dict) else {})})


POPS = {"malignant": 1, "non_malignant": 0}
lat = lattice(12)
pl = pair_list(12)
rows, pairs, spec, ind = [], [], [], []
for seed in SEEDS:
    with open(os.path.join(CACHE_DIR, f"run_seed{seed}_{STAMPS[seed]}.pkl"), "rb") as fh:
        run = _Tolerant(fh).load()
    st = run["states"]
    for key in ("V12_affine", "V12_mlp", "V12_deep"):
        h = run["heads"][key]
        for game in ("zero", "marginal", "expected_zero"):
            if game == "expected_zero" and key != "V12_mlp":
                continue
            for pop, cls in POPS.items():
                keep = h["pred"]["test"]["correct"] & (st["y_test"] == cls)
                prof = st["hard_test"][keep][:, h["columns"]]
                sign = 1.0 if cls == 1 else -1.0
                if game == "expected_zero":
                    probs = [np.stack([1 - st["prob_test"][keep][:, c], st["prob_test"][keep][:, c]], 1)
                             for c in h["columns"]]
                    u = expected_hard_games(h["tables"]["zero"], probs, lat)
                else:
                    u = games_from_profiles(h["tables"][game], prof, lat)
                u = sign * u
                W = walsh_diagnostics(u, lat)
                c = walsh(u)
                sz = lat.size
                var = (c[:, 1:] ** 2).sum(1)
                for k in range(1, 13):
                    spec.append({"seed": int(seed), "head": key, "game": game, "population": pop, "order": k,
                                 "share_mean": float(np.mean((c[:, sz == k] ** 2).sum(1) / np.maximum(var, 1e-300)))})
                D = decision_diagnostics(u, lat)
                os_ = W["order_share"]
                for i in range(len(u)):
                    r = {"seed": int(seed), "head": key, "game": game, "population": pop, "image": i,
                         "NA": W["NA"][i], "NA_odd": W["NA_odd"][i], "NA_even": W["NA_even"][i], "u0": u[i, 0],
                         "interaction_flip": bool(D["interaction_flip"][i]),
                         "interaction_flip_pair_share": float(D["interaction_flip_pairs"][i].mean()),
                         "even_change": float(D["even_erasure_decision_change"][i]),
                         "additive_change": float(D["additive_decision_change"][i])}
                    for k in range(1, 13):
                        r[f"order{k}"] = os_[i, k - 1]
                    rows.append(r)
                if game == "zero" and key != "V12_affine":
                    idx = interaction_indices(u, lat)
                    _, odd, even = parity_parts(u, lat)
                    st_odd = interaction_indices(odd, lat)["shapley_taylor"]
                    B_ = idx["banzhaf"]
                    for m, v in idx.items():
                        for i in range(len(u)):
                            rho = sps.spearmanr(v[i], B_[i])[0] if np.std(v[i]) > 0 and np.std(B_[i]) > 0 else np.nan
                            ind.append({"seed": int(seed), "head": key, "population": pop, "image": i, "method": m,
                                        "spearman": rho,
                                        "top_agree": bool(np.abs(v[i]).argmax() == np.abs(B_[i]).argmax()),
                                        "st_odd_share": float(np.linalg.norm(st_odd[i]) / max(np.linalg.norm(v[i]), 1e-300))
                                        if m == "shapley_taylor" else np.nan})
                Imean = W["I"].mean(0)
                for j, (a, b) in enumerate(pl):
                    pairs.append({"seed": int(seed), "head": key, "game": game, "population": pop, "a": a, "b": b,
                                  "I_mean": Imean[j]})
        print(f"seed {seed}, {key}: done", flush=True)
pd.DataFrame(rows).to_csv(os.path.join(TARGET_DIR, "tuned_images.csv"), index=False)
pd.DataFrame(pairs).to_csv(os.path.join(TARGET_DIR, "tuned_pairs.csv"), index=False)
pd.DataFrame(spec).to_csv(os.path.join(TARGET_DIR, "tuned_spectrum.csv"), index=False)
pd.DataFrame(ind).to_csv(os.path.join(TARGET_DIR, "tuned_indices.csv"), index=False)

# image-level Monte Carlo expected-hard errors of the model studied in depth (Figure 2d)
eh = pd.read_pickle(os.path.join(CACHE_DIR, f"e1_expected_hard_seed{SELECTED}_{STAMPS[SELECTED]}.pkl"))
eh.to_csv(os.path.join(TARGET_DIR, "e1_expected_hard_images.csv"), index=False)
print("Image-level tables written to", TARGET_DIR)
