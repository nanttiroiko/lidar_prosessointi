from pathlib import Path
import glob
import rvt.vis
import rvt.default
import numpy as np
import argparse
import time
import os
from tqdm import tqdm

#poistetaan käytöstä varoitukset, ettei printata turhia gdal varoituskäytönnön muutosinfoja
import warnings
warnings.filterwarnings("ignore")

def read_dem(dem_path):
    """
    Lukee korkeusmallin sisään ja palauttaa sen ja muut RVT-py tarvitsemat tiedot
    """
    dict_dem = rvt.default.get_raster_arr(dem_path)
    dem_arr = dict_dem["array"]  # numpy array of DEM
    dem_resolution = dict_dem["resolution"]
    dem_res_x = dem_resolution[0]  # resolution in X direction
    dem_res_y = dem_resolution[1]  # resolution in Y direction
    dem_no_data = dict_dem["no_data"]
    return dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data

def gdal_build_vrt(kansio, pyramidit):
    """
    Tekee annetun kansion .tif -päätteisistä tiedostoista virtuaalirasterin ja tallentaa sen samaan kansioon .vrt -muodossa
    Haluttaessa virtuaalirasterille voidaan tehdä ulkoiset pyramidit, eli karkeammat esikatselukuvat
    Funktio käyttää suoraan gdalbuildvrt ja gdaladdo -komentoja

    Parametrit:
    -kansio = kansio, jonka tiedostoja käsitellään. esim. 'hillshade/'
    -tee_pyramidit = True/False
    
    """
    print('luodaan virtuaalirasteri '+kansio+'/'+kansio+'.vrt')
    os.system('gdalbuildvrt '+kansio+'/'+kansio+'.vrt '+kansio+'/*.tif')

    if pyramidit:
        print('luodaan pyramidit virtuaalirasterille '+kansio+'/'+kansio+'.vrt')
        os.system('gdaladdo -r bilinear '+kansio+'/'+kansio+'.vrt 2 4 8 16 32')
    

def tallenna_tiedostoon(dem_path, output_path, output_arr, gdal_datatype):
    """
    Tallentaa valmiin rasterin tiedostoon. 
    
    RVT-py ilmeisesti kopioi osan spekseistä alkuperäisestä tiedostosta, joten tähän tarvitaan myös sen polku (?)
    """
    rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=output_path, out_raster_arr=output_arr, no_data=np.nan, e_type=gdal_datatype)
    
def slope(kwargs):
    """
    Laskee slopen RVT-py avulla ja tallentaa sen tiedostoon.

    Pakolliset argumentit:
    - dem_path = korkeusmallin tiedostopolku (str)

    Valinnaiset argumentit:
    - gdal_data_type = gdalin käyttämä koodi tallennettavan datatyypin valintaan. Oletuksena 6, eli float32  (int)
    - output_units = Tulokset yksikkö. Vaihtoehdot degree, radian, percent. Oletus degree.
    - ve_factor = Korkeuserojen liioitteluun käytettävä kerroin. Oletuksena 1.
    - slope = lasketaan slope (oletus True)
    - aspect = lasketaan aspect (oletus False)
    """
    #asetetaan tarvittaessa oletusasetukset
    if not 'gdal_datatype' in kwargs.keys():
        kwargs['gdal_datatype']=6
    if not 'output_units' in kwargs.keys():
        kwargs['output_units']='degree'
    if not 've_factor' in kwargs.keys():
        kwargs['ve_factor']=1
    if not 'slope' in kwargs.keys():
        kwargs['slope']=True
    if not 'aspect' in kwargs.keys():
        kwargs['aspect']=False

    #luetaan korkeusmalli
    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
    #lasketaan slope
    dict_slope_aspect = rvt.vis.slope_aspect(dem=dem_arr, resolution_x=dem_res_x, resolution_y=dem_res_y, 
                                             output_units=kwargs['output_units'], ve_factor=kwargs['ve_factor'], no_data=dem_no_data)

    #tallennetaan halutut tulokset tiedostoon ja luodaan tarvittaessa tallennuskansiot
    if kwargs['slope']:
        #asetaan tulostettavalle tiedostolle output_path
        output_path='slope/'+Path(kwargs['dem_path']).stem.replace('DEM','slope.tif')
        Path('slope/').mkdir(parents=True, exist_ok=True)
        slope_arr = dict_slope_aspect["slope"]
        tallenna_tiedostoon(kwargs['dem_path'], output_path, slope_arr, kwargs['gdal_datatype'])
    if kwargs['aspect']:
        Path('aspect/').mkdir(parents=True, exist_ok=True)
        aspect_arr = dict_slope_aspect["aspect"]
        output_path=output_path.replace('slope','aspect')
        tallenna_tiedostoon(kwargs['dem_path'], output_path, aspect_arr, kwargs['gdal_datatype'])

