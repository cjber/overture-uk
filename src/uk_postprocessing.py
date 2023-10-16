import geopandas as gpd
import h3pandas  # noqa
import pandas as pd


def add_uk_attributes(df, oa, oa_lookup, sdz, nidz, lad):
    df["lat"], df["lng"] = df.geometry.x, df.geometry.y

    for i in range(1, 10):
        df[f"h3_0{i}"] = df.h3.geo_to_h3(i).index

    df = df.to_crs("EPSG:27700")
    df["easting"], df["northing"] = df.geometry.x, df.geometry.y
    df = gpd.sjoin(df, oa, how="left").drop(columns=["index_right"])
    df = gpd.sjoin(df, sdz, how="left").drop(columns=["index_right"])
    df = gpd.sjoin(df, nidz, how="left").drop(columns=["index_right"])
    df = df.merge(oa_lookup, on="OA21CD", how="left")
    df = df.sjoin(lad).drop(columns=["index_right"])
    return df


def remove_list_cols(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    list_cols = df.apply(lambda x: any(isinstance(i, list) for i in x))
    for col in list_cols[list_cols].index:
        df[col] = df[col].astype(str)
    return df


if __name__ == "__main__":
    places = gpd.read_parquet("./data/processed/uk_places_cleaned.parquet")
    oa = gpd.read_file("~/data/OA_2021_BGC.gpkg")[["OA21CD", "geometry"]]
    oa_lookup = pd.read_csv("~/data/OA_lookup-2021.csv").drop(columns=["ObjectId"])
    sdz = gpd.read_file("~/data/SG_DataZoneBdry_2011.zip")[
        ["DataZone", "Name", "geometry"]
    ].rename(columns={"DataZone": "DZ11CD", "Name": "DZ11NM"})
    nidz = (
        gpd.read_file("~/data/NI_DZ21.zip")
        .drop(columns=["Area_ha", "Perim_km"])
        .to_crs("EPSG: 27700")
    )
    lad = gpd.read_file("~/data/LAD_BUC_2022.gpkg")

    places = add_uk_attributes(places, oa, oa_lookup, sdz, nidz, lad)
    places.to_parquet("./data/processed/uk_places_attributes.parquet")
