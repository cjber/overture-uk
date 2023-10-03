import duckdb

# # admins
# with open("./queries/uk_admins.sql") as f:
#     admins_query = f.read()
# duckdb.query(admins_query)
#
# # buildings
# with open("./queries/uk_buildings.sql") as f:
#     buildings_query = f.read()
# duckdb.query(buildings_query)

# places
with open("./queries/uk_places.sql") as f:
    places_query = f.read()
duckdb.query(places_query)