def hillshade(kwargs):
    """
    Laskee rinnevarjosteen RVT-py avulla ja tallentaa sen tiedostoon.

    Pakolliset argumentit:
    - dem_path = korkeusmallin tiedostopolku (str)

    Valinnaiset argumentit:
    - ve_factor = Korkeuserojen liioitteluun käytettävä kerroin. Oletuksena 3.
    - sun_azimuth = valonlähteen suunta asteina (myötäpäivään, pohjoinen 0)
    - sun_elevation = valonlähteen korkeus horisontista asteina
    - gdal_data_type = gdalin käyttämä koodi tallennettavan datatyypin valintaan. Oletuksena 6, eli float32  (int)
    """
    #asetetaan tarvittaessa oletusasetukset
    if not 've_factor' in kwargs.keys():
        kwargs['ve_factor']=3
    if not 'sun_azimuth' in kwargs.keys():
        kwargs['sun_azimuth']=315
    if not 'sun_elevation' in kwargs.keys():
        kwargs['sun_elevation']=45
    if not 'gdal_datatype' in kwargs.keys():
        kwargs['gdal_datatype']=6
    
    #jos hillshadelle ei ole valmiiksi kansiota, luodaan se
    Path('hillshade/').mkdir(parents=True, exist_ok=True)

    #asetaan tulostettavalle tiedostolle output_path
    output_path='hillshade/'+Path(kwargs['dem_path']).stem.replace('DEM','hillshade.tif')
        
    #luetaan korkeusmalli
    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
    #lasketaan hillshade
    hillshade_arr = rvt.vis.hillshade(dem=dem_arr, resolution_x=dem_res_x, resolution_y=dem_res_y, sun_azimuth=kwargs['sun_azimuth'], 
                                      sun_elevation=kwargs['sun_elevation'], slope=None, aspect=None, ve_factor=kwargs['ve_factor'], no_data=dem_no_data)
    
    #tallennetaan tiedostoon
    tallenna_tiedostoon(kwargs['dem_path'], output_path, hillshade_arr, kwargs['gdal_datatype'])

def multi_hillshade(kwargs):
    """
    Laskee useasta suunnasta varjostetun rinnevarjosteen RVT-py avulla ja tallentaa sen tiedostoon.

    Pakolliset argumentit:
    - dem_path = korkeusmallin tiedostopolku (str)

    Valinnaiset argumentit:
    - ve_factor = Korkeuserojen liioitteluun käytettävä kerroin. 
    - nr_directions = kuinka monesta suunnasta varjostetaan ts. azimuttien lukumäärä
    - sun_elevation = valonlähteen korkeus horisontista asteina
    - gdal_data_type = gdalin käyttämä koodi tallennettavan datatyypin valintaan. Oletuksena 6, eli float32  (int)
    """
    #asetetaan tarvittaessa oletusasetukset
    if not 've_factor' in kwargs.keys():
        kwargs['ve_factor']=1
    if not 'nr_directions' in kwargs.keys():
        kwargs['nr_directions']=3
    if not 'sun_elevation' in kwargs.keys():
        kwargs['sun_elevation']=45
    if not 'gdal_datatype' in kwargs.keys():
        kwargs['gdal_datatype']=6
    
    #jos multi_hillshadelle ei ole valmiiksi kansiota, luodaan se
    Path('multi_hillshade/').mkdir(parents=True, exist_ok=True)

    #asetaan tulostettavalle tiedostolle output_path
    output_path='multi_hillshade/'+Path(kwargs['dem_path']).stem.replace('DEM','multi_hillshade.tif')
        
    #luetaan korkeusmalli
    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
    #lasketaan multi_hillshade
    multi_hillshade_arr = rvt.vis.multi_hillshade(dem=dem_arr, resolution_x=dem_res_x, resolution_y=dem_res_y, nr_directions=kwargs['nr_directions'], 
                                                  sun_elevation=kwargs['sun_elevation'], slope=None, aspect=None, ve_factor=kwargs['ve_factor'],
                                                  no_data=dem_no_data)
    
    #tallennetaan tiedostoon
    tallenna_tiedostoon(kwargs['dem_path'], output_path, multi_hillshade_arr, kwargs['gdal_datatype'])

