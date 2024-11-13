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
- Tee uusi Python ympäristö seuraavalla komennolla:
```shell
conda create -n lidar -c conda-forge pdal gdal geopandas numpy rasterio affine tqdm
```

Tällä komennolla Anaconda luo uuden Python ympäristön nimeltä 'lidar' ja asentaa siihen tarvittavat paketit (pdal, gdal, geopandas, numpy & tqdm). Hyväksy ympäristön luominen painamalla 'y'.

## Kansiorakenne ja aineiston järjestäminen
Jotta skripti toimisi oikein, käsiteltävät tiedostot tulee järjestää kansioihin tietyllä tavalla. Skripti olettaa, että aineistot on järjestetty työskentelykansion sisällä erillisiin kansioihin aineiston tyypin perusteella seuraavasti:
- lidar (laserkeilausaineisto -laz -tiedostoina)
- dem (korkeusmallit geotiffeinä)

Varsinaiset skriptit (eli .py -päätteiset tiedostot) tallenetaan suoraan työskentelykansioon.

Skriptit käsittelevät oletuksena kaiken kansioihin tallennetun aineiston (jolla on oletettu tiedostopääte). Tästä syystä työskentelykansiota ei kannata käyttää aineistojen säilyttämiseen, eli kopioi työskentelykansioon vain se aineisto, minkä haluat käsitellä. Tuloksia sekä mahdollisia väliaikaistiedostoja varten tarvittavat kansiot luodaan lähtökohtaisesti automaattisesti.

Voit kopioida valmiin kansiorakenteen suoraan Githubista. Skriptit luovat tarvittaessa tuloksia ja väliaikaistiedostoja tarvittavat kansiot itse.

# Skriptien suorittaminen

Kun aloitat skriptien käytön, aktivoi aina ensin python-ympäristö ja aseta työskentelykansio.
- Avaa Anaconda prompt (ts. Anacondan oma 'komentorivi') ja aktivoi aiemmin luomasi python-ympäristö komennolla:
```shell
conda activate lidar
```
- Aseta työskentelykansio komennolla cd C:\lisää\oikea\polku\tähän, esim:
```shell
cd C:\users\kayttajatunnus\lidar_prosessointi
```

Tämän jälkeen voit suorittaa skriptejä komennolla: python skriptin_nimi_tähän.py 

Tarkemmat ohjeet skriptien käyttöön ja mahdolliset lisävalinnat on esitetty alla.

## laz2dem.py - Pintamallien teko laserkeilausaineistosta

laz2dem.py tekee lidar/ -kansioon tallennetuista .laz päätteisistä tiedostoista pintamallit ja tallentaa ne kansioon dem/.

Skripti suoritetaan komennolla: 
```shell
python laz2dem.py
```

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

## dem2rvt.py - Pintamallien visualisointi Relief Visualization Toolboxin (RVT) avulla

dem2rvt.py mahdollistaa erilaisten visualisointien tuottamisen Relief Visualization Toolboxin (RVT) avulla. RVT tarjoaa erittäin kattavan valikoiman erilaisia visualisointitekniikoita, jotka on listattu alla. Lisätietoa RVT:stä ja RVT:n avulla tehtävistä visualisoinneista: https://rvt-py.readthedocs.io/en/latest/index.html

RVT Python library, Žiga Kokalj, Žiga Maroh, Krištof Oštir, Klemen Zakšek and Nejc Čož, 2022. (ZRC SAZU and University of Ljubljana)

Esimerkkejä dem2rvt.py käytöstä:

Yksittäisen visualisoinnin tekeminen
```shell
python dem2rvt.py --visualisoinnit=hillshade
```
Useampien visualisointien tekeminen yhdellä komennolla on mahdollista käyttäen erottimena puolipistettä
```shell
python dem2rvt.py --visualisoinnit=slope;hillshade
```
Avainsanalla 'kaikki' voi tehdä yhdellä komennonnolla kaikki RVT:n mahdollistamat visualisoinnit
```shell
python dem2rvt.py --visualisoinnit=kaikki
```

### Vinovalovarjoste / hillshade

Laskee korkeusmallista vinovalovarjosteen ja tallentaa tuloksen kansioon hillshade/

```shell
python dem2rvt.py --visualisoinnit=hillshade
```

### Monisuuntainen vinovalovarjoste / multiple direction hillshade (mdhs)
Laskee korkeusmallista useasta suunnasta valaistun vinovalovarjosteen ja tallentaa sen kansioon multi_hillshade/

```shell
python dem2rvt.py --visualisoinnit=multi_hillshade
python dem2rvt.py --visualisoinnit=mdhs
```

### Rinteenkaltevuus / slope
Laskee korkeusmallista rinteenkaltevuuden (slope) ja tallentaa sen kansioon slope/

```shell
python dem2rvt.py --visualisoinnit=slope
```

### Simple local relief model (slrm)
Laskee korkeusmallista simple relief modelin (slrm) ja tallentaa sen kansioon simple_relief_model. Slrm lasketaan vertaamalla jokaisen solun korkeutta sitä ympäröivien solujen korkeuksien keskiarvoon halutulla säteellä. 

```shell
python dem2rvt.py --visualisoinnit=simple_local_relief_model
python dem2rvt.py --visualisoinnit=slrm
```

