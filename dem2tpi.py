import numpy as np
from osgeo import gdal
from affine import Affine
import rasterio
import glob
from pathlib import Path
from multiprocessing import Pool, TimeoutError
import argparse
import time

def numpy_dem2tpi(kwargs):
    """
    Funktio, jolla lasketaan topographic position index (TPI) annetun korkeusmallin perusteella. Funktio ottaa hakemistona seuraavat parametrit:
    -dem=korkeusmallin tiedostopolku
    -output=tulostettavan tpi:n tiedostopolku
    -radius=TPI:n laskennassa käytettävä säde pikseleinä
    Funktio perustuu suurelta osin Zoran Cuckovicin numpy-implementaatioon pienin muutoksin (ks. https://landscapearchaeology.org/2021/python-tpi/)
    """
    #asetetaan input ja output tiedostopolut
    dem_path=kwargs['dem']
    output_path=kwargs['output']

    print('Käsitellään ' + output_path)

    # luetaan dem
    dem_img = rasterio.open(dem_path)
    profile = dem_img.profile
    dem = dem_img.read(1)
    dem[dem <= 0] = np.nan  # values lower than 0 in the DTM is beeing ignored.

    #lasketaan TPI:n laskentaan käytettävä säde pikseleinä (oletetaan pikselit neliömäisiksi)
    radius=int(kwargs['radius']/abs(profile['transform'][0]))

    #Koodi liukuvan ikkunan asettamiseksi. Luo annetun säteen perusteella ympyrän muotoisen filtterin
    win = np.ones((2* radius +1, 2* radius +1))   # koko molempiin suuntiin 2x säde +1, jotta tulos olisi aina pariton
    r_x, r_y  = win.shape[0]//2, win.shape[1]//2  # ikkunan keskipiste
    win[r_x, r_y]=0                               # asetetaan ikkunan keskipisteen painoksi 0
    for x in range(2*radius+1):
        for y in range (2*radius+1):
            if np.linalg.norm(np.array([(x-radius), y-radius])) >= radius+0.5:
                win[x,y]=0
            elif np.linalg.norm(np.array([(x-radius), y-radius])) >= radius+0.1:
                win[x,y]=0.5
            
    def view (offset_y, offset_x, shape, step=1):
        """
        Function returning two matching numpy views for moving window routines.
        - 'offset_y' and 'offset_x' refer to the shift in relation to the analysed (central) cell 
        - 'shape' are 2 dimensions of the data matrix (not of the window!)
        - 'view_in' is the shifted view and 'view_out' is the position of central cells
        (see on LandscapeArchaeology.org/2018/numpy-loops/)
        """
        size_y, size_x = shape
        x, y = abs(offset_x), abs(offset_y)
        
        x_in = slice(x , size_x, step) 
        x_out = slice(0, size_x - x, step)
    
        y_in = slice(y, size_y, step)
        y_out = slice(0, size_y - y, step)
     
        # the swapping trick    
        if offset_x < 0: x_in, x_out = x_out, x_in                                 
        if offset_y < 0: y_in, y_out = y_out, y_in
     
        # return window view (in) and main view (out)
        return np.s_[y_in, x_in], np.s_[y_out, x_out]

    #dem = gdal.Open(dem_path)
    mx_z = dem

    #matrices for temporary data
    mx_temp = np.zeros(mx_z.shape)
    mx_count = np.zeros(mx_z.shape)

    # loop through window and accumulate values
    for (y,x), weight in np.ndenumerate(win):
        
        if weight == 0 : continue  #skip zero values !
        # determine views to extract data 
        view_in, view_out = view(y - r_y, x - r_x, mx_z.shape)
        # using window weights (eg. for a Gaussian function)
        mx_temp[view_out] += mx_z[view_in]  * weight
        
        # track the number of neighbours 
        # (this is used for weighted mean : Σ weights*val / Σ weights)
        mx_count[view_out] += weight

    # this is TPI (spot height – average neighbourhood height)
    out = mx_z - mx_temp / mx_count

    # Muunnetaan tietotyyppi kokonaisluvuksi ja skaalataan välille -100 - 100 (suuremmat/pienemmät leikataan vaihteluvälille)
    out = np.nan_to_num(out, nan=0)
    out = out * 100
    out[out > 100] = 100
    out[out < -100] = -100
    out = out.astype(dtype='int16')

    profile['dtype'] = 'int16'
    profile['nodata'] = None

    # Leikataan käytetyn säteen levyinen kaistale reunoista, koska näissä voi esiintyä virheitä
    old_trans = profile['transform']
    buffer_size = radius
    out = out[buffer_size:-buffer_size, buffer_size:-buffer_size]

    # Päivitetään uuden tiedoston georeferointitiedot
    profile['height'] = out.shape[0]
    profile['width'] = out.shape[1]
    profile['transform'] = Affine(old_trans[0], old_trans[1], old_trans[2] + radius/2, old_trans[3],
                                  old_trans[4], old_trans[5] - radius/2)
    profile['crs']  = kwargs['crs']

    # yritetään tulostaa tiedosto geotiffiksi
    try:
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(out, 1)
    except:
        print("Tiedoston " + output_path + " kirjoittaminen ei onnistunut")

def main(kwargs):
    kwargs=vars(kwargs)

    #asetetaan kansiot
    indir='dem/'
    outdir='tpi_radius_'+str(kwargs['radius'])+'/'
    
    #jos output-kansiota ei ole, luodaan se
    for kansio in [outdir]:
        Path(kansio).mkdir(parents=True, exist_ok=True)

    #tehdään multiprocessingia varten listaus tiedostoista ja parametreista
    file_list=[]
    for file in glob.glob(indir+'*.tif'):
        pdal_kwargs={}
        pdal_kwargs['dem']=file
        outfile=Path(file).stem
        #jos korvataan mahdollinen pintamallin pääte tpi-päätteellä (tai lisätään pääte, jos edellistä ei ole)
        if '_DEM' in outfile:
            outfile=outfile.replace('_DEM','_TPI.tif')
        else:
            outfile=outfile+'_TPI.tif'
        pdal_kwargs['output']=outdir+outfile
        pdal_kwargs['radius']=kwargs['radius']
        pdal_kwargs['crs']=kwargs['crs']
        file_list.append(pdal_kwargs)

    #suoritetaan TPI:n laskeva skripti multiprocessingin avulla
    pool = Pool(kwargs['cores'])
    pool.map(numpy_dem2tpi, file_list)

if __name__ == '__main__':
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cores', default=4, type=int) # säikeiden määrä, oletuksena 4, joka lienee ok useimmilla perustietokoneilla
    parser.add_argument('-r','--radius', type=int) # laskentaan käytettävä säde metreinä
    parser.add_argument('-s','--crs', default=3067, type=int) # koordinaattijärjestelmän EPSG-koodi, oletuksena ETRS89-TM35FIN (EPSG:3067)
    kwargs = parser.parse_args()
    print('Asetukset: '+ str(kwargs))
    
    main(kwargs)
    end = time.time()
    print("Skriptin suorittamiseen käytetty aika: " + str(end - start))
    if len(glob.glob('dem/*.tif')) >= 1:
        print("Käsittelyaika / tiedosto:              " + str((end-start)/len(glob.glob('dem/*.tif'))))

    