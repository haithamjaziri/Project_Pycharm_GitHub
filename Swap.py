import QuantLib as ql
import pandas_datareader.data as web
from datetime import datetime, timedelta

def get_market_data():
    print("Récupération des données FRED")
    # Tickers FRED pour SOFR et les taux Treasury (proxies pour la courbe)
    tickers = {
        "ON": "SOFR",  # SOFR Overnight
        "1Y": "DGS1",  # 1 Year Treasury
        "2Y": "DGS2",  # 2 Year Treasury
        "5Y": "DGS5",  # 5 Year Treasury
        "10Y": "DGS10",  # 10 Year Treasury
        "30Y": "DGS30"  # 30 Year Treasury
    }

    data = {}
    for label, ticker in tickers.items():
        try:
            # On prend la dernière valeur disponible
            df = web.DataReader(ticker, 'fred', datetime.now() - timedelta(days=5))
            rate = df.iloc[-1].values[0]
            data[label] = rate / 100.0
            print(f"[{label}] : {rate:.4f}%")
        except Exception as e:
            print(f"Erreur pour {label}: {e}")
    return data


def calculate_fair_rates():
    market_rates = get_market_data()

    # 1. Setup QuantLib
    today = ql.Date(15, 2, 2026)  # Date d'aujourd'hui
    ql.Settings.instance().evaluationDate = today
    calendar = ql.UnitedStates(ql.UnitedStates.Settlement)

    # 2. Construction de la Courbe SOFR
    sofr_index = ql.Sofr()
    helpers = []
    helpers.append(ql.DepositRateHelper(market_rates["ON"], ql.Period(1, ql.Days), 0, calendar, ql.Following, False,
                                        ql.Actual360()))

    for tenor in ["1Y", "2Y", "5Y", "10Y", "30Y"]:
        period = ql.Period(tenor)
        helpers.append(ql.OISRateHelper(2, period, ql.QuoteHandle(ql.SimpleQuote(market_rates[tenor])), sofr_index))

    yield_curve = ql.PiecewiseLogLinearDiscount(0, calendar, helpers, ql.Actual360())
    curve_handle = ql.YieldTermStructureHandle(yield_curve)

    # 3. Calcul du Fair Rate pour différentes maturités
    print(f"\n--- SWAP QUOTES (USD SOFR) - {today} ---")
    print(f"{'Maturité':<10} | {'Fair Rate (%)':<15}")
    print("-" * 30)

    test_maturities = ["2Y", "3Y", "5Y", "7Y", "10Y", "15Y", "20Y", "30Y"]

    for m in test_maturities:
        period = ql.Period(m)
        start_date = calendar.advance(today, 2, ql.Days)
        end_date = calendar.advance(start_date, period)

        # On crée un swap fictif avec un taux fixe à 0% juste pour extraire le Fair Rate
        schedule = ql.Schedule(start_date, end_date, ql.Period(ql.Annual), calendar,
                               ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)

        temp_swap = ql.VanillaSwap(ql.VanillaSwap.Payer, 1.0, schedule, 0.0, ql.Actual360(),
                                   schedule, ql.Sofr(curve_handle), 0.0, ql.Actual360())

        temp_swap.setPricingEngine(ql.DiscountingSwapEngine(curve_handle))

        # LA MÉTHODE CLÉ : fairRate()
        fair_rate = temp_swap.fairRate()
        print(f"{m:<10} | {fair_rate:.4%}")


if __name__ == "__main__":
    calculate_fair_rates()