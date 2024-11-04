# lidar_prosessointi

Kokoan tähän joitakin hyödyllisiä skriptejä LiDAR -aineistojen käsittelyyn ilmaisilla avoimen lähdekoodin työkaluilla (esim. PDAL).

Skriptit on tehty ensisijaisesti arkeologien tarpeisiin, mutta soveltuvat sellaisenaan tai muokattuna muihinkin tarkoituksiin.

Skriptit on laadittu suurien tiedostomäärien käsittelyä ajatellen - eli yhdellä komennolla käsitellään lähtökohtaisesti kaikki käsiteltävänä oleva aineisto.  Skriptit mahdollistavat usean tiedoston käsittelyn samanaikaisesti, mikä jonkin verran nopeuttaa prosessointia. 

Käyttöohjeissa on pyritty antamaan mahdollisimman yksinkertaiset ja seikkaperäiset ohjeet, joita noudattamalla skriptejä on mahdollista käyttää ilman aiempaa kokemusta ohjelmoinnista tai komentorivin käytöstä. 

# Esivalmistelut

## Python -ympäristön luominen

Skriptit tarvitsevat toimiakseen Python-ympäristön, johon on asennettu aineistojen käsittelyyn tarvittavat paketit (pdal). Alla on yksityiskohtiaset ohjeet python ympäristön luomiseen Anacondan avulla. 

- Asenna Anaconda https://docs.anaconda.com/anaconda/install/
- Käynnistä Anaconda prompt
- Tee uusi Python ympäristö komennolla: conda create -n pdal pdal geopandas numpy
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
- Aseta työskentelykansio komennolla: cd C:\lisää\oikea\polku\tähän (esim. cd C:\users\kayttajatunnus\lidar_prosessointi)

Tämän jälkeen voit suorittaa skriptejä komennolla: python skriptin_nimi_tähän.py 

Osa skripteistä mahdollistaa oletusasetusten muuttamisen antamalla skriptille valinnaisia argumentteja. Argumentit kirjoitetaan kometoriville varsinaisen komennon perään. 

Tarkemmat ohjeet skriptien käyttöön ja mahdolliset lisävalinnat on esitetty alla.

## pdal_laz2dem.py

pdal_laz2dem.py tekee lidar/ -kansioon tallennetuista .laz päätteisistä tiedostoista pintamallit ja tallentaa ne kansioon dem/.

Skripti suoritetaan komennolla: python pdal_laz2dem.py

Skriptille voi antaa seuraavat valinnaiset parametrit, jotka vaikuttavat skriptin toimintaan ja pintamallien ominaisuuksiin.
- --buffer      (default=0)
- --cores       (default=4)
- --crs         (default=3067, ts. ETRS-TM35FIN / EPSG:3067)
- --resolution  (default=1)













