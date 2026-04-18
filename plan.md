# Germany Housing Market Analysis — Full Project Plan

## Project Goal
Build a professional end-to-end portfolio project using Python + Tableau that demonstrates real-world data analyst skills: data sourcing, cleaning, transformation, analysis, dashboarding, storytelling, and documentation.

---

## Final Deliverables
- Clean GitHub repository
- Tableau dashboard
- Polished README with screenshots
- Python data pipeline scripts
- Key business insights report
- Optional forecasting/modeling extension

---

## Recommended Repo Structure

```text
germany-housing-market-analysis/
│── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
│── src/
│   ├── 01_download_data.py
│   ├── 02_clean_data.py
│   ├── 03_transform_data.py
│   ├── 04_eda.py
│   ├── 05_export_for_tableau.py
│
│── tableau/
│   ├── germany_housing_dashboard.twbx
│
│── outputs/
│   ├── charts/
│   ├── tables/
│   └── insights_summary.md
│
│── images/
│   ├── dashboard_preview.png
│   ├── map_preview.png
│
│── docs/
│   ├── data_dictionary.md
│   ├── methodology.md
│
│── requirements.txt
│── .gitignore
│── README.md
```

---

## Tech Stack
- Python
- pandas
- numpy
- matplotlib / plotly
- Tableau
- Git + GitHub
- Optional: scikit-learn

---

## Main Business Questions
1. Which cities have the highest rents?
2. Which cities are most affordable?
3. Rent per m² by city/state
4. How do size, rooms, and location affect price?
5. How does Munich compare with other major cities?
6. Which regions are rising fastest?
7. Which areas offer the best rental yield (annual rent / property price)?
8. Which regions show the strongest price appreciation?
9. Which markets offer best ROI for real estate investors?

---

## 14-Day Execution Plan

## Day 1 — Setup + Scope
- [ ] Create GitHub repo
- [x] Create folder structure
- [ ] Write project objective in README
- [ ] Find 1–2 Germany housing datasets
- [ ] Define KPIs

## Day 2 — Raw Data Collection
- [ ] Download CSV files / scrape legal public data
- [ ] Save into data/raw/
- [ ] Inspect columns and row counts
- [ ] Create data_dictionary.md draft

## Day 3 — Cleaning Part 1
- [ ] Remove duplicates
- [ ] Fix missing values
- [ ] Standardize city names
- [ ] Standardize price column

## Day 4 — Cleaning Part 2
- [ ] Standardize area (m²)
- [ ] Remove impossible values
- [ ] Convert datatypes
- [ ] Save processed dataset

## Day 5 — Feature Engineering
- [ ] Create price_per_m2
- [ ] Create region/state field
- [ ] Create affordability bands
- [ ] Create property size categories

## Day 6 — Exploratory Analysis
- [ ] Top expensive cities
- [ ] Cheapest cities
- [ ] Distribution of rents
- [ ] Correlation checks
- [ ] Export charts to outputs/charts/

## Day 7 — Munich Deep Dive
- [ ] Munich vs Berlin vs Hamburg vs Frankfurt
- [ ] Premium districts if available
- [ ] Summary notes

## Day 8 — Tableau Data Prep
- [ ] Export final CSV for Tableau
- [ ] Verify column names and formats
- [ ] Create KPI table if needed

## Day 9 — Tableau Dashboard Page 1
Executive Overview:
- [ ] Avg rent
- [ ] Avg price/m²
- [ ] Listings count
- [ ] Germany map
- [ ] Top cities ranking

## Day 10 — Tableau Dashboard Page 2
City Comparison:
- [ ] Compare selected cities
- [ ] Trend lines
- [ ] Filters
- [ ] Drilldowns

## Day 11 — Tableau Dashboard Page 3
Market Drivers:
- [ ] Size vs price
- [ ] Rooms vs price
- [ ] Furnished vs unfurnished (if available)
- [ ] Heatmaps

## Day 12 — Insights + Storytelling
Write 8–10 business insights:
- [ ] Munich X% above national avg
- [ ] Leipzig fastest growing etc.

## Day 13 — README Polish
Include:
- [ ] project overview
- [ ] tools used
- [ ] methodology
- [ ] screenshots
- [ ] findings
- [ ] how to run
- [ ] future improvements

## Day 14 — Final Publish
- [ ] Push clean commits
- [ ] Share on LinkedIn
- [ ] Add project to CV
- [ ] Ask for feedback

---

## Daily Routine (2–3 Hours)
1. 15 min review yesterday work
2. 90 min focused build session
3. 30 min debugging / cleanup
4. 30 min documentation
5. Commit to GitHub daily

---

## Git Commit Examples
- init project structure
- add raw housing dataset
- clean price and area fields
- add city comparison analysis
- build tableau executive dashboard
- finalize README

---

## Tableau Dashboard Layout

## Page 1: Germany Overview
- KPI cards
- Filled map
- Top 10 cities bar chart

## Page 2: Compare Cities
- Parameter selector
- Trends
- Rent per m² comparisons

## Page 3: Munich Spotlight
- Munich vs national avg
- Districts if available
- Market summary

## Page 4: Price Drivers
- Scatterplots
- Histograms
- Segments

---

## README Template

## Title
Germany Housing Market Analysis

## Overview
End-to-end analytics project using Python + Tableau.

## Dataset
Source(s), scope, date range.

## Tools
Python, pandas, Tableau.

## Process
Collect → Clean → Analyze → Visualize.

## Key Insights
Bullet list.

## Dashboard Preview
Insert screenshots.

## How to Run
pip install -r requirements.txt
python src/02_clean_data.py

---

## Quality Checklist Before Publishing
- Clean folder structure
- No messy notebooks unless intentional
- Meaningful commits
- Screenshots included
- README readable in 2 minutes
- No broken files
- Consistent naming

---

## Stretch Goals
- Forecast future rents
- Streamlit app
- Automated monthly refresh
- SQL database version
- German-language dashboard version

---

## Success Outcome
A recruiter should think:
“This person can do real analyst work already.”

