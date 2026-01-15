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

    def get_zz1000_stocks(self, date):
        """获取中证1000成分股"""
        self.login()
        print(f"Fetching ZZ1000 constituents for {date}...")
        rs = bs.query_zz500_stocks(date=date)  # baostock 暂无 zz1000 接口，使用 zz500 + 扩展
        # 注意：baostock 目前支持 hs300, zz500, sz50
        # 这里使用 query_stock_industry 获取更多股票作为替代方案
        zz1000_stocks = []
        # 先获取中证500作为基础
        rs = bs.query_zz500_stocks(date=date)
        while (rs.error_code == '0') & rs.next():
            row = rs.get_row_data()
            zz1000_stocks.append({'code': row[1], 'name': row[2]})
        # 如果需要更多股票，可以从沪深300补充
        if len(zz1000_stocks) < 500:
            hs300 = self.get_hs300_stocks(date)
            existing_codes = {s['code'] for s in zz1000_stocks}
            for stock in hs300:
                if stock['code'] not in existing_codes:
                    zz1000_stocks.append(stock)
                if len(zz1000_stocks) >= 1000:
                    break
        return zz1000_stocks[:1000]

    def get_daily_bars(self, code, start_date, end_date):
        """
        获取日线数据。
        优先读取本地缓存 (DATA_DIR/daily/{code}.csv)，若数据缺失则增量下载。
        """
        # 0. 准备路径和文件夹
        daily_dir = os.path.join(DATA_DIR, "daily")
        os.makedirs(daily_dir, exist_ok=True)
        file_path = os.path.join(daily_dir, f"{code}.csv")
        
        df_cache = pd.DataFrame()
        
        # 1. 尝试读取缓存
        if os.path.exists(file_path):
            try:
                df_cache = pd.read_csv(file_path, dtype={'code': str})
                if 'date' in df_cache.columns:
                    df_cache['date'] = df_cache['date'].astype(str)
                    df_cache = df_cache.sort_values('date')
            except Exception as e:
                print(f"[Warn] Error reading cache for {code}: {e}")
                df_cache = pd.DataFrame()

        # 2. 确定下载范围
        fetch_start = start_date
        fetch_end = end_date
        need_download = True
        
        if not df_cache.empty:
            cache_start = df_cache['date'].min()
            cache_end = df_cache['date'].max()
            
            # 如果请求的开始时间早于缓存，这里简单处理：重新下载全部（保证数据连续性）
            if start_date < cache_start:
                need_download = True
                fetch_start = start_date 
            elif end_date <= cache_end:
                 # 请求范围完全在缓存内
                 need_download = False
            else:
                 # 只要下载尾部增量
                 try:
                     last_dt = datetime.datetime.strptime(cache_end, "%Y-%m-%d")
                     next_dt = last_dt + datetime.timedelta(days=1)
                     fetch_start = next_dt.strftime("%Y-%m-%d")
                     if fetch_start > fetch_end:
                         need_download = False
                 except:
                     fetch_start = start_date
        
        # 3. 下载数据 (如果需要)
        if need_download:
            self.login()
            # print(f"Downloading {code} from {fetch_start} to {fetch_end}...")
            
            rs = bs.query_history_k_data_plus(code,
                "date,code,open,high,low,close,volume,amount,pctChg,peTTM,pbMRQ,turn,isST",
                start_date=fetch_start, end_date=fetch_end,
                frequency="d", adjustflag="3")
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if data_list:
                df_new = pd.DataFrame(data_list, columns=rs.fields)
                
                # 转换数值列
                numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pctChg', 'peTTM', 'pbMRQ', 'turn']
                for col in numeric_cols:
                    if col in df_new.columns:
                        df_new[col] = pd.to_numeric(df_new[col], errors='coerce')
                
                # 计算 VWAP
                if 'amount' in df_new.columns and 'volume' in df_new.columns:
                     df_new['vwap'] = df_new.apply(lambda row: row['amount'] / row['volume'] if row['volume'] > 0 else row['close'], axis=1)

                # 合并缓存
                if not df_cache.empty:
                    df_final = pd.concat([df_cache, df_new], ignore_index=True)
                    df_final.drop_duplicates(subset=['date'], inplace=True, keep='last')
                    df_final.sort_values('date', inplace=True)
                else:
                    df_final = df_new
                
                # 保存回 CSV
                df_final.to_csv(file_path, index=False)
                df_cache = df_final
            else:
                pass # 没有新数据下载
                
        # 4. 返回过滤后的数据
        if df_cache.empty:
            return pd.DataFrame()
            
        mask = (df_cache['date'] >= start_date) & (df_cache['date'] <= end_date)
        return df_cache.loc[mask].copy().reset_index(drop=True)

    def _query_quarterly_data(self, query_func, code, year, quarter):
        """
        查询季度财务数据的辅助方法。
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
