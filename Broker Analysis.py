import pandas as pd
import matplotlib.pyplot as plt


# Simulation de données de trading (Input type Aladdin/OMS)
trades = [
    {"Product": "LVMH", "Broker": "BNP", "Qty": 5000, "Exec_Price": 596.70, "Arrival_Price": 593.50},
    {"Product": "E-Mini S&P 500 Mar 26", "Broker": "JPM", "Qty": 2000, "Exec_Price": 6949.50, "Arrival_Price": 6945.00},
    {"Product": "EUR/USD", "Broker": "MS", "Qty": 10000, "Exec_Price": 1.175, "Arrival_Price": 1.180},
]

# Fontions

def generate_post_trade_report(data):
    df = pd.DataFrame(data)

    # Calcul du Slippage en Points de Base (bps)
    # Formule : ((Prix Exec - Prix Arrivée) / Prix Arrivée) * 10000
    df['Slippage_bps'] = ((df['Exec_Price'] - df['Arrival_Price']) / df['Arrival_Price']) * 10000

    # Calcul du coût total par ligne (Notionnel)
    df['Notional_EUR'] = df['Qty'] * df['Exec_Price']

    # Slippage moyen pondéré par le montant traité
    weighted_avg_slippage = (df['Slippage_bps'] * df['Notional_EUR']).sum() / df['Notional_EUR'].sum()

    # Identifier les exécutions dépassant 10 bps de coût
    outliers = df[df['Slippage_bps'] > 10]

    # Print les resultats

    print(df)
    print("--- DAILY POST-TRADE ANALYSIS ---")
    print(f"Total Value Traded: {df['Notional_EUR'].sum():,.2f} EUR")
    print(f"Weighted Average Slippage: {weighted_avg_slippage:.2f} bps")
    print(f"Flagged Transactions: {len(outliers)} execution(s) above 10bps limit.")

    return df


def generate_visual_report(data):
    df = pd.DataFrame(data)

    # 2. Création du graphique
    plt.figure(figsize=(10, 6))
    colors = ['red' if x > 10 else 'teal' for x in df['Slippage_bps']]

    bars = plt.bar(df['Broker'] + " - " + df['Product'], df['Slippage_bps'], color=colors)

    # Ajout d'une ligne de référence à 0 bps
    plt.axhline(0, color='black', linewidth=0.8)
    # Ajout d'une ligne d'alerte à 10 bps
    plt.axhline(10, color='red', linestyle='--', label='Seuil d\'alerte (10bps)')

    # 3.
    plt.title('Analyse de la Performance par Broker (Slippage en bps)', fontsize=14)
    plt.ylabel('Slippage (Points de base)')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Sauvegarde automatique du graphique
    plt.savefig('daily_broker_performance.png')
    plt.show()

# Exécution du rapport
report = generate_post_trade_report(trades)
generate_visual_report(report)