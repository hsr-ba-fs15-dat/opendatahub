"""

"""

import pandas as pd


class DataFrameUtils(object):
    @staticmethod
    def make_serializable(df):
        """
        :return: DataFrame which contains only exportable data (no objects)
        """
        df = pd.DataFrame(df.copy(True))
        for col in df.columns:
            temp = df[col].dropna()
            if len(temp) and temp.dtype == object and not isinstance(temp.iloc[0], unicode):
                try:
                    df[col] = df[col].astype(unicode)
                except:
                    pass

        return df