def slrm(kwargs):
    """
    Laskee simple relief modelin RVT-py avulla ja tallentaa sen tiedostoon.

    Pakolliset argumentit:
    - dem_path = korkeusmallin tiedostopolku (str)

    Valinnaiset argumentit:
    - ve_factor = Korkeuserojen liioitteluun käytettävä kerroin. 
    - radius_cell = kuinka monesta suunnasta varjostetaan ts. azimuttien lukumäärä
    - gdal_data_type = gdalin käyttämä koodi tallennettavan datatyypin valintaan. Oletuksena 6, eli float32  (int)
    """
    #asetetaan tarvittaessa oletusasetukset
    if not 've_factor' in kwargs.keys():
        kwargs['ve_factor']=1
    if not 'radius_cell' in kwargs.keys():
        kwargs['radius_cell']=15
    if not 'gdal_datatype' in kwargs.keys():
        kwargs['gdal_datatype']=6
    
    #jos slrm:lle ei ole valmiiksi kansiota, luodaan se
    Path('simple_local_relief_model/').mkdir(parents=True, exist_ok=True)

    #asetaan tulostettavalle tiedostolle output_path
    output_path='simple_local_relief_model/'+Path(kwargs['dem_path']).stem.replace('DEM','simple_local_relief_model.tif')
        
    #luetaan korkeusmallin tiedot
    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
    #lasketaan simple relief model
    slrm_arr = rvt.vis.slrm(dem=dem_arr, radius_cell=kwargs['radius_cell'], ve_factor=kwargs['ve_factor'], no_data=dem_no_data)

    #tallennetaan tiedostoon
    tallenna_tiedostoon(kwargs['dem_path'], output_path, slrm_arr, kwargs['gdal_datatype'])

def msrm(kwargs):
    """
    Laskee multi scale relief modelin RVT-py avulla ja tallentaa sen tiedostoon.

    Pakolliset argumentit:
    - dem_path = korkeusmallin tiedostopolku (str)

    Valinnaiset argumentit:
    - ve_factor = Korkeuserojen liioitteluun käytettävä kerroin. 
    - feature_min = kuinka monesta suunnasta varjostetaan ts. azimuuttien lukumäärä
    - feature_max = valonlähteen korkeus horisontista asteina
    - scaling_factor = 
    - gdal_data_type = gdalin käyttämä koodi tallennettavan datatyypin valintaan. Oletuksena 6, eli float32  (int)
    """
    #asetetaan tarvittaessa oletusasetukset
    if not 've_factor' in kwargs.keys():
        kwargs['ve_factor']=1
    if not 'feature_min' in kwargs.keys():
        kwargs['feature_min']=1
    if not 'feature_max' in kwargs.keys():
        kwargs['feature_max']=5
    if not 'scaling_factor' in kwargs.keys():
        kwargs['scaling_factor']=3
    if not 'gdal_datatype' in kwargs.keys():
        kwargs['gdal_datatype']=6
    
    #jos msrm:lle ei ole valmiiksi kansiota, luodaan se
    Path('multi-scale_relief_model/').mkdir(parents=True, exist_ok=True)

    #asetaan tulostettavalle tiedostolle output_path
    output_path='multi-scale_relief_model/'+Path(kwargs['dem_path']).stem.replace('DEM','multi-scale_relief_model.tif')
        
    #luetaan korkeusmallin tiedot
    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
    #lasketaan multi scale relief model
    msrm_arr = rvt.vis.msrm(dem=dem_arr, resolution=dem_res_x, feature_min=kwargs['feature_min'], feature_max=kwargs['feature_max'], 
                            scaling_factor=kwargs['scaling_factor'], ve_factor=kwargs['ve_factor'], no_data=dem_no_data)

    #tallennetaan tiedostoon
    tallenna_tiedostoon(kwargs['dem_path'], output_path, msrm_arr, kwargs['gdal_datatype'])

