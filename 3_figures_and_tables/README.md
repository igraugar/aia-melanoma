# Figures, tables and numbers of the paper

*Algebraic Interaction Analysis for Concept-Based Explanations in Skin Cancer Diagnosis*, Gonzalo Nápoles and Isel Grau.

`AIA_SkinCon_figures_tables.ipynb` rebuilds every figure and every table of the manuscript exactly as printed, from the simulation results alone. It also recomputes every number quoted in the text. The notebook is shipped executed, so its outputs can be read without running it.

## Running

1. Unzip `AIA_SkinCon_results.zip` next to the notebook, which gives the folder `AIA_SkinCon_results/`.
2. Install Python 3.11 with numpy, pandas, scipy, matplotlib, seaborn and jupyter. PyMuPDF is optional and enables the pixel comparison of the last cell. The manuscript figures were produced with numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, matplotlib 3.10.9 and seaborn 0.13.2. Other versions can change the rendering slightly, never the data.
3. Run all cells (about one minute).

## Output

* `output/fig0_pipeline.pdf` (Figure 1), `fig1_samples.pdf` (Figure 2), `fig2_computation.pdf` (Figure 3), `fig3_parity.pdf` (Figure 4), `fig4_decisions.pdf` (Figure 5), `fig6_summaries.pdf` (Figure 6) and `fig5_pairs.pdf` (Figure 7), with the file names that the manuscript includes, plus PNG previews.
* `output/tables/table1_performance.tex` (Table 1), `table4_concepts.tex` (Table 2), `table5_labels.tex` (Table 3), `table2_findings.tex` (Table 4) and `table3_report.tex` (Table 5), the LaTeX bodies of the five tables.

## Checks performed by the notebook

* Tables 1 to 5 are compared character for character with the manuscript.
* 186 numbers of the text are recomputed and compared with their printed values: data and splits, model settings, trained models, exact computation, non-additivity and parity, compact summaries, persistence, the population report, and the abstract, introduction and conclusions. Every failure stops the notebook.
* The rebuilt figures are compared pixel by pixel, at 150 dpi, with the manuscript figures in `reference_figures/`.

In the shipped run, all checks pass and all seven figures have identical pixels.

## Inputs

Only `AIA_SkinCon_results/`, `assets/lesion1.png` (the lesion thumbnail of the schematic in Figure 1) and `assets/samples/` (the nine Fitzpatrick17k images of Figure 2 with their rows of the Fitzpatrick17k metadata) are read. `AIA_SkinCon_results/README.md` describes every file.
