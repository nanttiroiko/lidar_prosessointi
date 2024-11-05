# lidar_prosessointi

Tähän on koottu joitakin hyödyllisiä skriptejä LiDAR -aineistojen tehokkaaseen käsittelyyn ilmaisilla avoimen lähdekoodin työkaluilla (esim. PDAL).

Skriptit on tehty erityisesti suuria tiedostomääriä ajatellen - eli yhdellä komennolla käsitellään lähtökohtaisesti kaikki käsiteltävänä oleva aineisto. Lisäksi skriptit mahdollistavat usean tiedoston käsittelemisen samanaikaisesti, mikä parhaimmillaan nopeuttaa prosessointia huomattavasti. Prosessoinnin nopeus voi kuitenkin vaihdella huomattavasti käytetyn tietokoneen ominaisuuksien ja parametrien mukaan.

Tällä hetkellä skriptien valikoima on melko rajattu ja tehty lähinnä arkeologien tarpeita ajatellen. Valikoimaan lisätään mahdollisesti myöhemmin muita skriptejä, mutta voit yhtä hyvin jatkaa aineiston käsittelyä myös muilla ohjelmilla (esim. QGIS)

Käyttöohjeissa on pyritty antamaan mahdollisimman yksinkertaiset ja seikkaperäiset ohjeet, joita noudattamalla skriptejä on mahdollista käyttää ilman aiempaa kokemusta ohjelmoinnista tai komentorivin käytöstä. Myös skriptien käyttö on pyritty pitämään mahdollisimman yksinkertaisena ja yhtenäisenä.

# Esivalmistelut

## Python -ympäristön luominen

Skriptit tarvitsevat toimiakseen Python-ympäristön, johon on asennettu aineistojen käsittelyyn tarvittavat paketit (pdal, gdal, numpy, geopandas, rasterio). Alla on yksityiskohtiaset ohjeet python ympäristön luomiseen Anacondan avulla. 

- Asenna Anaconda https://docs.anaconda.com/anaconda/install/
- Käynnistä Anaconda prompt
- Tee uusi Python ympäristö komennolla:
  - conda create -n pdal -c conda-forge pdal gdal geopandas numpy rasterio affine

Tällä komennolla Anaconda luo uuden Python ympäristön nimeltä 'pdal' ja asentaa siihen tarvittavat paketit (pdal, gdal, geopandas, numpy). Hyväksy ympäristön luominen painamalla 'y'.

## Kansiorakenne ja aineiston järjestäminen
Jotta skripti toimisi oikein, käsiteltävät tiedostot tulee järjestää kansioihin tietyllä tavalla. Skripti olettaa, että aineistot on järjestetty työskentelykansion sisällä erillisiin kansioihin aineiston tyypin perusteella seuraavasti:
- lidar (laserkeilausaineisto -laz -tiedostoina)
- dem (korkeusmallit geotiffeinä)
- visualisoinnit (valmiit visualisoinnit)
- temp (väliaikaistiedostot)

Varsinaiset skriptit (eli .py -päätteiset tiedostot) tallenetaan suoraan työskentelykansioon.

Skriptit käsittelevät oletuksena kaiken kansioihin tallennetun aineiston (jolla on oletettu tiedostopääte). Tästä syystä työskentelykansiota ei kannata käyttää aineistojen säilyttämiseen, eli kopioi työskentelykansioon vain se aineisto, minkä haluat käsitellä.

Voit kopioida valmiin kansiorakenteen suoraan Githubista. Skriptit luovat tarvittaessa tuloksia ja väliaikaistiedostoja tarvittavat kansiot itse.

# Skriptien suorittaminen

Kun aloitat skriptien käytön, aktivoi aina ensin python-ympäristö ja aseta työskentelykansio.
- Avaa Anaconda prompt (ts. Anacondan oma 'komentorivi') ja aktivoi aiemmin luomasi python-ympäristö komennolla: conda activate pdal
- Aseta työskentelykansio komennolla: cd C:\lisää\oikea\polku\tähän
  - esim. cd C:\users\kayttajatunnus\lidar_prosessointi

Tämän jälkeen voit suorittaa skriptejä komennolla: python skriptin_nimi_tähän.py 

Tarkemmat ohjeet skriptien käyttöön ja mahdolliset lisävalinnat on esitetty alla.

## laz2dem.py

laz2dem.py tekee lidar/ -kansioon tallennetuista .laz päätteisistä tiedostoista pintamallit ja tallentaa ne kansioon dem/.

Skripti suoritetaan komennolla: 
   - python laz2dem.py

Skriptille voi antaa seuraavat valinnaiset parametrit:
- --buffer      (default=0)
  - Laserkeilaustiilten käsittelyssä käytettävä bufferi. Käytettäessä bufferia pintamallin muodostamiseen käytetään myös käsiteltävää tiiltä ympäröivät pisteet, jolloin myös pintamalleista tulee alkuperäistä laserkeilaustiiltä laajempia. Bufferin käytöstä on hyötyä esimerkiksi tiettyjen visualisointitekniikoiden kanssa (esim. TPI), jotta vältytään poikkeamilta käsitetävien tiilien reunoilla. Bufferin koko annetaan metreissä. Bufferin käyttö hidastaa jonkin verran käsittelyä.
