from multiprocessing import Pool, TimeoutError
import argparse
import pdal
import glob
import time
import os
import json
import geopandas as gp
from pathlib import Path


def pdal_pipe(pdal_kwargs):
    """
    Tämä osuus sisältää varsinaisen laserkeilausaineistojen käsittelyyn käytettävän työnkulun määrittelyn.

    Työnkulku sisältää seuraavat vaiheet:
    - jos käytetään bufferia, luodaan väliaikainen .laz-tiedosto, joka sisältää myös bufferin sisään jäävät pisteet ympäröiviltä alueilta
    - käsitellään laserkeilausaineisto 
    
    """
    wkt=pdal_kwargs['wkt']
    output_file=pdal_kwargs['outfile']
    infile=pdal_kwargs['infile']
    tempfile=pdal_kwargs['tempfile']
    tindex_path=pdal_kwargs['tindex_path']
    resolution=pdal_kwargs['resolution']
    buffer=pdal_kwargs['buffer']
    crs=pdal_kwargs['crs']

    print('Käsitellään: '+infile)
    
    #tehdään tarvittaessa väliaikainen tiedosto bufferilla
    if buffer:
        os.system('pdal tindex merge --tindex '+tindex_path+' --filespec '+tempfile+' --lyr_name pdal --polygon "'+wkt+'" --t_srs EPSG:'+str(crs))

    #Käsittelyyn käytettävän PDAL-pipelinen määrittely
    pipe = [
        infile,
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
    #suoritetaan PDAL-pipeline
    pipeline = pdal.Pipeline(json.dumps(pipe))
    count = pipeline.execute()

    if os.path.isfile(tempfile):
        os.remove(tempfile)


def main(kwargs):
    """
    
    """
    
    indir='lidar/'
    outdir='dem/'
    tempdir='temp/'

    #jos out- ja temp-kansioita ei ole, luodaan ne
    for kansio in [outdir, tempdir]:
        Path(kansio).mkdir(parents=True, exist_ok=True)

    
    kwargs=vars(kwargs)
    buffer=kwargs['buffer']
    cores=kwargs['cores']
    crs=kwargs['crs']
    resolution=kwargs['resolution']

    file_list=[]
    if buffer == 0: 
        for file in glob.glob(indir+'*.laz'):
            pdal_kwargs={}
            pdal_kwargs['wkt']=""
            outfile=Path(file)
            pdal_kwargs['outfile']=outdir+outfile.stem+'_DEM.tif'
            pdal_kwargs['infile']=file
            pdal_kwargs['tempfile']=tempdir+Path(file).stem+'.laz'
            pdal_kwargs['tindex_path']=""
            pdal_kwargs['resolution']=resolution
            pdal_kwargs['crs']=crs
            pdal_kwargs['buffer']=False
            file_list.append(pdal_kwargs)
    else:
        #Luodaan tile index 
        pdal_str='pdal tindex create '+tempdir+'tindex.gpkg '+indir+'*.laz --lyr_name pdal --t_srs EPSG:3067 --fast_boundary -f GPKG'
        os.system(pdal_str)

        #luetaan tindex geodataframeksi
        tindex_gdf=gp.GeoDataFrame.from_file(tempdir+'tindex.gpkg')
        tindex_gdf['wkt']=tindex_gdf['geometry'].buffer(buffer).envelope.to_wkt()

        #for file in glob.glob(indir+'*.laz'):
        for row in tindex_gdf.itertuples():
            pdal_kwargs={}
            pdal_kwargs['wkt']=tindex_gdf['wkt'][row.Index]
            #outfile=Path(file)
            pdal_kwargs['outfile']=outdir+Path(tindex_gdf['location'][row.Index]).stem+'_DEM.tif'
            pdal_kwargs['infile']=tindex_gdf['location'][row.Index]
            pdal_kwargs['tempfile']=tempdir+'temp'+Path(tindex_gdf['location'][row.Index]).stem+'.laz'
            pdal_kwargs['tindex_path']=tempdir+'tindex.gpkg'
            pdal_kwargs['resolution']=resolution
            pdal_kwargs['crs']=crs
            pdal_kwargs['buffer']=buffer
            file_list.append(pdal_kwargs)
        
    pool = Pool(cores)
    pool.map(pdal_pipe, file_list)

    if os.path.isfile(tempdir+'tindex.gpkg'):
        os.remove(tempdir+'tindex.gpkg')

if __name__ == '__main__':
    """
    Tämä osuus käynnistää varsinaisen skriptin suorituksen.

    Lisäksi tässä osuudessa määritellään skriptin parametrit, näiden oletusarvot, sekä ilmoitetaan skriptin suorituksen viemä aika käyttäjälle.
    """
    start = time.time()
    parser = argparse.ArgumentParser(
        description="Parses arguments from CMD"
    )
    parser.add_argument('-b', '--buffer', default=0, type=int) # bufferi metreinä, oletus 0, vaikuttaa huomattavasti käsittelyaikaan
    parser.add_argument('-c','--cores', default=4, type=int) # säikeiden määrä, oletuksena 4, joka lienee ok useimmilla perustietokoneilla
    parser.add_argument('-s','--crs', default=3067, type=int) # koordinaattijärjestelmän EPSG-koodi, oletuksena ETRS89-TM35FIN (EPSG:3067)
    parser.add_argument('-r','--resolution', default=1) # tuotettavien rasterien resoluutio metreinä
    kwargs = parser.parse_args()
    print('Asetukset: '+ str(kwargs))
    
    main(kwargs)
    end = time.time()
    print("Skriptin suorittamiseen käytetty aika: " + str(end - start))
    if len(glob.glob('lidar/*.laz')) >= 1:
        print("Käsittelyaika / tiedosto:              " + str((end-start)/len(glob.glob('lidar/*.laz'))))