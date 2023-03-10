import datetime
import math
import pickle

import inflection
import numpy as np
import pandas as pd


class Rossmann(object):
    def __init__(self):
        self.competition_time_month_scaler = pickle.load(
            open("../src/features/competition_time_month_scaler.pkl", "rb")
        )
        self.competition_distance_scaler = pickle.load(
            open("../src/features/competition_distance_scaler.pkl", "rb")
        )
        self.promo_time_week_scaler = pickle.load(
            open("../src/features/promo_time_week_scaler.pkl", "rb")
        )
        self.store_type_scaler = pickle.load(
            open("../src/features/store_type_scaler.pkl", "rb")
        )
        self.year_scaler = pickle.load(open("../src/features/year_scaler.pkl", "rb"))

    def data_clean(self, df):

        ## 1.2. Rename Columns
        # Nome das colunas
        cols_old = [
            "Store",
            "DayOfWeek",
            "Date",
            "Open",
            "Promo",
            "StateHoliday",
            "SchoolHoliday",
            "StoreType",
            "Assortment",
            "CompetitionDistance",
            "CompetitionOpenSinceMonth",
            "CompetitionOpenSinceYear",
            "Promo2",
            "Promo2SinceWeek",
            "Promo2SinceYear",
            "PromoInterval",
        ]

        # Alteração do nome das colunas
        snakecase = lambda x: inflection.underscore(x)
        cols_new = list(map(snakecase, cols_old))

        # Renomeia as colunas do DF
        df.columns = cols_new

        ## 1.4. Data Types
        df["date"] = pd.to_datetime(df["date"])

        ## 1.6. Fillout NA
        ### 1.6.1. competition_distance
        df["competition_distance"].max()
        df["competition_distance"] = df["competition_distance"].apply(
            lambda x: 200000.0 if math.isnan(x) else x
        )

        ### 1.6.2. competition_open_since_month
        df["competition_open_since_month"] = df.apply(
            lambda x: x["date"].month
            if math.isnan(x["competition_open_since_month"])
            else x["competition_open_since_month"],
            axis=1,
        )

        ### 1.6.3. competition_open_since_year
        df["competition_open_since_year"] = df.apply(
            lambda x: x["date"].year
            if math.isnan(x["competition_open_since_year"])
            else x["competition_open_since_year"],
            axis=1,
        )

        ### 1.6.4. promo2_since_week
        df["promo2_since_week"] = df.apply(
            lambda x: x["date"].week
            if math.isnan(x["promo2_since_week"])
            else x["promo2_since_week"],
            axis=1,
        )

        ### 1.6.5. promo2_since_year
        df["promo2_since_year"] = df.apply(
            lambda x: x["date"].year
            if math.isnan(x["promo2_since_year"])
            else x["promo2_since_year"],
            axis=1,
        )

        ### 1.6.6. promo_interval
        month_map = {
            1: "Jan",
            2: "Fev",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }

        df["promo_interval"].fillna(0, inplace=True)
        df["month_map"] = df["date"].dt.month.map(month_map)
        df["is_promo"] = df[["promo_interval", "month_map"]].apply(
            lambda x: 0
            if x["promo_interval"] == 0
            else 1
            if x["month_map"] in x["promo_interval"].split(",")
            else 0,
            axis=1,
        )

        ## 1.7. Change Types
        df["competition_open_since_month"] = df["competition_open_since_month"].astype(
            int
        )
        df["competition_open_since_year"] = df["competition_open_since_year"].astype(
            int
        )

        df["promo2_since_week"] = df["promo2_since_week"].astype(int)
        df["promo2_since_year"] = df["promo2_since_year"].astype(int)

        return df

    def feature_engeneering(self, df):

        # year
        df["year"] = df["date"].dt.year

        # month
        df["month"] = df["date"].dt.month

        # day
        df["day"] = df["date"].dt.day

        # week of year
        df["week_of_year"] = df["date"].dt.weekofyear

        # year week
        df["year_week"] = df["date"].dt.strftime("%Y-%W")

        # competition since
        df["competition_since"] = df.apply(
            lambda x: datetime.datetime(
                year=x["competition_open_since_year"],
                month=x["competition_open_since_month"],
                day=1,
            ),
            axis=1,
        )
        df["competition_time_month"] = (
            ((df["date"] - df["competition_since"]) / 30)
            .apply(lambda x: x.days)
            .astype(int)
        )

        # promo since
        df["promo_since"] = (
            df["promo2_since_year"].astype(str)
            + "-"
            + df["promo2_since_week"].astype(str)
        )
        df["promo_since"] = df["promo_since"].apply(
            lambda x: datetime.datetime.strptime(x + "-1", "%Y-%W-%w")
            - datetime.timedelta(days=7)
        )
        df["promo_time_week"] = (
            ((df["date"] - df["promo_since"]) / 7).apply(lambda x: x.days).astype(int)
        )

        # assortment
        df["assortment"] = df["assortment"].apply(
            lambda x: "basic" if x == "a" else "extra" if x == "b" else "extended"
        )

        # state holiday
        df["state_holiday"] = df["state_holiday"].apply(
            lambda x: "public_holiday"
            if x == "a"
            else "easter_holiday"
            if x == "b"
            else "christmas"
            if x == "c"
            else "regular_day"
        )

        # 3.0. FILTERING FEATURES
        ## 3.1. Filtering Lines
        df = df[(df["open"] != 0)]

        ## 3.2. Columns Selection
        cols_drop = ["open", "promo_interval", "month_map"]
        df.drop(cols_drop, axis=1, inplace=True)

        return df

    def data_preparation(self, df):
        ## 5.2. Rescaling
        # competition_distance
        df["competition_distance"] = self.competition_distance_scaler.transform(
            df[["competition_distance"]].values
        )

        # competition_time_month
        df["competition_time_month"] = self.competition_distance_scaler.transform(
            df[["competition_time_month"]].values
        )

        # promo_time_week
        df["promo_time_week"] = self.promo_time_week_scaler.transform(
            df[["promo_time_week"]].values
        )

        # year
        df["year"] = self.year_scaler.transform(df[["year"]].values)

        ## 5.3. Transformation
        # state_holiday - One Hot Encoding
        df = pd.get_dummies(df, prefix=["state_holiday"], columns=["state_holiday"])

        # store_type - Label Encoding
        df["store_type"] = self.store_type_scaler.transform(df["store_type"])

        # assortment - Ordinal Encoding
        assortment_dict = {"basic": 1, "extra": 2, "extended": 3}
        df["assortment"] = df["assortment"].map(assortment_dict)

        ### 5.3.3. Nature Transformation
        # month - Ciclo de 12 Meses
        df["month_sin"] = df["month"].apply(lambda x: np.sin(x * (2.0 * np.pi / 12)))
        df["month_cos"] = df["month"].apply(lambda x: np.cos(x * (2.0 * np.pi / 12)))

        # day - Ciclo de 30 Dias
        df["day_sin"] = df["day"].apply(lambda x: np.sin(x * (2.0 * np.pi / 30)))
        df["day_cos"] = df["day"].apply(lambda x: np.cos(x * (2.0 * np.pi / 30)))

        # week_of_year - Ciclo de 52 semanas
        df["week_of_year_sin"] = df["week_of_year"].apply(
            lambda x: np.sin(x * (2.0 * np.pi / 52))
        )
        df["week_of_year_cos"] = df["week_of_year"].apply(
            lambda x: np.cos(x * (2.0 * np.pi / 52))
        )

        # day_of_week - Ciclo de 7 dias
        df["day_of_week_sin"] = df["day_of_week"].apply(
            lambda x: np.sin(x * (2.0 * np.pi / 7))
        )
        df["day_of_week_cos"] = df["day_of_week"].apply(
            lambda x: np.cos(x * (2.0 * np.pi / 7))
        )

        cols_selected = [
            "store",
            "promo",
            "store_type",
            "assortment",
            "competition_distance",
            "competition_open_since_month",
            "competition_open_since_year",
            "promo2",
            "promo2_since_week",
            "promo2_since_year",
            "competition_time_month",
            "promo_time_week",
            "month_sin",
            "month_cos",
            "day_sin",
            "day_cos",
            "week_of_year_sin",
            "week_of_year_cos",
            "day_of_week_sin",
            "day_of_week_cos",
        ]

        return df[cols_selected]

    def get_prediction(self, model, original_data, test_data):
        # prediction
        pred = model.predict(test_data)

        # join pred into original_data
        original_data["predictions"] = np.expm1(pred)

        return original_data.to_json(orient="records", date_format="iso")
