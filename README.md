# lidar_prosessointi

Kokoan tähän joitakin hyödyllisiä skriptejä LiDAR -aineistojen käsittelyyn ilmaisilla avoimen lähdekoodin työkaluilla (esim. PDAL).

Skriptit on tehty ensisijaisesti arkeologien tarpeisiin, mutta soveltuvat sellaisenaan tai muokattuna muihinkin tarkoituksiin.

Skriptit on laadittu suurien tiedostomäärien käsittelyä ajatellen - eli yhdellä komennolla käsitellään lähtökohtaisesti kaikki käsiteltävänä oleva aineisto.  Skriptit mahdollistavat usean tiedoston käsittelyn samanaikaisesti, mikä jonkin verran nopeuttaa prosessointia. 

Käyttöohjeissa on pyritty antamaan mahdollisimman yksinkertaiset ja seikkaperäiset ohjeet, joita noudattamalla skriptejä on mahdollista käyttää ilman aiempaa kokemusta ohjelmoinnista tai komentorivin käytöstä. 

# Esivalmistelut

## Python -ympäristön luominen

Skriptit tarvitsevat toimiakseen Python-ympäristön, johon on asennettu aineistojen käsittelyyn tarvittavat paketit (pdal, gdal, numpy, geopandas). Alla on yksityiskohtiaset ohjeet python ympäristön luomiseen Anacondan avulla. 

- Asenna Anaconda https://docs.anaconda.com/anaconda/install/
- Käynnistä Anaconda prompt
- Tee uusi Python ympäristö komennolla: conda create -n pdal pdal gdal ygeopandas numpy
Tällä komennolla Anaconda luo uuden Python ympäristön nimeltä 'pdal' ja asentaa siihen tarvittavat paketit (pdal, geopandas, numpy). Hyväksy ympäristön luominen painamalla 'y'.

## Kansiorakenne ja aineiston järjestäminen
Jotta skripti toimisi oikein, käsiteltävät tiedostot tulee järjestää kansioihin tietyllä tavalla. Skripti olettaa, että aineistot on järjestetty työskentelykansion sisällä erillisiin kansioihin aineiston tyypin perusteella seuraavasti:
- 0_lidar (laserkeilausaineisto -laz/-las -tiedostoina)
- 1_dem (korkeusmallit geotiffeinä)
- 2_visualisoinnit (valmiit visualisoinnit geotiffeinä)

Varsinaiset skriptit (eli .py -päätteiset tiedostot) tallenetaan suoraan työskentelykansioon.

Skriptit käsittelevät oletuksena kaiken kansioihin tallennetun aineiston (jolla on oletettu tiedostopääte). Tästä syystä työskentelykansiota ei kannata käyttää aineistojen säilyttämiseen, eli kopioi työskentelykansioon vain se aineisto, minkä haluat käsitellä.

Voit kopioida valmiin kansiorakenteen suoraan Githubista. Skriptit luovat tarvittaessa tuloksia ja väliaikaistiedostoja tarvittavat kansiot itse.

# Skriptien suorittaminen

Kun aloitat skriptien käytön, aktivoi aina ensin python-ympäristö ja aseta työskentelykansio.
- Avaa Anaconda prompt (ts. Anacondan oma 'komentorivi') ja aktivoi aiemmin luomasi python-ympäristö komennolla: conda activate pdal
- Aseta työskentelykansio komennolla: cd C:\lisää\oikea\polku\tähän
  - (esim. cd C:\users\kayttajatunnus\lidar_prosessointi)

Tämän jälkeen voit suorittaa skriptejä komennolla: python skriptin_nimi_tähän.py 

Tarkemmat ohjeet skriptien käyttöön ja mahdolliset lisävalinnat on esitetty alla.

## pdal_laz2dem.py

pdal_laz2dem.py tekee lidar/ -kansioon tallennetuista .laz päätteisistä tiedostoista pintamallit ja tallentaa ne kansioon dem/.

Skripti suoritetaan komennolla: python pdal_laz2dem.py

Skriptille voi antaa seuraavat valinnaiset parametrit, jotka vaikuttavat skriptin toimintaan ja pintamallien ominaisuuksiin:
- --buffer      (default=0)
  - Laserkeilaustiilten käsittelyssä käytettävä bufferi. Käytettäessä bufferia pintamallin muodostamiseen käytetään myös käsiteltävää tiiltä ympäröivät pisteet, jolloin myös pintamalleista tulee alkuperäistä laserkeilaustiiltä laajempia. Bufferin käytöstä on hyötyä esimerkiksi tiettyjen visualisointitekniikoiden kanssa (esim. TPI), jotta vältytään poikkeamilta käsitetävien tiilien reunoilla. Bufferin koko annetaan metreissä. Bufferin käyttö hidastaa jonkin verran käsittelyä.
- --cores       (default=4)
  - Rinnakkain käsiteltävien tiedostojen määrä. Tällä asetuksella voit vaikuttaa huomattavasti prosessoinnin nopeuteen. Rinnakkain käsiteltävien tiedostojen määrän tulisi olla korkeintaan yhtä suuri kuin tietokoneen loogisten suorittimien määrä, minkä voit tarkistaa esimerkiksi tehtävienhallinnasta. Huomaa kuitenkin, että tietokoneen ominaisuuksista riippuen maksimia pienempi rinnakkain käsiteltävien tiedostojen määrä voi olla kokonaisuutena nopeampi.
- --crs         (default=3067, ts. ETRS-TM35FIN / EPSG:3067)
  - Tällä asetuksella voit asettaa haluamasi koordinaattijärjestelmän. Koordinaattijärjestelmän asettamiseen käytetään EPSG-numerokoodia. 
- --resolution  (default=1)
  - Laserkeilausaineistosta tuotettavien rasterien resoluutio metreinä. Käytä desimaalierottimena pistettä.

Lisäparametrit annetaan varsinaisen komennon jälkeen, esim: python pdal_laz2dem.py --buffer=30 --cores=8 --resolution=0.5

Skriptin suorittamisen lopuksi skripti ilmoittaa käsittelyyn kuluneen ajan sekä yhden tiedoston käsittelyyn keskimäärin kuluneen ajan sekunteina. Voit käyttää tätä ominaisuutta esimerkiksi eri asetusten vaikutusten testaamiseen.

## dem2tpi.py
















