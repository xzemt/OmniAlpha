import baostock as bs
import pandas as pd
import datetime
import os
from core.config import DATA_DIR

class BaostockProvider:
    def __init__(self):
        self.is_logged_in = False

    def login(self):
        if not self.is_logged_in:
            bs.login()
            self.is_logged_in = True

    def logout(self):
        if self.is_logged_in:
            bs.logout()
            self.is_logged_in = False

    def get_hs300_stocks(self, date):
        self.login()
        print(f"Fetching HS300 constituents for {date}...")
        rs = bs.query_hs300_stocks(date=date)
        hs300_stocks = []
        while (rs.error_code == '0') & rs.next():
            row = rs.get_row_data()
            hs300_stocks.append({'code': row[1], 'name': row[2]})
        return hs300_stocks

    def get_daily_bars(self, code, start_date, end_date):
        """
        Fetch daily bars. 
        TODO: Implement caching to DATA_DIR.
        """
        self.login()
        # Ensure dates are strings
        
        rs = bs.query_history_k_data_plus(code,
            "date,code,open,high,low,close,volume,amount,pctChg,peTTM,pbMRQ,turn,isST",
            start_date=start_date, end_date=end_date,
            frequency="d", adjustflag="3")
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
            
        if not data_list:
            return pd.DataFrame()

        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # Convert numeric columns
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pctChg', 'peTTM', 'pbMRQ', 'turn']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate VWAP if not present (approximate)
        if 'amount' in df.columns and 'volume' in df.columns:
             # Baostock volume is in shares, amount in Yuan.
             # Sometimes volume is 0.
             df['vwap'] = df.apply(lambda row: row['amount'] / row['volume'] if row['volume'] > 0 else row['close'], axis=1)
        
        return df

    def _query_quarterly_data(self, query_func, code, year, quarter):
        """
        Helper method to query quarterly financial data.
        """
        self.login()
        try:
            rs = query_func(code=code, year=year, quarter=quarter)
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return None
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            return df
        except Exception as e:
            print(f"Error querying quarterly data for {code} {year}Q{quarter}: {e}")
            return None

    def get_profit_data(self, code, year, quarter):
        """
        季频盈利能力: roeAvg, npMargin, gpMargin, netProfit, etc.
        """
        return self._query_quarterly_data(bs.query_profit_data, code, year, quarter)

    def get_operation_data(self, code, year, quarter):
        """
        季频营运能力: NRTurnRatio, invTurnRatio, etc.
        """
        return self._query_quarterly_data(bs.query_operation_data, code, year, quarter)

    def get_growth_data(self, code, year, quarter):
        """
        季频成长能力: YOYEquity, YOYAsset, YOYNI, etc.
        """
        return self._query_quarterly_data(bs.query_growth_data, code, year, quarter)

    def get_balance_data(self, code, year, quarter):
        """
        季频偿债能力: currentRatio, quickRatio, cashRatio, liabilityToAsset, etc.
        """
        return self._query_quarterly_data(bs.query_balance_data, code, year, quarter)

# Singleton
data_provider = BaostockProvider()
