from abc import ABC, abstractmethod
from data.baostock_provider import data_provider
import datetime

# --- Base Class ---
class StockStrategy(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def check(self, code, data_df):
        pass

# --- Helper ---
def _get_report_period(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    month = dt.month
    year = dt.year
    if 1 <= month <= 4:
        return str(year - 1), "3"
    elif 5 <= month <= 8:
        return str(year), "1"
    elif 9 <= month <= 10:
        return str(year), "2"
    else:
        return str(year), "3"

# --- Technical Strategies ---

class MovingAverageStrategy(StockStrategy):
    @property
    def name(self):
        return "MA_Trend"

    @property
    def description(self):
        return "Moving Average Trend: Close > MA20 AND MA5 > MA20"

    def check(self, code, df):
        if df is None or len(df) < 20:
            return False, {}
        df = df.copy()
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        last_row = df.iloc[-1]
        condition_1 = last_row['close'] > last_row['MA20']
        condition_2 = last_row['MA5'] > last_row['MA20']
        if condition_1 and condition_2:
            return True, {
                'price': last_row['close'],
                'MA5': round(last_row['MA5'], 2),
                'MA20': round(last_row['MA20'], 2)
            }
        return False, {}

class VolumeRiseStrategy(StockStrategy):
    @property
    def name(self):
        return "Volume_Breakout"
    @property
    def description(self):
        return "Volume Breakout: Rise > 2% AND Volume > 1.5 * MA_VOL5"
    def check(self, code, df):
        if df is None or len(df) < 6:
            return False, {}
        df = df.copy()
        df['MA_VOL5'] = df['volume'].rolling(window=5).mean()
        last_row = df.iloc[-1]
        is_up = last_row['pctChg'] > 2.0
        is_volume_up = last_row['volume'] > (last_row['MA_VOL5'] * 1.5)
        if is_up and is_volume_up:
            return True, {
                'price': last_row['close'],
                'pctChg': last_row['pctChg'],
                'vol_ratio': round(last_row['volume'] / last_row['MA_VOL5'], 2)
            }
        return False, {}

class HighTurnoverStrategy(StockStrategy):
    @property
    def name(self):
        return "High_Turnover"
    @property
    def description(self):
        return "High Turnover: Turnover > 5% AND Not ST"
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
        last_row = df.iloc[-1]
        turn = last_row.get('turn', 0)
        is_st = last_row.get('isST', '0')
        if turn > 5 and str(is_st) != '1':
            return True, {
                'price': last_row['close'],
                'turn': round(turn, 2),
                'pctChg': round(last_row.get('pctChg', 0), 2)
            }
        return False, {}

# --- Fundamental Strategies ---

class LowPeStrategy(StockStrategy):
    @property
    def name(self):
        return "Value_LowPE"
    @property
    def description(self):
        return "Low Valuation: 0 < PE_TTM < 30"
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
        last_row = df.iloc[-1]
        if 'peTTM' not in last_row:
            return False, {}
        pe = last_row['peTTM']
        if 0 < pe < 30:
            return True, {
                'price': last_row['close'],
                'peTTM': round(pe, 2),
                'pbMRQ': round(last_row.get('pbMRQ', 0), 2)
            }
        return False, {}

class HighGrowthStrategy(StockStrategy):
    @property
    def name(self):
        return "Growth_DoubleHigh"
    @property
    def description(self):
        return "High Growth: YOY Profit > 20% AND YOY Revenue > 20%"
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
        date_str = str(df.iloc[-1]['date'])
        year, quarter = _get_report_period(date_str)
        g_df = data_provider.get_growth_data(code, year, quarter)
        if g_df is None or g_df.empty:
            return False, {}
        try:
            yoy_ni = float(g_df.iloc[0]['YOYNI'])
            if yoy_ni > 20:
                return True, {
                    'price': df.iloc[-1]['close'],
                    'YOY_NetProfit': f"{yoy_ni:.2f}%",
                    'Period': f"{year}Q{quarter}"
                }
        except Exception:
            pass
        return False, {}

class HighRoeStrategy(StockStrategy):
    @property
    def name(self):
        return "Quality_HighROE"
    @property
    def description(self):
        return "High Quality: ROE > 15%"
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
        date_str = str(df.iloc[-1]['date'])
        year, quarter = _get_report_period(date_str)
        p_df = data_provider.get_profit_data(code, year, quarter)
        if p_df is None or p_df.empty:
            return False, {}
        try:
            roe = float(p_df.iloc[0]['roeAvg'])
            real_roe = roe * 100 if roe < 1.0 else roe
            if real_roe > 15:
                return True, {
                    'price': df.iloc[-1]['close'],
                    'ROE': f"{real_roe:.2f}%",
                    'Period': f"{year}Q{quarter}"
                }
        except:
            pass
        return False, {}

class LowDebtStrategy(StockStrategy):
    @property
    def name(self):
        return "Safety_LowDebt"
    @property
    def description(self):
        return "Financial Health: Debt Ratio < 50%"
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
        date_str = str(df.iloc[-1]['date'])
        year, quarter = _get_report_period(date_str)
        b_df = data_provider.get_balance_data(code, year, quarter)
        if b_df is None or b_df.empty:
            return False, {}
        try:
            liab_ratio = float(b_df.iloc[0]['liabilityToAsset']) * 100
            if liab_ratio < 50:
                 return True, {
                    'price': df.iloc[-1]['close'],
                    'DebtRatio': f"{liab_ratio:.2f}%",
                    'Period': f"{year}Q{quarter}"
                }
        except:
            pass
        return False, {}

# --- Registry ---
STRATEGY_REGISTRY = {
    'ma': MovingAverageStrategy,
    'vol': VolumeRiseStrategy,
    'turn': HighTurnoverStrategy,
    'pe': LowPeStrategy,
    'growth': HighGrowthStrategy,
    'roe': HighRoeStrategy,
    'debt': LowDebtStrategy
}

def get_strategy(key):
    strategy_cls = STRATEGY_REGISTRY.get(key)
    if strategy_cls:
        return strategy_cls()
    return None

def get_all_strategy_keys():
    return list(STRATEGY_REGISTRY.keys())
