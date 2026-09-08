import os
import sys
import logging
import pandas as pd
import numpy as np
from IPython.display import display, Markdown

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ── Pandas display options ──
pd.set_option('display.max_columns', 5)
pd.set_option('display.max_rows', 200)
pd.set_option('display.width', 180)
pd.set_option('display.float_format', '{:.2f}'.format)

# ── Paths ──
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "immo_data.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
CLEAN_PATH = os.path.join(PROCESSED_DIR, "immo_data_clean.csv")

df =pd.read_csv(RAW_PATH) 
df.head()
df.tail()
ret = df.sample(5)
df.shape
df.columns

print(df.tail())

#print(df.info())
#print(df.dtypes)
#print(df.isnull().sum())
#print((df.isnull().mean() * 100).sort_values(ascending=False))