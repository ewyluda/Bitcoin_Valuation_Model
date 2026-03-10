# Bitcoin Valuation Model - Agent Documentation

## Project Overview

This is a data science research project that implements a Bitcoin valuation model based on Metcalfe's Law. The model estimates whether Bitcoin's current price is supported by network activity, using Daily Active Addresses (DAA) as the primary metric.

The fundamental hypothesis is that Bitcoin's network value (market cap) is related to the square of its daily active users, similar to how telecommunications networks are valued according to Metcalfe's Law.

### Key Concepts

- **Metcalfe's Law (NV ~ n²):** Network value is proportional to the square of connected users. Used as the upper fundamental boundary.
- **Odlyzko's Law (NV ~ n×ln(n)):** A more conservative variation accounting for unequal user contributions. Used as the lower fundamental boundary.
- **Generalized Metcalfe's Law (NV ~ n^1.5):** An intermediate variation.
- **NVT Ratio:** Network Value to Transactions ratio, often called the "crypto PE ratio".

## Technology Stack

- **Language:** Python 3.7+
- **Environment:** Jupyter Notebook
- **Core Dependencies:**
  - `pandas` - Data manipulation and analysis
  - `numpy` - Numerical computing
  - `matplotlib` - Data visualization
  - `datetime` - Date handling

## Project Structure

```
Bitcoin_Valuation_Model/
├── model.ipynb              # Main analysis notebook (entry point)
├── README.md                # Human-readable project documentation
├── .gitignore               # Standard Python gitignore
├── AGENTS.md                # This file
└── resources/
    ├── btc.csv              # Primary dataset from CoinMetrics (~4,500 rows)
    ├── btc valuation model.xlsx  # Excel backup of analysis
    ├── historical data/     # Archive of older datasets
    ├── Fig1.png             # Upper & lower boundaries visualization
    ├── Fig2.png             # Actual vs fundamental NAV plot
    ├── NVT_formula.png      # NVT formula reference
    ├── metcalfe2.png        # Metcalfe's Law illustration
    ├── metcalfe_variations.png  # Formula variations
    ├── correlation.png      # Correlation calculation results
    └── *.png                # Additional formula/visualization assets
```

## Data Schema

The primary dataset (`resources/btc.csv`) contains 44 columns of daily Bitcoin metrics from CoinMetrics:

**Key columns used in analysis:**
- `date` - Date (YYYY-MM-DD format)
- `AdrActCnt` - Daily Active Address Count (primary input)
- `CapMrktCurUSD` - Current Market Cap in USD (target variable)

**Other notable columns:**
- `PriceUSD` - Daily price
- `TxCnt` - Transaction count
- `TxTfrValUSD` - Transfer value in USD
- `HashRate` - Network hash rate
- `NVTAdj` / `NVTAdj90` - NVT ratios

**Date range:** 2009-01-03 to 2021-04-06 (4,477 daily records)

## Running the Analysis

### Prerequisites

Install required packages:
```bash
pip install pandas numpy matplotlib jupyter
```

### Execution

1. Launch Jupyter Notebook:
   ```bash
   jupyter notebook model.ipynb
   ```

2. Run all cells sequentially (Cell > Run All)

3. Output plots are saved to `resources/Fig1.png` and `resources/Fig2.png`

## Model Methodology

### 1. Data Preprocessing
- Load CSV data from `resources/btc.csv`
- Extract relevant columns: Date, Active_Address_Count, Market_Cap
- Remove rows with NaN values
- Convert Date column to datetime
- Calculate 30-day Simple Moving Average (SMA) of Market Cap

### 2. Metcalfe Law Calculations
```python
# Upper boundary (Metcalfe's Law)
metcalfe_n = Active_Address_Count²
upperbound = a1 + b1 × ln(SMA_30(metcalfe_n))
# where a1 = 0, b1 = 1

# Lower boundary (Odlyzko's Law)
odlyzko_n = Active_Address_Count × ln(Active_Address_Count)
lowerbound = a2 + b2 × SMA_30(ln(SMA_30(odlyzko_n)))
# where a2 = -3.48, b2 = 1.65
```

### 3. Fundamental Value Calculation
```python
fundamental_NAV = (upperbound + lowerbound) / 2
```

### 4. Correlation Analysis
The model calculates Pearson correlation between actual Bitcoin NAV (log of market cap) and:
- Metcalfe's Law (NV ~ n²): ~0.9705
- Generalized Metcalfe (NV ~ n^1.5): ~0.9702
- Odlyzko's Law (NV ~ n×ln(n)): ~0.9692

## Code Organization

The notebook `model.ipynb` is organized as follows:

1. **Setup & Dependencies** - Import libraries, configure formatting
2. **Data Loading** - Load and inspect `btc.csv`
3. **Data Preprocessing** - Column selection, NaN handling, date formatting
4. **Feature Engineering** - Calculate 30-day SMA, log transforms
5. **Metcalfe's Law Implementation** - Upper boundary calculation
6. **Odlyzko's Law Implementation** - Lower boundary calculation
7. **Clearblocks Determination** - Generalized Metcalfe calculation
8. **Fundamental Value Calculation** - Combine upper/lower bounds
9. **Visualization** - Generate and save plots
10. **Correlation Analysis** - Statistical validation

## Key Constants

The following empirically-derived constants are used for curve fitting:

```python
a1 = 0       # Metcalfe intercept
b1 = 1       # Metcalfe slope
a2 = -3.48   # Odlyzko intercept  
b2 = 1.65    # Odlyzko slope
```

These constants were chosen to create the narrowest channel between upper and lower boundaries while still containing the actual network value.

## Output Artifacts

Running the notebook produces:

1. **Console Output:**
   - DataFrame info and previews
   - Correlation coefficients for all three law variations

2. **Saved Visualizations:**
   - `resources/Fig1.png` - BTC NAV with upper/lower bounds vs Daily Active Addresses
   - `resources/Fig2.png` - Actual NAV vs Fundamental NAV comparison

## Important Notes

- **Data Source:** CoinMetrics no longer supports free API access; data is loaded from CSV
- **On-chain Only:** The model uses only on-chain transactions; exchange trading activity is excluded
- **Empirical Fitting:** The boundary constants (a1, b1, a2, b2) were determined through manual testing to find the narrowest channel containing actual market cap
- **Jupyter Formatting:** The notebook uses custom pandas float formatting (`${:,.2f}`) which may affect numerical display

## Limitations

- No automated testing framework
- No requirements.txt or dependency management file
- Single monolithic notebook (not modularized)
- Data is static (last updated 2021-04-06)
- No CI/CD pipeline

## Future Enhancements (if needed)

- Convert notebook to modular Python scripts
- Add requirements.txt or pyproject.toml for dependency management
- Implement unit tests for calculation functions
- Add data pipeline for automated data updates
- Extend analysis to other cryptocurrencies
