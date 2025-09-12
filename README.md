# Bike Sharing Analysis & Streamlit Dashboard

This is a complete submission package for the **Dicoding Proyek Analisis Data** using the **Bike Sharing** dataset (UCI).

## Folder Structure

```
submission/
├── dashboard/
│   └── dashboard.py
├── data/
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Business Questions
1. **Kapan (jam & hari) permintaan sewa sepeda mencapai puncak, dan bagaimana polanya antar musim?**
2. **Faktor apa yang paling berkorelasi dengan total penyewaan (cnt) pada data harian?**

## Run Locally

### 1) Setup environment
```bash
pip install -r requirements.txt
```

### 2) Run Jupyter Notebook
```bash
jupyter notebook
# open notebook.ipynb and run all cells
```

### 3) Run Streamlit Dashboard
```bash
cd dashboard
streamlit run dashboard.py
```

## Deploy to Streamlit Community Cloud
1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io , connect your repo, pick `dashboard/dashboard.py` as the entry file.
3. Put the deployed URL into `url.txt` (already created).

## Notes
- Dataset source: UCI Bike Sharing. Files used: `day.csv`, `hour.csv`.
- The notebook includes: data loading, cleaning, EDA, visualization, and conclusions with clear markdown documentation.
- The dashboard offers interactive filtering by **season** and **workingday** with several charts.

Good luck!
