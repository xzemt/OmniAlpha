from data.baostock_provider import data_provider
import datetime

class AnalysisEngine:
    def __init__(self, strategies):
        self.strategies = strategies

    def scan_one(self, code, date_str):
        # Calculate start_date for fetching data (e.g. 100 days back)
        end_date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        start_date_obj = end_date_obj - datetime.timedelta(days=150) # Enough for MA60 etc.
        start_date_str = start_date_obj.strftime("%Y-%m-%d")
        
        try:
            # We use the existing signature of get_daily_bars(code, start_date, end_date)
            # If data_provider is updated to support lookback_days, we might need to adjust,
            # but using start/end is safer if we control the calculation.
            df = data_provider.get_daily_bars(code, start_date_str, date_str)
        except Exception as e:
            print(f"Error fetching data for {code}: {e}")
            return None
            
        if df is None or df.empty:
            return None
            
        combined_details = {}
        all_match = True
        
        for strategy in self.strategies:
            is_match, details = strategy.check(code, df)
            if not is_match:
                all_match = False
                break
            combined_details.update(details)
            
        if all_match:
            res = {
                'code': code,
                'strategy': "+".join([s.name for s in self.strategies]),
                'date': date_str
            }
            res.update(combined_details)
            return res
            
        return None
