# lidar_prosessointi

Tähän on koottu kokoelma skriptejä LiDAR -aineistojen käsittelyyn ilmaisilla avoimen lähdekoodin työkaluilla (esim. PDAL).

Skriptit on tehty ensisijaisesti arkeologien tarpeisiin, mutta soveltuvat sellaisenaan tai muokattuna muihinkin tarkoituksiin.

Skriptit on laadittu erityisesti suurien tiedostomäärien käsittelyä ajatellen - eli yhdellä komennolla käsitellään lähtökohtaisesti koko käsiteltävänä oleva aineisto. Niitä ei kuitenkaan ole erityisemmin optimoitu suorituskykyä ajatellen, joten tietyt skriptit ja työvaiheet eivät välttämättä ole erityisen nopeita. Osasta skriptejä on olemassa rinnakkaisprosessoinnin mahdollistavat versiot mikä voi nopeuttaa käsittelyä merkittävästikin.

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

Voit kopioida valmiin kansiorakenteen suoraan Githubista.

# Skriptien suorittaminen

## Ennen aloittamista
- Avaa Anaconda prompt (ts. Anacondan oma 'komentorivi') ja aktivoi aiemmin luomasi python-ympäristö komennolla: conda activate pdal
- Aseta työskentelykansio komennolla: cd C:\lisää\oikea\polku\tähän (esim. cd C:\users\kayttajatunnus\lidar_prosessointi)

Nämä komennot täytyy antaa joka kerta uudestaan kun aloitat skriptien käytön.









