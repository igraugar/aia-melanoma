# Experiment notebooks

*Algebraic Interaction Analysis for Concept-Based Explanations in Skin Cancer Diagnosis*, Gonzalo Nápoles and Isel Grau.

These notebooks produce every simulation result of the paper. Their output tables are the content of `AIA_SkinCon_results.zip`, from which `AIA_SkinCon_figures_tables.ipynb` rebuilds every figure, table and number of the manuscript.

## Contents

| Notebook | Role | Output |
|---|---|---|
| `00_hyperparameter_search_tuned_models.ipynb` | Search that fixed the hyperparameters of the tuned models (validation images only). Supplementary, with its saved outputs. Its final setting used 40 epochs and Fitzpatrick17k training images only, whereas the reported tuned models use 30 epochs and the training images of both sources, as stated in the paper. | none needed by the paper |
| `01_AIA_SkinCon_tuned_models.ipynb` | Part 1 trains the tuned models (primary family). Part 2 runs Experiments 1 to 4 on them. This is the notebook that produced the reported results. Only its introduction cell was rewritten. | `outputs/` → `AIA_SkinCon_results/tuned/` |
| `02_AIA_SkinCon_baseline_models.ipynb` | The same analysis for the baseline models (replication family). This is the version that produced the reported baseline results. The introduction cell was rewritten, and the checkpoint folder is `models_baseline/`, so that the two families never overwrite each other's checkpoints (both use the same file names). | `AIA_outputs/` → `AIA_SkinCon_results/baseline/` |
| `03_export_image_level_tables.ipynb` | Image-level tables of the tuned models, computed from the cached runs of notebook 01 with its own functions. | `outputs/image_level/` → `AIA_SkinCon_results/image_level/` |
| `04_export_concept_level_tables.ipynb` | Concept loads, removal-effect certificates and labels of concept pairs (overlapping evidence or evidence that matters only in combination) for both families, computed from the cached runs of notebooks 01 and 02 with the functions of notebook 01. They answer Q1 to Q3 and give Tables 2 and 3. | `outputs/concept_level/` → `AIA_SkinCon_results/concept_level/` |

## Data

All notebooks expect one Google Drive folder, `PROJECT_DIR = /content/drive/MyDrive/Notebooks/SkinCon`:

```
SkinCon/
  skincon/annotations_fitzpatrick17k.csv, annotations_ddi.csv   SkinCon annotations, https://skincon-dataset.github.io
  fitzpatrick17k/fitzpatrick17k.csv                              metadata, https://github.com/mattgroh/fitzpatrick17k
  fitzpatrick17k/images/<md5hash>.jpg                            Fitzpatrick17k images
  ddi/ddi_metadata.csv and the DDI images                        https://ddi-dataset.github.io (research use agreement)
  splits/skincon_splits_fitz_ddi.csv, ..._vocabularies.json      frozen split, written by the first run and reused
  models/                                                        tuned checkpoints and manifest_skincon.json
  models_baseline/                                               baseline checkpoints
  outputs/, AIA_outputs/                                         results of notebooks 01 and 02
  notebooks/                                                     these notebooks (read by notebook 03)
```

## Running

1. Open the notebooks in Google Colab. Part 1 needs a GPU. Part 2 runs on CPU, never opens an image and reads only the checkpoints of Part 1.
2. Run `01_AIA_SkinCon_tuned_models.ipynb` from top to bottom. With `RUN_TRAINING = False` and `SKIP_TRAINED_SEEDS = True` (the reported setting), Part 1 reuses the checkpoints in `models/`. To retrain, set `RUN_TRAINING = True` and `SKIP_TRAINED_SEEDS = False` (the reported models took about 33 min per seed on a Colab GPU, as recorded in `manifest_skincon.json`).
3. Run `02_AIA_SkinCon_baseline_models.ipynb` in the same way, with its checkpoints in `models_baseline/`.
4. Run `03_export_image_level_tables.ipynb`, then `04_export_concept_level_tables.ipynb`.
5. Copy `outputs/csv`, `outputs/run_info.json`, `outputs/frozen_choices.json`, `outputs/console_log.txt`, `models/training_metrics.csv` and `models/manifest_skincon.json` into `AIA_SkinCon_results/tuned/`. Copy the corresponding baseline files into `AIA_SkinCon_results/baseline/` `outputs/image_level/` into `AIA_SkinCon_results/image_level/` and `outputs/concept_level/` into `AIA_SkinCon_results/concept_level/`.

Expensive steps are cached in `outputs/cache/`, so an interrupted run resumes where it stopped. Part 2 takes a few hours on a Colab CPU, mostly for the samplers of Experiment 1 and for the fits of Experiment 3 on 20 concepts.

## What reproduces exactly

* **From the frozen split file and the checkpoints of the paper**, Part 2 of both notebooks regenerates `AIA_SkinCon_results` exactly. Its only random steps use fixed seeds. We checked this for the tuned models (see the verification note below).
* **Without the frozen split file**, Part 1 rebuilds it from the same images with the fixed split seed (2024). The rebuilt split is identical only when all 3863 images are retrieved.
* **Retraining** on a GPU is not bit-for-bit deterministic. Retrained models give numbers close to, but not identical with, the paper. The structural findings of the paper are claims about such variation: they are reported only when they hold in all three retrained models under both removal rules.

The checkpoints and the frozen split file are too large for this package and are available from the authors.

## Verification note

We reran Part 2 of `01_AIA_SkinCon_tuned_models.ipynb` from the cached masked tables of the reported models, with every later cache removed. The inverse-temperature curves, null scales, identities, samplers, expected-hard games, controls, certificates, decision diagnostics, invisibility tests and index comparisons all agreed with `AIA_SkinCon_results/tuned` to within 2e-16 (1e-15 for sampler errors). Only the wall-clock columns (`seconds_*`) differ, since they depend on the hardware. `03_export_image_level_tables.ipynb` reproduced every file of `AIA_SkinCon_results/image_level` exactly, and `04_export_concept_level_tables.ipynb` reproduced every file of `AIA_SkinCon_results/concept_level` exactly from the same cached runs.