def mstp(kwargs):
    """
    Laskee multi scale relief modelin RVT-py avulla ja tallentaa sen tiedostoon.

    Pakolliset argumentit:
    - dem_path = korkeusmallin tiedostopolku (str)

    Valinnaiset argumentit:
    - ve_factor = Korkeuserojen liioitteluun käytettävä kerroin. 
    - local_scale = (min, max, step)
    - meso_scale = (min, max, step)
    - broad_scale = (min, max, step)
    - lightness = parhaat tulokset 0.8 - 1.6
    - gdal_data_type = gdalin käyttämä koodi tallennettavan datatyypin valintaan. Oletuksena 6, eli float32  (int)
    """
    #asetetaan tarvittaessa oletusasetukset
    if not 've_factor' in kwargs.keys():
        kwargs['ve_factor']=1
    if not 'local_scale' in kwargs.keys():
        kwargs['local_scale']=(1,5,1) # min, max, step
    if not 'meso_scale' in kwargs.keys():
        kwargs['meso_scale']=(5,50,5) # min, max, step
    if not 'broad_scale' in kwargs.keys():
        kwargs['broad_scale']=(50,500,50) # min, max, step
    if not 'lightness' in kwargs.keys():
        kwargs['lightness']=1.2
    if not 'gdal_datatype' in kwargs.keys():
        kwargs['gdal_datatype']=6

    #jos mstp:lle ei ole valmiiksi kansiota, luodaan se
    Path('multi-scale_topographic_position/').mkdir(parents=True, exist_ok=True)

    #asetaan tulostettavalle tiedostolle output_path
    output_path='multi-scale_topographic_position/'+Path(kwargs['dem_path']).stem.replace('DEM','multi-scale_topographic_position.tif')
        
    #luetaan korkeusmallin tiedot
    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
    #lasketaan mstp
    mstp_arr = rvt.vis.mstp(dem=dem_arr, local_scale=kwargs['local_scale'], meso_scale=kwargs['meso_scale'], broad_scale=kwargs['broad_scale'],
                            lightness=kwargs['lightness'], ve_factor=kwargs['ve_factor'], no_data=dem_no_data)
    #tallennetaan tiedostoon
    tallenna_tiedostoon(kwargs['dem_path'], output_path, mstp_arr, kwargs['gdal_datatype'])

def svf(kwargs):
    """
    Laskee valinnan mukaan sky-view factorin, anistropic sky-view factorin tai positive/negative opennessin RVT-py avulla ja tallentaa tiedostoon.

    Pakolliset argumentit:
    - dem_path = korkeusmallin tiedostopolku (str)

    Valinnaiset argumentit:
    ks. alla

    """
    #asetetaan tarvittaessa oletusasetukset
    if not 've_factor' in kwargs.keys():
        kwargs['ve_factor']=1
    if not 'gdal_datatype' in kwargs.keys():
        kwargs['gdal_datatype']=6
    # svf, sky-view factor parameters which also applies to asvf and opns
    if not 'compute_svf' in kwargs.keys():
        kwargs['compute_svf']=False           #bool, if true it computes sky-view factor
    if not 'compute_asvf' in kwargs.keys():
        kwargs['compute_asvf']=False          #bool, if true it computes anisotropic svf
    if not 'copmute_opns' in kwargs.keys():
        kwargs['copmute_opns']=False          #bool, if true it computes positive openness
    if not 'svf_n_dir' in kwargs.keys():
        kwargs['svf_n_dir']=16               # number of directions
    if not 'svf_r_max' in kwargs.keys():
        kwargs['svf_r_max']=10               # max search radius in pixels
    if not 'svf_noise' in kwargs.keys():
        kwargs['svf_noise']=0                # level of noise remove (0-don't remove, 1-low, 2-med, 3-high)
    # asvf, anisotropic svf parameters
    if not 'asvf_level' in kwargs.keys():
        kwargs['asvf_level']=1               # level of anisotropy (1-low, 2-high)
    if not 'asvf_dir' in kwargs.keys():
        kwargs['asvf_dir']=315               # dirction of anisotropy in degrees

    #jos svf:lle ei ole valmiiksi kansiota, luodaan se
    if kwargs['compute_svf']:
        Path('sky-view_factor/').mkdir(parents=True, exist_ok=True)
        output_path_svf='sky-view_factor/'+Path(kwargs['dem_path']).stem.replace('DEM','swf.tif')
    #jos asvf:lle ei ole valmiiksi kansiota, luodaan se
    if kwargs['compute_asvf']:
        Path('anisotropic_sky-view_factor/').mkdir(parents=True, exist_ok=True)
        output_path_asvf='anisotropic_sky-view_factor/'+Path(kwargs['dem_path']).stem.replace('DEM','aswf.tif')
    #jos openness:lle ei ole valmiiksi kansioita, luodaan ne
    if kwargs['copmute_opns']:
        Path('positive_openness/').mkdir(parents=True, exist_ok=True)
        output_path_popns='positive_openness/'+Path(kwargs['dem_path']).stem.replace('DEM','pos-openness.tif')
        Path('negative_openness/').mkdir(parents=True, exist_ok=True)
        output_path_nopns='negative_openness/'+Path(kwargs['dem_path']).stem.replace('DEM','neg-openness.tif')
        
    #luetaan korkeusmallin tiedot
    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
    #lasketaan svr/asvf/positive-openness
    dict_svf = rvt.vis.sky_view_factor(dem=dem_arr, resolution=dem_res_x, compute_svf=kwargs['compute_svf'], compute_asvf=kwargs['compute_asvf'],
                                       compute_opns=kwargs['copmute_opns'], svf_n_dir=kwargs['svf_n_dir'], svf_r_max=kwargs['svf_r_max'],
                                       svf_noise=kwargs['svf_noise'], asvf_level=kwargs['asvf_level'], asvf_dir=kwargs['asvf_dir'], no_data=dem_no_data)
    
    #tallennetaan tiedostoon
    #svf
    if kwargs['compute_svf']:
        tallenna_tiedostoon(kwargs['dem_path'], output_path_svf, dict_svf["svf"], kwargs['gdal_datatype'])
    #asvf
    if kwargs['compute_asvf']:
        tallenna_tiedostoon(kwargs['dem_path'], output_path_asvf, dict_svf["asvf"], kwargs['gdal_datatype'])
    #openness
    if kwargs['copmute_opns']:
        tallenna_tiedostoon(kwargs['dem_path'], output_path_popns, dict_svf["opns"], kwargs['gdal_datatype'])
        #tarvittaessa lasketaan myös negative openness
        dem_arr_neg_opns = dem_arr * -1  # dem * -1 for neg opns 
        dict_neg_openness = rvt.vis.sky_view_factor(dem=dem_arr_neg_opns, resolution=dem_res_x, compute_svf=False, compute_asvf=False, compute_opns=True,
                                   svf_n_dir=kwargs['svf_n_dir'], svf_r_max=kwargs['svf_r_max'], svf_noise=kwargs['svf_noise'],
                                   asvf_level=kwargs['asvf_level'], asvf_dir=kwargs['asvf_dir'],
                                   no_data=dem_no_data)
        tallenna_tiedostoon(kwargs['dem_path'], output_path_nopns, dict_neg_openness["opns"], kwargs['gdal_datatype'])

