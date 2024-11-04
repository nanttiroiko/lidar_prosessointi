"""
Tähän koottuna jokseenkin fiksusti toimiva pilottiversio PDAL-työnkulusta, jolla voidaan korvata LAStools LIDARK-skriptin tarpeisiin

Tällä hetkellä ongelmana on, että ilmeisesti pipeline ei toimi oikein kaikille .laz tiedostoille. Alkuperäiset testatut toimivat hyvin, mutta tampereen kanssa on ollut ongelmia.
"""

from multiprocessing import Pool, TimeoutError
import pdal
import time
import os
import json
import geopandas as gp
from pathlib import Path



#työskentelykansio
os.chdir(r'C:/Users/nikantti/pdal_wrench_testi/')
import pdal_pipe as pdal_multi
#kansiot
indir='00_Original/'
outdir='01_DTM/'
tempdir='pdal_temp/'

#Luodaan tile index 
pdal_str='pdal tindex create '+indir+'tindex.gpkg '+indir+'*.laz --lyr_name pdal --t_srs EPSG:3067 --fast_boundary -f GPKG'
os.system(pdal_str)

#luetaan tindex geodataframeksi
tindex_gdf=gp.GeoDataFrame.from_file(indir+'tindex.gpkg')
tindex_gdf['wkt']=tindex_gdf['geometry'].buffer(60).envelope.to_wkt()
       
def main():
    file_list=[]
    for row in tindex_gdf.itertuples(): 
        wkt=tindex_gdf['wkt'][row.Index]
        outfile=Path(tindex_gdf['location'][row.Index])
        outfile=outdir+outfile.stem+'_DTM.tif'
        tempfile=Path(tindex_gdf['location'][row.Index])
        tempfile=tempdir+tempfile.stem+'_temp.laz'
        tindex_path=indir+'tindex.gpkg'
        file_list.append((wkt,outfile,tempfile,tindex_path))

    print(file_list)

    #file_iter=iter(file_list)
    parallel_processes = 2
    pool = Pool(parallel_processes)
    pool.map(pdal_multi.pdal_pipe, file_list)

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(end - start) + " seconds")