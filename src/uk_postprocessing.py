from argparse import ArgumentParser
from pathlib import Path

import geopandas as gpd
import h3pandas  # noqa
import pandas as pd

parser = ArgumentParser()
parser.add_argument("--filename", type=str, required=True)

args = parser.parse_args()

filename = Path(args.filename)


def add_uk_attributes(df, oa, oa_lookup, sdz, nidz, lad):
    df = df.to_crs("EPSG:27700")
    df["easting"], df["northing"] = df.geometry.x, df.geometry.y

    df = df.sjoin(lad).drop(columns=["index_right"])
    df = gpd.sjoin(df, oa, how="left").drop(columns=["index_right"])
    df = df.merge(oa_lookup, on="OA21CD", how="left")

    df = gpd.sjoin(df, sdz, how="left").drop(columns=["index_right"])
    df = gpd.sjoin(df, nidz, how="left").drop(columns=["index_right"])

    return df


def remove_list_cols(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    list_cols = df.apply(lambda x: any(isinstance(i, list) for i in x))
    for col in list_cols[list_cols].index:
        df[col] = df[col].astype(str)
    return df


if __name__ == "__main__":
    places = gpd.read_parquet(f"./data/processed/{filename}.parquet")
    oa = gpd.read_file("~/data/OA_2021_BGC.gpkg")[["OA21CD", "geometry"]]
    oa_lookup = pd.read_csv("~/data/OA_lookup-2021.csv").drop(
        columns=["ObjectId", "LAD22CD", "LAD22NM"]
    )
    sdz = gpd.read_file("~/data/SG_DataZoneBdry_2011.zip")[
        ["DataZone", "Name", "geometry"]
    ].rename(columns={"DataZone": "DZ11CD", "Name": "DZ11NM"})
    nidz = (
        gpd.read_file("~/data/NI_DZ21.zip")
        .drop(columns=["Area_ha", "Perim_km"])
        .to_crs("EPSG: 27700")
    )
    lad = gpd.read_file("~/data/LAD_BUC_2022.gpkg")[["LAD22CD", "LAD22NM", "geometry"]]

    places = add_uk_attributes(places, oa, oa_lookup, sdz, nidz, lad)
    places = places.drop(
        columns=[
            "geometry",
            "names_language",
            "source_property",
            "sources_recordid",
            "brand_name_language",
            "LEP21CD1",
            "LEP21NM1",
            "LEP21CD2",
            "LEP21NM2",
        ]
    )
    places.to_parquet(f"./data/processed/{filename}_admin.parquet")