def dominance(kwargs):
    """
    Laskee local dominancen RVT-py avulla ja tallentaa sen tiedostoon.

    Pakolliset argumentit:
    - dem_path = korkeusmallin tiedostopolku (str)

    Valinnaiset argumentit:
    - ve_factor = Korkeuserojen liioitteluun käytettävä kerroin. 
    - min_rad = minimum radial distance
    - max_rad = maximum radial distance
    - rad_inc = radial distance steps in pixels
    - angular_res = angular step for determination of number of angular directions
    - observer_height = height at which we observe the terrain
    - gdal_data_type = gdalin käyttämä koodi tallennettavan datatyypin valintaan. Oletuksena 6, eli float32  (int)
    """
    #asetetaan tarvittaessa oletusasetukset
    if not 've_factor' in kwargs.keys():
        kwargs['ve_factor']=1
    if not 'min_rad' in kwargs.keys():
        kwargs['min_rad']=10
    if not 'max_rad' in kwargs.keys():
        kwargs['max_rad']=20
    if not 'rad_inc' in kwargs.keys():
        kwargs['rad_inc']=1
    if not 'angular_res' in kwargs.keys():
        kwargs['angular_res']=15
    if not 'observer_height' in kwargs.keys():
        kwargs['observer_height']=1.7
    if not 'gdal_datatype' in kwargs.keys():
        kwargs['gdal_datatype']=6

    #jos local dominance:lle ei ole valmiiksi kansiota, luodaan se
    Path('local_dominance/').mkdir(parents=True, exist_ok=True)

    #asetaan tulostettavalle tiedostolle output_path
    output_path='local_dominance/'+Path(kwargs['dem_path']).stem.replace('DEM','local_dominance.tif')
        
    #luetaan korkeusmallin tiedot
    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
    #lasketaan local dominance
    local_dom_arr = rvt.vis.local_dominance(dem=dem_arr, min_rad=kwargs['min_rad'], max_rad=kwargs['max_rad'], rad_inc=kwargs['rad_inc'], 
                                            angular_res=kwargs['angular_res'], observer_height=kwargs['observer_height'], ve_factor=kwargs['ve_factor'],
                                            no_data=dem_no_data)
    #tallennetaan tiedostoon
    tallenna_tiedostoon(kwargs['dem_path'], output_path, local_dom_arr, kwargs['gdal_datatype'])