- --cores       (default=4)
  - Rinnakkain käsiteltävien tiedostojen määrä. Tällä asetuksella voit vaikuttaa huomattavasti prosessoinnin nopeuteen. Rinnakkain käsiteltävien tiedostojen määrän tulisi olla korkeintaan yhtä suuri kuin tietokoneen loogisten suorittimien määrä, minkä voit tarkistaa esimerkiksi tehtävienhallinnasta. Huomaa kuitenkin, että tietokoneen ominaisuuksista riippuen maksimia pienempi rinnakkain käsiteltävien tiedostojen määrä voi olla kokonaisuutena nopeampi.
- --crs         (default=3067, ts. ETRS-TM35FIN / EPSG:3067)
  - Tällä asetuksella voit asettaa haluamasi koordinaattijärjestelmän. Koordinaattijärjestelmän asettamiseen käytetään EPSG-numerokoodia. 
- --resolution  (default=1)
  - Laserkeilausaineistosta tuotettavien rasterien resoluutio metreinä. Käytä desimaalierottimena pistettä.

Lisäparametrit annetaan varsinaisen komennon jälkeen, esim: python pdal_laz2dem.py --buffer=30 --cores=8 --resolution=0.5

Skriptin suorittamisen lopuksi skripti ilmoittaa käsittelyyn kuluneen ajan sekä yhden tiedoston käsittelyyn keskimäärin kuluneen ajan sekunteina. Voit käyttää ominaisuutta esimerkiksi asetusten vaikutusten testaamiseen.

laz2dem.py on hyödyntää laserkeilausaineiston käsittelyyn PDAL-kirjastoa: https://pdal.io/

## dem2tpi.py

dem2tpi.py laskee dem/ -kansioon tallennetuista .tif päätteisistä korkeusmalleista topographic position indexin (TPI) ja tallentaa sen uuteen kansioon. Uusi kansio nimetään TPI:n laskennassa käytettyjen parametrien perusteella.

TPI on hyödyllinen tekniikka lähiympäristöön korkeampien tai matalampien maastonmuotojen visualisointiin. Topographic position index lasketaan vertaamalla korkeusmallin jokaisen solun korkeutta sen ympäristön solujen korkeuksien keskiarvoon. Lähiympäristön tarkasteluun käytettävää sädettä muuttamalla TPI:n avulla voidaan korostaa hyvin eri kokoisia maastonmuotoja. Esimerkiksi 5 metrin sädettä käyttämällä TPI korostaa paikallisia mittakaavaltaan pieniä maastonmuotoja, mutta ei juurikaan reagoi suurempiin maastonmuotoihin. Vastaavasti suurempaa sädettä käytettäessä TPI korostaa mittakaavaltaan suurempia maastonmuotoja. 

Skripti suoritetaan komennolla: 
   - python dem2tpi.py --radius=7

Pakolliset parametrit
- --radius
  - määrittää TPI:n laskentaan käytettävän säteen metreinä. Esimerkiksi arkeologisesti kiinnostavien pinnanmuotojen visualisointiin radius on tyypillisesti hyvä asettaa välille 5-15.
  - Huomioithan, että suurempi radius kasvattaa huomattavasti prosessointiin kuluvaa aikaa.
  - HUOM! Tämä versio skriptistä soveltuu lähinnä suhteellisen pienten ja paikallisten korkeuserojen visualisointiin, koska tulokset skaalataan vakioidulla kaavalla tietylle vaihteluvälille. 

Skriptille voi antaa seuraavat valinnaiset parametrit:
- --cores       (default=4)
  - Rinnakkain käsiteltävien tiedostojen määrä. Tällä asetuksella voit vaikuttaa huomattavasti prosessoinnin nopeuteen. Rinnakkain käsiteltävien tiedostojen määrän tulisi olla korkeintaan yhtä suuri kuin tietokoneen loogisten suorittimien määrä, minkä voit tarkistaa esimerkiksi tehtävienhallinnasta. Huomaa kuitenkin, että tietokoneen ominaisuuksista riippuen maksimia pienempi rinnakkain käsiteltävien tiedostojen määrä voi olla kokonaisuutena nopeampi.
- --crs         (default=3067, ts. ETRS-TM35FIN / EPSG:3067)
  - Tällä asetuksella voit asettaa haluamasi koordinaattijärjestelmän. Koordinaattijärjestelmän asettamiseen käytetään EPSG-numerokoodia.
 
Skriptin suorittamisen lopuksi skripti ilmoittaa käsittelyyn kuluneen ajan sekä yhden tiedoston käsittelyyn keskimäärin kuluneen ajan sekunteina. Voit käyttää ominaisuutta esimerkiksi asetusten vaikutusten testaamiseen.

dem2tpi.py perustuu Zoran Čučkovićin numpy-kirjastoa hyödyntävään tapaan laskea TPI. Oleellisimpana erona alkuperäiseen tässä esitetty versio skriptistä mahdollistaa suoraan usean tiedoston rinnakkaisen käsittelyn ja skaalaa tulokset vakioidulla kaavalla kokonaisluvuiksi väliltä +/- 100.




















