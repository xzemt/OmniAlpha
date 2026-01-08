from data.baostock_provider import data_provider
from backtest.engine import BacktestEngine
from alpha.factors.gtja191 import GTJA191
from core.config import PROJECT_ROOT

def main():
    print(f"BlackOil-OmniAlpha System Initialized at {PROJECT_ROOT}")
    
    # 1. Data Test
    # stocks = data_provider.get_hs300_stocks('2023-01-01')
    # print(f"Loaded {len(stocks)} stocks from HS300.")
    
    # 2. Factor Calculation Example
    # df = data_provider.get_daily_bars('sh.600000', '2023-01-01', '2023-06-01')
    # if not df.empty:
    #     alphas = GTJA191(df)
    #     factor_val = alphas.alpha001()
    #     print("Alpha 001 Sample:", factor_val.tail())
        
    # 3. Backtest Example
    engine = BacktestEngine(start_date='2023-01-01', end_date='2023-06-01')
    engine.run(strategy=None, stock_pool=['sh.600000'])

if __name__ == "__main__":
    main()