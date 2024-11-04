import pdal, json, os

def pdal_pipe(pdal_kwargs):
    
    wkt=pdal_kwargs['wkt']
    output_file=pdal_kwargs['outfile']
    tempfile=pdal_kwargs['tempfile']
    tindex_path=pdal_kwargs['tindex_path']
    resolution=pdal_kwargs['resolution']
    buffer=pdal_kwargs['buffer']
    crs=pdal_kwargs['crs']

    print(tempfile)
    
    #tehdään tarvittaessa väliaikainen tiedosto bufferilla
    if buffer:
        os.system('pdal tindex merge --tindex '+tindex_path+' --filespec '+tempfile+' --lyr_name pdal --polygon "'+wkt+'" --t_srs EPSG:'+str(crs))

    pipe = [
        tempfile,
        {
          "type": "filters.range",
          "limits": "Classification[2:2]",
          "tag":"ground_pts"
        },
        {
          "type": "filters.delaunay",
          "inputs":"ground_pts",
          "tag":"tin"
        },
        {
          "type": "filters.faceraster",
          "resolution":resolution,
          "inputs":"tin",
          "tag":"dem"
        },
        {
           "type":"writers.raster",
           "inputs":"dem",
           "data_type":"float32",
           "filename":output_file
        }
    ]
    pipeline = pdal.Pipeline(json.dumps(pipe))
    count = pipeline.execute()