#def sky_illumination(kwargs):
#    """
#    Laskee local sky illuminationin RVT-py avulla ja tallentaa sen tiedostoon.
#
#    Pakolliset argumentit:
#    - dem_path = korkeusmallin tiedostopolku (str)
#
#    Valinnaiset argumentit:
#    - ve_factor = Korkeuserojen liioitteluun käytettävä kerroin. 
#    - sky_model = ("overcast" or "uniform")
#    - compute_shadow = (True/False,  if true it adds shadow)
#    - max_fine_radius = max shadow modeling distance in pixels
#    - num_directions = (number of directions to search for horizon)
#    - shadow_az = (shadow azimuth if copute_shadow is true)
#    - shadow_el = (shadow elevation if compute_shadow is true)
#    - gdal_data_type = gdalin käyttämä koodi tallennettavan datatyypin valintaan. Oletuksena 6, eli float32  (int)
#    """
#    #asetetaan tarvittaessa oletusasetukset
#    if not 've_factor' in kwargs.keys():
#        kwargs['ve_factor']=1
#    if not 'sky_model' in kwargs.keys():
#        kwargs['sky_model']="uniform"
#    if not 'compute_shadow' in kwargs.keys():
#        kwargs['compute_shadow']=False
#    if not 'max_fine_radius' in kwargs.keys():
#        kwargs['max_fine_radius']=50
#    if not 'num_directions' in kwargs.keys():
#        kwargs['num_directions']=16
#    if not 'shadow_az' in kwargs.keys():
#        kwargs['shadow_az']=315
#    if not 'shadow_el' in kwargs.keys():
#        kwargs['shadow_el']=35
#    if not 'gdal_datatype' in kwargs.keys():
#        kwargs['gdal_datatype']=6
#
#    #jos sky_illumination:lle ei ole valmiiksi kansiota, luodaan se
#    Path('sky_illumination/').mkdir(parents=True, exist_ok=True)
#
#    #asetaan tulostettavalle tiedostolle output_path
#    output_path='sky_illumination/'+Path(kwargs['dem_path']).stem.replace('DEM','sky_illumination.tif')
#        
#    #luetaan korkeusmallin tiedot
#    dict_dem, dem_arr, dem_resolution, dem_res_x, dem_res_y, dem_no_data = read_dem(kwargs['dem_path'])
#    #lasketaan sky illumination
#    sky_illum_arr = rvt.vis.sky_illumination(dem=dem_arr, resolution=dem_res_x, sky_model=kwargs['sky_model'],
#                                         max_fine_radius=kwargs['max_fine_radius'], num_directions=kwargs['num_directions'],
#                                         shadow_az=kwargs['shadow_az'], shadow_el=kwargs['shadow_el'], ve_factor=1,
#                                         no_data=dem_no_data)
#    #tallennetaan tiedostoon
#    tallenna_tiedostoon(kwargs['dem_path'], output_path, sky_illum_arr, kwargs['gdal_datatype'])

