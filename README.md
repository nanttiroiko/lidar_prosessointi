# lidar_prosessointi

Tähän on koottu kokoelma skriptejä LiDAR -aineistojen käsittelyyn ilmaisilla avoimen lähdekoodin työkaluilla (esim. PDAL ja SAGA).

Skriptit on tehty ensisijaisesti arkeologien tarpeisiin, mutta soveltuvat yhtä hyvin muuhunkin käyttöön.

# Esivalmistelut

Skriptit käyttävät laserkeilausaineistojen käsittelyyn pääasiassa PDAL-kirjastoa tai SAGAa. 

## Python - ympäristön luominen

Skriptit voi suorittamiseen tarvitaan

Skriptit tarvitsevat toimiakseen Python-ympäristön, johon on asennettu aineistojen käsittelyyn tarvittavat paketit (pdal). Alla on yksityiskohtiaset ohjeet python ympäristön luomiseen Anacondan avulla. 

1 - Asenna Anaconda https://docs.anaconda.com/anaconda/install/
2 - Käynnistä Anaconda prompt
3 - Tee uusi Python ympäristö komennolla: conda create -n pdal pdal geopandas numpy
Tällä komennolla Anaconda luo uuden Python ympäristön nimeltä 'pdal' ja asentaa siihen tarvittavat paketit (pdal, geopandas, numpy). Hyväksy ympäristön luominen painamalla 'y'.

## Kansiorakenne ja aineiston järjestäminen
Jotta skripti toimisi oikein, käsiteltävät tiedostot tulee järjestää kansioihin aina samalla tavalla.  


# Skriptien ajaminen
tapa 1 komentoriviltä
tapa 2 jupyter notebook








