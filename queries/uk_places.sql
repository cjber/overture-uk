-- adapted from https://github.com/OvertureMaps/data/blob/main/duckdb_queries/places.sql
-- bounding box from https://epsg.io/27700

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
        bbox.minx > -9.0
        AND bbox.maxx < 2.01
        AND bbox.miny > 49.75
        AND bbox.maxy < 61.01
    ) TO 'data/raw/uk_places.gpkg'
WITH (FORMAT GDAL, DRIVER 'GPKG');