def rvt_prosessoi(kwargs):
    """
    Tämä funktio määrittää argumenttien perusteella suoritettavan RVT-py komennon ja argumentit eteenpäin seuraavalle funktiolle
    
    """
    
    
    #tehdään lista suoritettavista toiminnoista. Tällä mahdollistetaan useiden toimintojen suorittaminen samalla komennolla
    metodit=kwargs['visualisoinnit'].split(';')
    metodit = [m.strip(' ') for m in metodit]

    #listataan käsiteltävät rasterit
    rasterit=glob.glob('dem/*.tif')

    #tarkistetaan suoritettavat metodit ja lasketaan visualisoinnit
    if 'slope' in metodit or 'kaikki' in metodit or 'aspect' in metodit:
        if 'slope' in metodit or 'kaikki' in metodit:
            kwargs['slope']=True
        if 'aspect' in metodit or 'kaikki' in metodit:
            kwargs['aspect']=True
        print("Käsitellään slope ja/tai aspect")
        for i in tqdm(range(len(rasterit))):
            kwargs['dem_path']=rasterit[i]
            slope(kwargs)
        #lasketaan tarvittaessa vrt ja pyramidit
        if kwargs['vrt']:
            if 'slope' in metodit or 'kaikki' in metodit:
                gdal_build_vrt('slope', kwargs['vrt_pyramidit'])
            if 'aspect' in metodit or 'kaikki' in metodit:
                gdal_build_vrt('aspect', kwargs['vrt_pyramidit'])
            
    if 'hillshade' in metodit or 'kaikki' in metodit:
        print("Käsitellään hillshade")
        for i in tqdm(range(len(rasterit))):
            kwargs['dem_path']=rasterit[i]
            hillshade(kwargs)
        #lasketaan tarvittaessa vrt ja pyramidit
        if kwargs['vrt']:
            gdal_build_vrt('hillshade', kwargs['vrt_pyramidit'])
            
    if 'multi_hillshade' in metodit or 'mdhs' in metodit or 'kaikki' in metodit:
        print("Käsitellään multi_hillshade (mdhs)")
        for i in tqdm(range(len(rasterit))):
            kwargs['dem_path']=rasterit[i]
            multi_hillshade(kwargs)
        #lasketaan tarvittaessa vrt ja pyramidit
        if kwargs['vrt']:
            gdal_build_vrt('multi_hillshade', kwargs['vrt_pyramidit'])
            
    if 'simple_local_relief_model' in metodit or 'slrm' in metodit or 'kaikki' in metodit:
        print("Käsitellään simple_local_relief_model (slrm)")
        for i in tqdm(range(len(rasterit))):
            kwargs['dem_path']=rasterit[i]
            slrm(kwargs)
        #lasketaan tarvittaessa vrt ja pyramidit
        if kwargs['vrt']:
            gdal_build_vrt('simple_local_relief_model', kwargs['vrt_pyramidit'])
        
    if 'multi-scale_relief_model' in metodit or 'msrm' in metodit or 'kaikki' in metodit:
        print("Käsitellään multi-scale_relief_model (msrm)")
        for i in tqdm(range(len(rasterit))):
            kwargs['dem_path']=rasterit[i]
            msrm(kwargs)
        #lasketaan tarvittaessa vrt ja pyramidit
        if kwargs['vrt']:
            gdal_build_vrt('multi-scale_relief_model', kwargs['vrt_pyramidit'])
            
    if 'multi-scale_topographic_position' in metodit or 'mstp' in metodit or 'kaikki' in metodit:
        print("Käsitellään multi-scale_topographic_position (mstp)")
        for i in tqdm(range(len(rasterit))):
            kwargs['dem_path']=rasterit[i]
            mstp(kwargs)
        #lasketaan tarvittaessa vrt ja pyramidit
        if kwargs['vrt']:
            gdal_build_vrt('multi-scale_topographic_position', kwargs['vrt_pyramidit'])
            
    if 'sky-view_factor' in metodit or 'anisotropic_sky-view_factor' in metodit or 'openness' in metodit or 'kaikki' in metodit:
        if 'sky-view_factor' in metodit or 'svf' in metodit or 'kaikki' in metodit:
            kwargs['compute_svf']=True
        if 'anisotropic_sky-view_factor' in metodit or 'asvf' in metodit or 'kaikki' in metodit:
            kwargs['compute_asvf']=True
        if 'openness' in metodit or 'kaikki' in metodit:
            kwargs['copmute_opns']=True
            print("Käsitellään sky-view_factor (svf), anisotropic_sky-view_factor (asvf) ja/tai topographic openness")
        for i in tqdm(range(len(rasterit))):
            kwargs['dem_path']=rasterit[i]
            svf(kwargs)
        #lasketaan tarvittaessa vrt ja pyramidit
        if kwargs['vrt']:
            if 'sky-view_factor' in metodit or 'svf' in metodit or 'kaikki' in metodit:
                gdal_build_vrt('sky-view_factor', kwargs['vrt_pyramidit'])
            if 'anisotropic_sky-view_factor' in metodit or 'asvf' in metodit or 'kaikki' in metodit:
                gdal_build_vrt('anisotropic_sky-view_factor', kwargs['vrt_pyramidit'])
            if 'openness' in metodit or 'kaikki' in metodit:
                gdal_build_vrt('positive_openness', kwargs['vrt_pyramidit'])
                gdal_build_vrt('negative_openness', kwargs['vrt_pyramidit'])
            
    if 'local_dominance' in metodit or 'kaikki' in metodit:
        print("Käsitellään local_dominance")
        for i in tqdm(range(len(rasterit))):
            kwargs['dem_path']=rasterit[i]
            dominance(kwargs)
        #lasketaan tarvittaessa vrt ja pyramidit
        if kwargs['vrt']:
            gdal_build_vrt('local_dominance', kwargs['vrt_pyramidit'])

