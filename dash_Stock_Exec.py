import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf


def generate_real_data_report(ticker_symbol):
    # 1. Récupération des données réelles sur 1 jour (intervalle 5min)
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="1d", interval="5m")

    if df.empty:
        print("Erreur : Impossible de récupérer les données.")
        return

    # 2. Simulation de nos exécutions (basée sur les prix réels)
    # On simule qu'on a exécuté 10% du volume de chaque intervalle
    df['Our_Exec_Price'] = df['Close'] * (1 + np.random.normal(0, 0.0002, len(df)))
    df['Our_Volume'] = (df['Volume'] * 0.1).astype(int)
    df['Cum_Volume'] = df['Our_Volume'].cumsum()

    # 3. Configuration du Dashboard
    fig = plt.figure(figsize=(15, 10))
    grid = plt.GridSpec(2, 2, height_ratios=[1.5, 1])

    # --- GRAPHIQUE 1 : PRIX RÉELS VS EXÉCUTION ---
    ax1 = fig.add_subplot(grid[0, :])
    ax1.plot(df.index, df['Close'], color='navy', label=f'Market Price ({ticker_symbol})', alpha=0.7)
    ax1.scatter(df.index, df['Our_Exec_Price'], color='orange', s=20, label='Our Trades', zorder=5)
    ax1.set_title(f"Intraday Execution Tracking: {ticker_symbol}", fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.2)

    # --- GRAPHIQUE 2 : ANALYSE DU VOLUME (REAL DATA) ---
    ax2 = fig.add_subplot(grid[1, 0])
    ax2.bar(df.index, df['Volume'], color='gray', alpha=0.3, width=0.002, label='Market Vol')
    ax2_twin = ax2.twinx()
    ax2_twin.plot(df.index, df['Cum_Volume'], color='darkgreen', label='Our Cumul. Vol')
    ax2.set_title("Market Liquidity vs Our Participation")
    ax2.legend(loc='upper left')

    # --- GRAPHIQUE 3 : DISTRIBUTION DU SLIPPAGE ---
    ax3 = fig.add_subplot(grid[1, 1])
    slippage = (df['Our_Exec_Price'] - df['Open']) / df['Open'] * 10000
    ax3.hist(slippage, bins=15, color='teal', edgecolor='black', alpha=0.7)
    ax3.axvline(0, color='red', linestyle='--')
    ax3.set_title("Slippage Distribution (bps)")
    ax3.set_xlabel("Basis Points (bps)")

    plt.tight_layout()
    plt.savefig('LVMH_execution_analysis.png')
    plt.show()


# Test avec LVMH
generate_real_data_report("MC.PA")

print(df)