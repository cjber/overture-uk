import ast
import json
from argparse import ArgumentParser
from pathlib import Path

import geopandas as gpd
import h3pandas  # noqa
import pandas as pd

parser = ArgumentParser()
parser.add_argument("--filename", type=str, required=True)

args = parser.parse_args()

filename = Path(args.filename)


def process_columns(df: gpd.GeoDataFrame, cols: list[str]) -> gpd.GeoDataFrame:
    for col in cols:
        df[col] = df[col].apply(
            lambda x: json.loads(x) if not isinstance(x, (float, type(None))) else x
        )

    names = pd.json_normalize(
        pd.json_normalize(df["names"]).map(lambda x: x[0])["common"]
    ).add_prefix("names_")

    categories = pd.json_normalize(df["categories"]).add_prefix("category_")

    addresses = pd.json_normalize(
        df["addresses"].map(lambda x: x[0] if not isinstance(x, float) else {}),
        meta_prefix=True,
    ).add_prefix("addresses_")

    sources = pd.json_normalize(
        df["sources"].map(lambda x: x[0] if not isinstance(x, float) else {})
    ).add_prefix("sources_")

    brand = pd.json_normalize(
        pd.json_normalize(df["brand"])["names.brand_names_common"].map(
            lambda x: x[0] if not isinstance(x, float) else {}
        )
    ).add_prefix("brand_name_")

    df = df.drop(cols, axis=1)
    df = pd.concat([df, names, categories, addresses, sources, brand], axis=1)

    df["lat"], df["lng"] = df.geometry.x, df.geometry.y

    for i in range(1, 10):
        df[f"h3_0{i}"] = df.h3.geo_to_h3(i).index
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
    places = gpd.read_file(f"./data/raw/{filename}.gpkg")

    places = process_columns(
        places, ["names", "categories", "addresses", "sources", "brand"]
    )
    places = add_list_cols(places, ["websites", "socials", "phones"])
    places.to_parquet(f"./data/processed/{filename}.parquet")
