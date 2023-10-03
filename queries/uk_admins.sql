-- adapted from https://github.com/OvertureMaps/data/blob/main/duckdb_queries/places.sql
-- bounding box from https://epsg.io/27700

LOAD httpfs;
LOAD spatial;

COPY (
    SELECT
        type,
        version,
        CAST(updatetime as varchar) as updateTime,
        JSON(names) as names,
        JSON(sources) as sources,
        ST_GeomFromWKB(geometry) as geometry
    FROM
        read_parquet('s3://overturemaps-us-west-2/release/2023-07-26-alpha.0/theme=admins/type=*/*', hive_partitioning=1)
    WHERE
        bbox.minx > -9.0
        AND bbox.maxx < 2.01
        AND bbox.miny > 49.75
        AND bbox.maxy < 61.01
    ) TO 'data/uk_admins.gpkg'
WITH (FORMAT GDAL, DRIVER 'GPKG');
