import pandas as pd
import re

AGG_ALIASES = {
    "paybis": ["paybis", "paybis.com", "paybis ltd"],
    "guardarian": ["guardarian", "guardarian.com"],
    "mt pelerin": ["mt pelerin", "mtpelerin"],
    "banxa": ["banxa"],
    "changelly": ["changelly"],
    # ... остальные
}

COUNTRY_FALLBACK = {
    "poland": ["europe", "eu", "world"],
    "latvia": ["europe", "eu", "world"],
    "kazakhstan": ["cis", "world"],
    "belarus": ["cis", "world"],
    "ukraine": ["cis", "world"],
    # ... остальные
}

def aggregator_match(name, search):
    name, search = name.lower(), search.lower()
    for agg, aliases in AGG_ALIASES.items():
        if (name in aliases and search in aliases) or (agg in [name, search]):
            return True
    return name == search or name.replace('.com', '') == search.replace('.com', '')

def is_blocked(row):
    bug = str(row.get("Bug", "")).lower()
    blocked = str(row.get("Blocked", "")).lower()
    status = str(row.get("Status", "")).lower()
    return "bug" in bug or "block" in blocked or "api error" in status or "not working" in status

class AggregatorSelector:
    def __init__(self, tbl2, tbl3_500, tbl3_2000, tbl3_10000, tbl1):
        self.tbl2 = tbl2
        self.tbl3 = {500: tbl3_500, 2000: tbl3_2000, 10000: tbl3_10000}
        self.tbl1 = tbl1

    def _get_tier(self, amount):
        if amount <= 500: return 500
        elif amount <= 2000: return 2000
        else: return 10000

    def region_fallback(self, country):
        variants = [country.lower()]
        variants += COUNTRY_FALLBACK.get(country.lower(), [])
        return variants

    def select_top(self, country, method, amount, kyc_wanted: bool = True):
        tier = self._get_tier(amount)
        df = self.tbl3[tier]
        result = []
        regions = self.region_fallback(country)
        for reg in regions:
            row = df[(df["Country"].str.lower() == reg) & (df["Method"].str.lower() == method.lower())]
            if not row.empty:
                aggs = [row.iloc[0][col] for col in ["Top 1", "Top 2", "Top 3"] if pd.notna(row.iloc[0][col])]
                for agg in aggs:
                    if self.check_limits(agg, amount) and self.check_kyc(agg, kyc_wanted):
                        result.append(agg)
                if result:
                    return result
        # Fallback: любые методы по "world"
        for alt_method in ["card", "sepa", "bank", "apple pay"]:
            alt = df[(df["Country"].str.lower() == "world") & (df["Method"].str.lower() == alt_method)]
            if not alt.empty:
                aggs = [alt.iloc[0][col] for col in ["Top 1", "Top 2", "Top 3"] if pd.notna(alt.iloc[0][col])]
                for agg in aggs:
                    if self.check_limits(agg, amount) and self.check_kyc(agg, kyc_wanted):
                        result.append(agg)
                if result:
                    return result
        return []

    def check_limits(self, aggregator, amount):
        row = self.tbl1[self.tbl1["Aggregator"].apply(lambda x: aggregator_match(x, aggregator))]
        if row.empty or is_blocked(row.iloc[0]):
            return False
        minmax = row.iloc[0].get("Min/Max", None)
        if not isinstance(minmax, str): return True
        match = re.match(r"[≈~]?([\d,]+)\/([\d,]+)", minmax.replace(" ", ""))
        if not match: return True
        min_val, max_val = float(match.group(1).replace(',', '')), float(match.group(2).replace(',', ''))
        return min_val <= amount <= max_val

    def check_kyc(self, aggregator, kyc_wanted: bool):
        row = self.tbl1[self.tbl1["Aggregator"].apply(lambda x: aggregator_match(x, aggregator))]
        if row.empty: return True
        kyc_val = row.iloc[0].get("KYC", "") or row.iloc[0].get("KYC Needed", "")
        kyc_bool = "no" not in str(kyc_val).lower() and "0" not in str(kyc_val)
        return kyc_bool if kyc_wanted else not kyc_bool
