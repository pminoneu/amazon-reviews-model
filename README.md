# Assignment 6: Proposal Team Package

This package contains the proposal and supporting materials for this assignment. Team members can read the report, inspect the code, review the images and use the Streamlit app from the included result tables.

**Repository note.** The large raw Amazon data files in `data/` are intentionally excluded from version control. They are not required to run the Streamlit interface. Team members who need to reproduce the analysis can download the source files using the links recorded in `results/audit.json`.

**The required submission is only `submission/Assignment6_Proposal_Early_Product_Success.pdf`: two proposal pages plus one app-sketch page. The other files support team review and reproducibility; the supplied assignment screenshots do not require them as separate submission attachments.**

## Start here

1. `submission/Assignment6_Proposal_Early_Product_Success.pdf`: the report covering all six required sections.
2. `images/target_distribution.png`: the target distribution plotted from the actual data.
3. `images/app_sketch.png`: sketches of the Predict and Explore screens.
4. `results/dataset_overview.csv`, `baseline_scores.csv`, and `target_distribution.csv`: compact result tables that can be opened directly.
5. `scripts/analyze_proposal.py`: data cleaning, sample construction, label generation, splitting, baseline evaluation, and plotting.
6. `DATA_DICTIONARY.md`: file descriptions, column definitions, and methodological conventions.

## Package contents

| Location | Contents |
| --- | --- |
| `submission/` | The three-page PDF required for this assignment |
| `scripts/` | Analysis, verification, table-export, and PDF-generation code |
| `data/` | Two complete original datasets, compressed as `.jsonl.gz` and readable directly by the code |
| `results/` | Product-level tables, summary tables, audit and verification records, and the target-distribution plot |
| `images/` | The standalone distribution plot, previews of the first two report pages, and the app sketch |
| `references/` | The original Idea 4 document and three assignment screenshots; the revised report corrects statistics from the original idea |
| `proposal_content.md` | A generated Markdown reading copy of the report text |
| `requirements.txt` | Direct dependencies needed to run the code |
| `tested_versions.json` | Dependency versions observed in the local environments used for verification |
| `MANIFEST.json` | File sizes and SHA-256 hashes for checking package integrity |

## Results already computed

- Raw reviews: 701,528; exact duplicate records removed: 7,275; remaining reviews: 694,253.
- Eligible products: 5,709; positive labels: 836; negative labels: 4,873.
- Training / test products: 3,996 / 1,713; 70/30 split with random seed 42.
- `is_successful = 1` when a product receives at least 24 additional reviews averaging at least 4.0 stars during the 365 days after review 20.
- The 24-review threshold is the training set's 75th percentile of subsequent review counts. The same threshold is applied to the test set.
- The baseline always predicts class 0: balanced accuracy = 0.50, accuracy = 84.47%, and positive-class recall = 0.

The 35% value in the sketch is explicitly illustrative. The 0.65-0.70 range in the proposal is the pre-model expectation requested by the assignment. Neither is a measured model result.

## Running the code

Use Python 3.11 or later. Open a terminal in the extracted package folder containing this README. The supplied PDF, images, and CSV files can be reviewed without running any code.

Create a virtual environment:

```sh
python -m venv .venv
```

Activate it on macOS or Linux:

```sh
source .venv/bin/activate
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies and reproduce the proposal analysis:

```sh
python -m pip install -r requirements.txt
python scripts/analyze_proposal.py
python scripts/export_tables.py
python scripts/verify_evidence.py
```

The analysis regenerates the tables, audit file, and distribution plot in `results/`. No data download is needed: the original files are included in `data/`.

To regenerate the PDF:

```sh
python scripts/build_proposal_pdf.py
```

The PDF is written to `submission/`, and the reading copy is written to `proposal_content.md`. Existing files with those names are updated. The layout uses an installed Arial font when available and falls back to Helvetica otherwise. After rebuilding on another computer, confirm that the PDF still has three pages and that text and figures are not clipped.

**The editable source of the report text is the `sections` variable in `scripts/build_proposal_pdf.py`.** Editing only `proposal_content.md` will not update the PDF. If the data definitions change, update and recheck the numerical claims in the report. The report previews and app sketch in `images/` are saved copies of the current version; the commands above do not automatically refresh those previews.

## Remaining submission details

- Confirm and add team members' names and individual responsibilities. The report assigns the main implementation work to the team lead; the other members' individual assignments remain to be confirmed.
- Post the PDF from `submission/` to the team's Slack project channel before class on November 5, as specified in the supplied assignment screenshots.

## Sources and code notes

The original data comes from McAuley Lab's [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/). Download links and original-file hashes are recorded under `sources` in `results/audit.json`.

The package preserves the original calculations. File paths and font fallback handling were adapted so teammates can run the scripts from the extracted folder. The original data, CSV outputs, and PDF were verified. Local virtual environments, caches, and unrelated files are excluded.
