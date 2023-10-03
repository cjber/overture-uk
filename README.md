# Overture Data Processing

Uses `duckdb` to query the [Overture Maps Data](https://github.com/OvertureMaps/data) for the United Kingdom. Data processed into both `gpkg` and `geoparquet` formats.

`src/queries.py` uses the `.sql` files in `queries/` to downlaod the data using a DuckDB query, `src/clean.py` then processes the `.gpkg` to normalise the `json` columns and add/remove lists to save as `.parquet` and `.gpkg` formats.