if __name__ == '__main__':
    start = time.time()
    parser = argparse.ArgumentParser()
    #parser.add_argument('-c', '--cores', default=2, type=int) # säikeiden määrä, oletuksena 2, joka lienee ok useimmilla perustietokoneilla
    parser.add_argument('-v', '--visualisoinnit', default='hillshade', type=str) # säikeiden määrä, oletuksena 4, joka lienee ok useimmilla perustietokoneilla
    parser.add_argument('--vrt', default=True, type=bool) # luodaanko käsittelyn jälkeen virtuaalirasteri
    parser.add_argument('--vrt_pyramidit', default=True, type=bool) # luodaanko virtuaalirasterille pyramidit
    parser.add_argument('--gdal_datatype', type=int) #kaikki - tulostettavan tiedoston GDAL datyyppikoodi oletuksena visualisoinneissa yleensä 6, eli float32
    parser.add_argument('--ve_factor', type=float)   #monet - vertical exaggeration factor korkeuserojen liioitteluun käytettävä kerroin
    parser.add_argument('--output_units', type=str)  #slope - tulosten ilmoittamiseen käytetty yksikkö. vaihtoehdot 'degree', 'radian', 'percent'
    parser.add_argument('--sun_azimuth', type=int)   #hillshade - valonlähteen suunta/atsimuutti asteina
    parser.add_argument('--sun_elevation', type=int) #hillshade, mdhs - valonlähteen korkeus horisontista asteina
    parser.add_argument('--nr_directions', type=int) #multihillshade - valaisusuuntien määrä
    parser.add_argument('--radius_cell', type=int)   #slrm - laskentaan käytetty säde soluina/pikseleinä
    parser.add_argument('--feature_min', type=int)   #msrm - tarkasteltavien ilmiöiden oletettu minimikoko
    parser.add_argument('--feature_max', type=int)   #msrm - tarkasteltavien ilmiöiden oletettu maksimikoko
    parser.add_argument('--scaling_factor', type=int)#msrm - 
    parser.add_argument('--local_scale', type=tuple) #mstp - tuple (min, max, step)
    parser.add_argument('--meso_scale', type=tuple)  #mstp - tuple (min, max, step)
    parser.add_argument('--broad_scale', type=tuple) #mstp - tuple (min, max, step)
    parser.add_argument('--lightness', type=float)   #mstp - lightness parametri
    parser.add_argument('--svf_n_dir', type=int)     #svf, asvf, opns
    parser.add_argument('--svf_r_max', type=int)     #svf, asvf, opns
    parser.add_argument('--svf_noise', type=int)     #svf, asvf, opns
    parser.add_argument('--asvf_level', type=int)    #asvf - anisotropian taso 1-matala 2-korkea
    parser.add_argument('--asvf_dir', type=int)      #asvf - anisotropian suunta asteina
    parser.add_argument('--min_rad', type=int)       #dominance - minimi säteittäinen etäisyys
    parser.add_argument('--max_rad', type=int)       #dominance - maksimi säteittäinen etäisyys
    parser.add_argument('--rad_inc', type=int)       #dominance - säteittäisen etäisyyden askelkoko pikseleinä
    parser.add_argument('--angular_res', type=int)   #dominance - tarkasteltavien suuntien välinen kulma
    parser.add_argument('--observer_height', type=float) #dominance -tarkastelupisteen korkeus


    #muotoillaan argiumenttihakemistoa poistamalla ne, joita ei saatu syötteenä
    temp_kwargs = parser.parse_args()
    temp_kwargs=vars(temp_kwargs)
    kwargs={}
    for kw in temp_kwargs:
        if temp_kwargs[kw] != None:
            kwargs[kw]=temp_kwargs[kw]
    
    print('Asetukset: '+ str(kwargs))
    
    rvt_prosessoi(kwargs)
    end = time.time()
    print("Skriptin suorittamiseen käytetty aika: " + str(end - start))
    if len(glob.glob('dem/*.tif')) >= 1:
        print("Käsittelyaika / tiedosto:              " + str((end-start)/len(glob.glob('dem/*.tif'))))
    
    