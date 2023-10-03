import ast
import json

import geopandas as gpd
import pandas as pd


def process_columns(df: gpd.GeoDataFrame, cols: list[str]) -> gpd.GeoDataFrame:
    for col in cols:
        df[col] = df[col].apply(
            lambda x: json.loads(x) if not isinstance(x, (float, type(None))) else x
        )

    names = pd.json_normalize(
        pd.json_normalize(df["names"]).map(lambda x: x[0])["common"]
    ).add_prefix("names_")
    print("names done")

    categories = pd.json_normalize(df["categories"]).add_prefix("category_")
    print("category done")

    addresses = pd.json_normalize(
        df["addresses"].map(lambda x: x[0] if not isinstance(x, float) else {}),
        meta_prefix=True,
    ).add_prefix("addresses_")
    print("address done")

    sources = pd.json_normalize(
        df["sources"].map(lambda x: x[0] if not isinstance(x, float) else {})
    ).add_prefix("sources_")
    print("source done")

    brand = pd.json_normalize(
        pd.json_normalize(df["brand"])["names.brand_names_common"].map(
            lambda x: x[0] if not isinstance(x, float) else {}
        )
    ).add_prefix("brand_name_")
    print("brand done")

    df = df.drop(cols, axis=1)
    df = pd.concat([df, names, categories, addresses, sources, brand], axis=1)
    return df


def add_list_cols(df: gpd.GeoDataFrame, cols: list[str]) -> gpd.GeoDataFrame:
    for col in cols:
        df[col] = df[col].apply(
            lambda x: ast.literal_eval(x)
            if not isinstance(x, (float, type(None)))
            else []
        )
    return df


def remove_list_cols(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    list_cols = df.apply(lambda x: any(isinstance(i, list) for i in x))
    for col in list_cols[list_cols].index:
        df[col] = df[col].astype(str)
    return df


if __name__ == "__main__":
    uk_places = gpd.read_file("./data/uk_places.gpkg")

    uk_places = process_columns(
        uk_places, ["names", "categories", "addresses", "sources", "brand"]
    )
    uk_places = add_list_cols(uk_places, ["websites", "socials", "phones"])
    uk_places.to_parquet("./data/uk_places_cleaned.parquet")
    print("parquet done")

    uk_places = remove_list_cols(uk_places)
    uk_places.to_file("./data/uk_places_cleaned.gpkg", driver="GPKG")
    print("gpkg done")
