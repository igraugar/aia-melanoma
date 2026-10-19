# Reproducibility package

*Algebraic Interaction Analysis for Concept-Based Explanations in Skin Cancer Diagnosis*, Gonzalo Nápoles and Isel Grau, submitted to Information Fusion.

This package holds the code that produced every simulation result of the article, the results themselves, and the notebook that rebuilds every figure, table and number of the article from these results. Readers can verify the article from the results alone in about one minute, without a GPU and without the image data.

## Contents

| Folder | Content | Produced by |
|---|---|---|
| `1_experiments/` | Notebooks 00 to 04 and the two export scripts that train the models and run Experiments 1 to 4. Its `README.md` documents each notebook, the data layout and the expected run times. | The authors, on Google Colab |
| `2_results/AIA_SkinCon_results/` | Every csv, json and log file written by the notebooks of `1_experiments/`, unchanged. Its `README.md` describes every file and the part of the article that uses it. | `1_experiments/` |
| `3_figures_and_tables/` | `AIA_SkinCon_figures_tables.ipynb`, which rebuilds Figures 1 to 7 and Tables 1 to 5 and recomputes 186 numbers in the text. Its `README.md` explains how to run it. `reference_figures/` holds the seven figure files of the article for the pixel comparison of the last cell. | `2_results/` |

## Quick verification from the results

1. Install Python 3.11 with numpy, pandas, scipy, matplotlib, seaborn and jupyter (optionally PyMuPDF for the pixel comparison).
2. Make the results visible next to the notebook, for instance, with `ln -s ../2_results/AIA_SkinCon_results 3_figures_and_tables/AIA_SkinCon_results` (or copy the folder).
3. Add the folder `3_figures_and_tables/assets/` described below, then run all cells of `AIA_SkinCon_figures_tables.ipynb`.

The notebook compares Tables 1 to 5 character for character with the article and stops at the first number of the text that differs from its recomputed value. In the shipped run, all 186 checks pass and all seven figures have identical pixels. The notebook is shipped executed, so its outputs can also be read without running it.

## Full reproduction from the images

1. Download the SkinCon annotations (https://skincon-dataset.github.io), the Fitzpatrick17k metadata and images (https://github.com/mattgroh/fitzpatrick17k) and the Diverse Dermatology Images (https://ddi-dataset.github.io, under its research use agreement), and arrange them as `1_experiments/README.md` describes.
2. Run `01_AIA_SkinCon_tuned_models.ipynb` and `02_AIA_SkinCon_baseline_models.ipynb` in Google Colab. Part 1 of each notebook trains the models on a GPU (about 33 minutes per seed), and Part 2 runs Experiments 1 to 4 on a CPU (a few hours, mostly for the samplers and for the fits on 20 concepts).
3. Run `03_export_image_level_tables.ipynb` and then `04_export_concept_level_tables.ipynb`.
4. Copy the outputs into `2_results/AIA_SkinCon_results/` as step 5 of `1_experiments/README.md` lists, and run the notebook of `3_figures_and_tables/`.

`00_hyperparameter_search_tuned_models.ipynb` documents the search on validation images that fixed the settings of the tuned models. The article does not need its outputs.

## What reproduces exactly

From the frozen split file and the model checkpoints of the article, Part 2 of both experiment notebooks regenerates `2_results/` exactly, since its only random steps use fixed seeds. Without the frozen split file, Part 1 rebuilds the same split with the fixed split seed 2024, provided that all 3863 images are retrieved. Retraining on a GPU is not bit-for-bit deterministic, so retrained models give numbers close to, but not identical with, the article. The structural findings of the article are claims about this variation, since we report them only when they hold in all three retrained models under both removal rules.

## Items not included

| Item | Reason | How to obtain it |
|---|---|---|
| Model checkpoints and the frozen split file | Too large for this package | From the authors upon request |
| Images of SkinCon, Fitzpatrick17k and the Diverse Dermatology Images | Third-party data under their own terms | From the sources listed above |
| `3_figures_and_tables/assets/` (`lesion1.png` for the schematic of Figure 1, and the nine Fitzpatrick17k images of Figure 2 in `samples/` with their metadata rows) | Third-party images | Place the nine images shown in Figure 2 (with their metadata rows) and a lesion thumbnail in this folder, since the first cell of the notebook checks for them. All other figures and every table and number need only `2_results/`. |

## Correspondence between the article and this package

| Part of the article | Results files | Notebook cell |
|---|---|---|
| Section 6.1 (data and splits) | `data/part1_data_summary.txt`, `tuned/run_info.json` | Numbers of the text |
| Section 6.2 and Table 1 (models) | `tuned/` and `baseline/` `training_metrics.csv`, `manifest_skincon.json` | Table 1 |
| Section 7.2 and Table 2 (concept loads) | `concept_level/concept_loads.csv` | Table 2 |
| Section 7.3 and Table 3 (labels of concept pairs) | `concept_level/pair_labels.csv` | Table 3 |
| Section 7.4 and Figure 3 (computation) | `e1_sampler.csv`, `image_level/e1_expected_hard_images.csv` | Figure 3 |
| Sections 7.5 and 7.6, Figures 4 and 5 (interactions and decisions) | `e2_controls.csv`, `e2_decisions.csv`, `e2_invisibility_full.csv`, `e2_indices*.csv`, `image_level/tuned_images.csv`, `image_level/tuned_indices.csv` | Figures 4 and 5 |
| Section 7.7 and Figure 6 (compact displays) | `e3_summaries.csv` | Figure 6 |
| Section 7.8, Table 4 and Figure 7 (persistence) | `e2_certificates.csv`, `e2_scalar_certificates.csv`, `e4_*.csv` | Table 4 and Figure 7 |
| Section 7.9 and Table 5 (population report) | `e2_controls.csv`, `e2_decisions.csv`, `concept_level/` | Table 5 |

A few check labels in the last code cell quote an earlier wording of the article. Every recomputed value matches the submitted text.
