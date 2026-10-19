# Simulation results

*Algebraic Interaction Analysis for Concept-Based Explanations in Skin Cancer Diagnosis*, Gonzalo Nápoles and Isel Grau.

Every csv file was written by the experiment notebooks and is unchanged. Each one carries a `table` column with the title it was printed under in the console log. Populations are the correctly classified malignant and non-malignant test images of a head. Games are `zero` (zero removal), `marginal` (marginal removal) and `expected_zero` (expected-hard game under zero removal). Heads are `V12_affine`, `V12_mlp`, `V12_deep`, `V16_mlp` and `V20_mlp`. The seeds 42, 64 and 128 are the three retrained models. The best-performing tuned model is seed 64 and the best-performing baseline model is seed 128.

## Folders

| Folder | Source |
|---|---|
| `tuned/` | Tuned models (primary family), written by `01_AIA_SkinCon_tuned_models.ipynb` (`outputs/` and `models/`) |
| `baseline/` | Baseline models (replication family), written by `02_AIA_SkinCon_baseline_models.ipynb` (`AIA_outputs/` and `models/`) |
| `image_level/` | Image-level tables of the tuned models, written by `03_export_image_level_tables.ipynb` |
| `concept_level/` | Concept loads and labels of concept pairs of both families, written by `04_export_concept_level_tables.ipynb` |
| `data/` | Printed output of the data cell of Part 1 (counts of images, duplicates, splits and concept prevalences) |

## Files in `tuned/` and `baseline/`

| File | Content | Used for |
|---|---|---|
| `training_metrics.csv` | Train, validation and test metrics of the concept predictor and of every head, per seed | Table 1, Section 7.1 |
| `manifest_skincon.json` (tuned only) | Training settings and checkpoint files of Part 1 | Section 6.2 |
| `run_info.json`, `frozen_choices.json` | Seeds, frozen inverse temperatures, null scales, vocabularies and the selected seed | Sections 6.1, 6.3, 7.1 |
| `console_log.txt` | Full console output of Part 2 | reference |
| `csv/heads.csv` | Population sizes and balanced accuracy per head and split | Section 7.1 |
| `csv/tuning_beta0.csv`, `csv/tuning_beta0_extension.csv` (tuned only) | Split-half agreement over the grid of beta0 values and above it | Section 7.1 |
| `csv/e1_identities.csv` | Lookup against direct evaluation, float32 table error, Banzhaf identity, forward against backward partition function | Section 7.4 |
| `csv/e1_sampler.csv`, `csv/e1_sampler_summary.csv` | Metropolis and replica exchange against the exact laws, per image and step count, with exact oscillation and R-hat | Figure 3a to c, Table 4, Section 7.4 |
| `csv/e1_expected_hard.csv` | Medians of the Monte Carlo expected-hard errors | Section 7.4 |
| `csv/e2_controls.csv`, `csv/e2_controls_summary.csv` | Non-additivity index, its certified lower bound and the even share per configuration | Sections 7.5 and 7.6, Tables 4 and 5 |
| `csv/e2_decisions.csv`, `csv/e2_decision_pairs.csv` | Joint flips, interaction flips, additive and even decision changes | Sections 7.5 and 7.6, Tables 4 and 5 |
| `csv/e2_invisibility.csv`, `csv/e2_invisibility_full.csv` | Changes of ranking quantities, Shapley and Banzhaf values after the even part is erased or reversed | Figure 4d, Sections 7.5 and 7.6, Table 4 |
| `csv/e2_indices.csv`, `csv/e2_indices_full.csv` | Agreement of other pair indices with the Banzhaf index, and odd share of Shapley-Taylor | Sections 7.5 and 7.6, Table 4 |
| `csv/e2_certificates.csv`, `csv/e2_certificates_summary.csv` | Hoeffding and empirical Bernstein certificates of every pair index, with images needed | Figure 7, Section 7.8 |
| `csv/e2_scalar_certificates.csv` | Certificates of the mean non-additivity index and of the mean even share | Section 7.8 |
| `csv/e3_summaries.csv`, `csv/e3_summary.csv`, `csv/e3_by_na.csv` | Maximum-entropy fits of the soft ranking and of the average positions per image | Figure 6, Section 7.7, Table 4 |
| `csv/e4_persistence.csv`, `csv/e4_persistent.csv`, `csv/e4_counts.csv`, `csv/e4_unresolved.csv` | Persistence of every certified population mean across seeds and removal rules | Section 7.8, Table 4 |

The baseline run predates the numerical floor of the certificates, so the baseline `e2_certificates.csv` keeps 33 affine pair signs whose means of order 1e-17 are rounding. The baseline `training_metrics.csv` has no concept AUROC column, so Table 1 prints n/a there. The quantity `NA` must be read with `keep_default_na=False`, otherwise pandas turns it into a missing value.

## Files in `image_level/`

| File | Content | Used for |
|---|---|---|
| `tuned_images.csv` | Per image: NA, NA_odd, NA_even, Walsh order shares (`order1` to `order12`), interaction flips, share of flipping pairs, even and additive decision changes | Figures 4 and 5, Sections 7.5 and 7.6 |
| `tuned_indices.csv` | Per image and method: rank correlation and top-pair agreement with the Banzhaf index, odd share of the Shapley-Taylor pair terms | Figure 5, Sections 7.5 and 7.6 |
| `tuned_pairs.csv`, `tuned_spectrum.csv` | Mean pair indices and mean Walsh spectra per population | reference |
| `e1_expected_hard_images.csv` | Per image and number of draws: sup-norm error, Banzhaf interaction error and Hoeffding bound, relative to the score scale | Figure 3d, Section 7.4 |

## Files in `concept_level/`

Both files cover the MLP head (games `zero`, `marginal`, `expected_zero`) and the deep head (games `zero`, `marginal`) on V12, for both families (`family` column). One union bound covers the 66 pair indices and the 12 removal effects of each head, model, game and population, and a mean below the float32 table error plus 1e-9 counts as rounding.

| File | Content | Used for |
|---|---|---|
| `concept_loads.csv` | Per concept: share of images with the concept predicted present, mean odd and even loads (fractions of the variance of the game), mean removal effect with its empirical Bernstein radius, certified sign and images needed | Table 2, Sections 7.2, 7.3 and 7.9 |
| `pair_labels.csv` | Per pair: mean Banzhaf interaction index with its radius, certified sign and images needed, certified signs of both removal effects, and the label (`overlapping`, `combination` or empty) | Table 3, Sections 7.3 and 7.9 |