### Multi-scale relief model (msrm)
Laskee korkeusmallista multi-scale relief modelin (msrm) ja tallentaa sen kansioon multi-scale_relief_model.

```shell
python dem2rvt.py --visualisoinnit=multi-scale_relief_model
python dem2rvt.py --visualisoinnit=msrm
```

### Sky-view factor (svf) 
Laskee korkeusmallista sky-view factorin tai anisotropic sky-view factorin.

Sky-view factor tarkempi kuvaus ja viittaukset: Zakšek, K., Oštir, K., Kokalj, Ž. 2011. Sky-View Factor as a Relief Visualization Technique. Remote Sensing 3: 398-415 https://doi.org/10.3390/rs3020398 

```shell
#sky-view factor
python dem2rvt.py --visualisoinnit=sky-view_factor
python dem2rvt.py --visualisoinnit=svf
#anisotropic sky-view factor
python dem2rvt.py --visualisoinnit=anisotropic_sky-view_factor
python dem2rvt.py --visualisoinnit=asvf
```

### Topographic openness
Laskee pintamallista topographic positiivisen- ja negatiivisen topographic opennessin ja tallentaa ne erillisiin kansioihin.

```shell
python dem2rvt.py --visualisoinnit=openness
```
### Multi-scale topographic position (mstp)
Laskee pintamallista multi-scale topographic positionin (mstp).

```shell
python dem2rvt.py --visualisoinnit=multi-scale_topographic_position
python dem2rvt.py --visualisoinnit=mstp
```

### Local dominance
Laskee pintamallista local dominancen.

```shell
python dem2rvt.py --visualisoinnit=dominance
```

## dem2tpi.py - Topographic position index

dem2tpi.py laskee dem/ -kansioon tallennetuista .tif päätteisistä korkeusmalleista topographic position indexin (TPI) ja tallentaa sen uuteen kansioon. Uusi kansio nimetään TPI:n laskennassa käytettyjen parametrien perusteella.

TPI on hyödyllinen tekniikka lähiympäristöön korkeampien tai matalampien maastonmuotojen visualisointiin. Topographic position index lasketaan vertaamalla korkeusmallin jokaisen solun korkeutta sen ympäristön solujen korkeuksien keskiarvoon. Lähiympäristön tarkasteluun käytettävää sädettä muuttamalla TPI:n avulla voidaan korostaa hyvin eri kokoisia maastonmuotoja. Esimerkiksi 5 metrin sädettä käyttämällä TPI korostaa paikallisia mittakaavaltaan pieniä maastonmuotoja, mutta ei juurikaan reagoi suurempiin maastonmuotoihin. Vastaavasti suurempaa sädettä käytettäessä TPI korostaa mittakaavaltaan suurempia maastonmuotoja. 

Skripti suoritetaan komennolla: 
```shell
python dem2tpi.py --radius=7
```

Pakolliset parametrit
- --radius
  - määrittää TPI:n laskentaan käytettävän säteen metreinä. Esimerkiksi arkeologisesti kiinnostavien pinnanmuotojen visualisointiin radius on tyypillisesti hyvä asettaa välille 5-15.
  - Huomioithan, että suurempi radius kasvattaa prosessointiin kuluvaa aikaa.
  - HUOM! Tämä versio skriptistä soveltuu lähinnä suhteellisen pienten ja paikallisten korkeuserojen visualisointiin, koska tulokset skaalataan vakioidulla kaavalla tietylle vaihteluvälille. Muihin tarpeisiin on parempi käyttää RVT:n simple local relief model -visualisointia, joka on käytännössä sama asia.

Skriptille voi antaa seuraavat valinnaiset parametrit:
- --cores       (default=4)
  - Rinnakkain käsiteltävien tiedostojen määrä. Tällä asetuksella voit vaikuttaa huomattavasti prosessoinnin nopeuteen. Rinnakkain käsiteltävien tiedostojen määrän tulisi olla korkeintaan yhtä suuri kuin tietokoneen loogisten suorittimien määrä, minkä voit tarkistaa esimerkiksi tehtävienhallinnasta. Huomaa kuitenkin, että tietokoneen ominaisuuksista riippuen maksimia pienempi rinnakkain käsiteltävien tiedostojen määrä voi olla kokonaisuutena nopeampi.
- --crs         (default=3067, ts. ETRS-TM35FIN / EPSG:3067)
  - Tällä asetuksella voit asettaa haluamasi koordinaattijärjestelmän. Koordinaattijärjestelmän asettamiseen käytetään EPSG-numerokoodia.
 
Skriptin suorittamisen lopuksi skripti ilmoittaa käsittelyyn kuluneen ajan sekä yhden tiedoston käsittelyyn keskimäärin kuluneen ajan sekunteina. Voit käyttää ominaisuutta esimerkiksi asetusten vaikutusten testaamiseen.

dem2tpi.py perustuu Zoran Čučkovićin numpy-kirjastoa hyödyntävään tapaan laskea TPI (https://landscapearchaeology.org/2021/python-tpi/). Oleellisimpana erona alkuperäiseen tässä esitetty versio skriptistä mahdollistaa suoraan usean tiedoston rinnakkaisen käsittelyn ja skaalaa tulokset vakioidulla kaavalla kokonaisluvuiksi väliltä +/- 100.




















