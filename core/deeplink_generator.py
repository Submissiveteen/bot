import pandas as pd
from urllib.parse import urlencode


class DeeplinkGenerator:
    def __init__(self, table_4):
        self.table_4 = table_4

    def get_query_map(self, aggregator):
        df = self.table_4[
            self.table_4["aggregator"].str.contains(
                aggregator.split(".")[0], case=False
            )
        ]
        return {
            row["feature"]: row["parameter"]
            for _, row in df.iterrows()
            if pd.notna(row["parameter"])
        }

    def get_required(self, aggregator):
        df = self.table_4[
            self.table_4["aggregator"].str.contains(
                aggregator.split(".")[0], case=False
            )
        ]
        return df[df["IsRequired"] == 1]["feature"].tolist()

    def flatten_query(self, params, prefix=""):
        out = {}
        for k, v in params.items():
            if isinstance(v, dict):
                for kk, vv in self.flatten_query(v, prefix=f"{prefix}{k}.").items():
                    out[kk] = vv
            else:
                out[f"{prefix}{k}"] = v
        return out

    def generate(self, aggregator, base_url, params_dict):
        query_map = self.get_query_map(aggregator)
        required = self.get_required(aggregator)
        missing = [
            field
            for field in required
            if field not in params_dict or params_dict[field] is None
        ]
        if missing:
            raise ValueError(f"Missing required fields for {aggregator}: {missing}")
        query = {
            query_map.get(k, k): v
            for k, v in params_dict.items()
            if k in query_map and v is not None
        }
        # Поддержка вложенных полей (например, details.wallet)
        flat_query = self.flatten_query(query)
        url = base_url + "?" + urlencode(flat_query)
        return url
