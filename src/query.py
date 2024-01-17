from argparse import ArgumentParser
from pathlib import Path

import duckdb

parser = ArgumentParser()
parser.add_argument("--minx", type=float, required=True)
parser.add_argument("--maxx", type=float, required=True)
parser.add_argument("--miny", type=float, required=True)
parser.add_argument("--maxy", type=float, required=True)
parser.add_argument("--filename", type=str, required=True)

args = parser.parse_args()

filename = Path(args.filename)

# buildings
query = f"""
-- adapted from https://github.com/OvertureMaps/data/blob/main/duckdb_queries/places.sql
-- bounding box from https://epsg.io/27700
INSTALL httpfs;
INSTALL spatial;

LOAD httpfs;
LOAD spatial;

COPY (
    SELECT
       id,
       updatetime,
       version,
       CAST(names AS JSON) AS names,
       CAST(categories AS JSON) AS categories,
       confidence,
       CAST(websites AS JSON) AS websites,
       CAST(socials AS JSON) AS socials,
       CAST(emails AS JSON) AS emails,
       CAST(phones AS JSON) AS phones,
       CAST(brand AS JSON) AS brand,
       CAST(addresses AS JSON) AS addresses,
       CAST(sources AS JSON) AS sources,
       ST_GeomFromWKB(geometry)
    FROM
       read_parquet('s3://overturemaps-us-west-2/release/2023-07-26-alpha.0/theme=places/type=*/*', hive_partitioning=1)
    WHERE
        bbox.minx > {args.minx}
        AND bbox.maxx < {args.maxx}
        AND bbox.miny > {args.miny}
        AND bbox.maxy < {args.maxy}
    ) TO 'data/raw/{filename}.gpkg' -- can't use parquet yet
WITH (FORMAT GDAL, DRIVER 'GPKG');
"""

duckdb.query(query)

# remove left-over rtree file
rtree_file = Path(f"data/raw/{filename}.gpkg.tmp_rtree_{filename}.db")
if rtree_file.exists():
    rtree_file.unlink()
