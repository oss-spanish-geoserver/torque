import sys;

tile_sql = """
WITH par AS (
    WITH innerpar AS (
        SELECT 1.0/(CDB_XYZ_Resolution({zoom})*{resolution}) as resinv
    ),
    bounds AS (
        SELECT min({column_conv}) as start, (max({column_conv}) - min({column_conv}) )/{steps} step 
        FROM ({_sql}) _i
    )
    SELECT CDB_XYZ_Resolution({zoom})*{resolution} as res, innerpar.resinv as resinv, start, step FROM innerpar, bounds
)
select
   floor(st_x(i.{gcol})*resinv) as xx,
   floor(st_y(i.{gcol})*resinv) as yy
   , {countby} c
   , floor(({column_conv} - start)/step) d
    FROM ({_sql}) i, par p
    GROUP BY xx, yy, d

"""

if len(sys.argv) != 6:
    print "python torque_query.py zoom resolution time_column steps table"
    print "example: "
    print """python torque_query.py 14 1 "date_part('epoch', date)" 512 "select * from ships" """

    sys.exit()

zoom=int(sys.argv[1])
for x in xrange(zoom):
    mat = "DROP MATERIALIZED VIEW IF EXISTS table_zoom_%d ;\n" % x
    mat += "create materialized view table_zoom_%d as " % x

    mat += tile_sql.format(
        zoom=x,
        resolution=int(sys.argv[2]),
        gcol='the_geom_webmercator',
        column_conv=sys.argv[3],
        steps=int(sys.argv[4]),
        _sql=sys.argv[5],
        countby='count(cartodb_id)'
    )

    mat +=";"

    print mat


