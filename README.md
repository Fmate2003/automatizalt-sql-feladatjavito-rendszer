# Automatizált SQL feladatjavító rendszer

A program egy vizsgamappából olvassa be a javítókulcsot és a hallgatók SQL-megoldásait. A referencia és a beadás külön adatbázis-állapotban fut. A javító a lekérdezések eredményét, adat- vagy táblamódosításnál pedig a várt és a tényleges végállapotot veti össze. A pontlapon feladatonként látszik, mely feltételek teljesültek, hol volt eltérés, és hány pontot vont le ezért a javító.

## Futtatás és adatbázis-kapcsolat

A bemutató Python 3.12-t és PostgreSQL-t használ. Az adminisztrátor hozzon létre egy elkülönített, `sql_grader_demo` nevű adatbázist, és ott egyszer futtassa az előkészítő SQL-fájlt. Ez hozza létre a `sql_runner` futtatói fiókot és a korlátozott `sql_student` szerepkört. A kapcsolat címét, portját és időkorlátait a `config.json` tartalmazza. A futtatói jelszót a `SQLGRADER_DB_PASSWORD` környezeti változóval lehet megadni. [PostgreSQL előkészítés](database/postgresql_init.sql) · [Kapcsolati beállítások](config.json)

### Linux és WSL

A parancsokat a projekt gyökérmappájából futtasd. Windows alatt használható hozzá a Windows Subsystem for Linux (WSL) terminálja is.

~~~bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m sqlgrader minta/postgresql
~~~

### Windows PowerShell

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m sqlgrader minta/postgresql
~~~

A rövid PostgreSQL-minta két beadásának várt eredménye `40/50` és `50/50`. A teljes, 30 fős próba leadási formátumban is futtatható, opcionálisan mesterséges intelligenciával (AI) készített visszajelzéssel. Az `--ai` kapcsolóhoz a helyi Ollama és a beállított modell szükséges.

~~~bash
.venv/bin/python -m sqlgrader probak/zh-30-diak --output eredmenyek/bemutato --spec-output --ai
~~~

| Paraméter | Szerepe |
| --- | --- |
| `vizsgamappa` | A kötelező bemeneti útvonal. Itt van a javítókulcs, a tesztadat és a beadott SQL. |
| `--config fájl` | A kapcsolati és futtatási beállítások fájlja. Alapértéke `config.json`. |
| `--output mappa` | A kimenet gyökérmappája. Alapértéke `eredmenyek`, minden futás saját időbélyeges almappát kap. |
| `--spec-output` | Tabulátorral tagolt `osszesito.xls` fájlt ír a specifikáció szerint. |
| `--ai` | A pontozás után elindítja a helyi AI-visszajelzést. |
| `-d`, `--debug` | Részletes naplózás, a projektmodulok függvényhívásaival. |
| `--help`, `--version` | A használható paramétereket vagy a program verzióját mutatja. |

Az adatbázis-kapcsolatot, az SQL ellenőrzését és a futtatást külön adapter kezeli. Az `engine` beállítás választja ki az adaptert, a fő modul pedig annak közös műveleteit hívja. PostgreSQL-hez a program a `psycopg2` Python-illesztőprogramot használja. Az Oracle 12c-hez külön adapter, mintafeladatsor és beállítási útmutató tartozik. A végleges bemutató PostgreSQL-en futott. Az Oracle-adapter élő futása külön ellenőrzést igényel. [Adatbázis-modul](sqlgrader/database.py) · [Oracle 12c beállítása](docs/ORACLE.md)

## Vizsgamappa és javítókulcs

A `solution.sql` a javítókulcs rögzített neve. A `--pregen` fejléc a kezdő adatbázist felépítő fájlra mutat. Ha a fejléc hiányzik, a program a `create_db.sql` fájlt keresi. A `--case` fejléc egy tesztesetet nevez meg, és megadhat hozzá kiegészítő adatfájlt. A próbavizsgán a `base` az alapadatokat, az `edge` a kiegészített adatkészletet jelöli. A javítókulcs és az általa hivatkozott előkészítő fájlok kimaradnak a beadások közül.

| Feladatblokk | Tartalma |
| --- | --- |
| `--2 comparetype` | A feladat típusa, maximuma, részpontjai és egyéb szabályai JSON-formátumban, vagyis kulcs–érték párokkal leírva. |
| `--2 solution` | A referenciamegoldás SQL-utasítása. |
| `--2 solutionpre` | Opcionális előkészítő SQL a referenciamegoldás futtatása előtt. |
| `--2 studentpre` | Opcionális előkészítő SQL a beadott megoldás futtatása előtt. |

A beadás UTF-8 kódolású `.sql` fájl. A feladatok előtt meg kell adni a nevet és a hat karakterből álló, betűket és számjegyeket tartalmazó Neptun-kódot. A feladatazonosító lehet szám vagy számból és betűből álló jelölés, például `2` vagy `1a`. A következő feladatfejléc zárja le a választ. A válasz több sorból állhat, üresen maradhat, és tartalmazhat szokásos SQL-megjegyzéseket. Feladatonként egy SQL-utasítás adható meg. Az alábbi mintában az `1b` feladat válasza üres. [Bemeneti formátum](docs/FORMATUM.md)

~~~sql
--név: Minta Hallgató
--neptun: ABC123

--1a
SELECT id
FROM customers
-- Az eredmény azonosító szerint rendezve.
ORDER BY id;

--1b
~~~

## Mi történik egy javítási futásban?

1. A fő modul beolvassa a parancssori paramétereket, megnyitja a naplót, és betölti a konfigurációt.
2. A javítókulcs beolvasása és a beadások összegyűjtése után ellenőrzi az adatbázis-kapcsolatot és a futtatói szerepkört.
3. Hallgatónként végigmegy a feladatokon. A referencia és a beadás külön kezdőállapotot kap. Tesztesetenként a kezdő SQL, a tesztadat és a megfelelő előkészítő blokk fut le a megoldás előtt. PostgreSQL-en minden futtatáshoz saját ideiglenes séma készül. A kapcsolat lezárásakor az adatbázis visszagörgeti a változásokat.
4. A javító a feladat típusához választ összehasonlítást, és a kulcs feltételei alapján kiszámolja a pontokat. A kimeneti modul elkészíti az egyéni pontlapokat és a csoportösszesítőt. Az AI-visszajelzés ezután indul, ha a futtatásnál szerepel az `--ai` kapcsoló.

| Modul | Feladata |
| --- | --- |
| [`__main__.py`](sqlgrader/__main__.py) és [`inputs.py`](sqlgrader/inputs.py) | Futásvezérlés, a kulcs és a beadások beolvasása. |
| [`database.py`](sqlgrader/database.py) és az adapterek | Kapcsolat, SQL-ellenőrzés, futtatás és takarítás. |
| [`grading.py`](sqlgrader/grading.py), [`comparison.py`](sqlgrader/comparison.py) és [`rubric.py`](sqlgrader/rubric.py) | Feladattípus szerinti összehasonlítás, részpontok és állapotok. |
| [`output.py`](sqlgrader/output.py) | Pontlap, feladatsor, fejléc, összesítő és átlagok. |
| [`ai.py`](sqlgrader/ai.py) és [`feedback.py`](sqlgrader/feedback.py) | Ellenőrzött tényekből készülő visszajelzés és helyi AI-pontjavaslat. |

## Javítási szabályok

A `SELECT` feladatnál az oszlopok és a sorok száma, a cellák tartalma és a sorok ismétlődése is számít. A `column_names` az oszlopneveket és azok sorrendjét, az `ordered` az eredménysorok sorrendjét teszi kötelezővé. A `case_insensitive` beállítással a szöveges értékek kis- és nagybetűktől függetlenül hasonlíthatók össze. PostgreSQL-en az oktató a külső `ORDER BY` záradékot (`require_order_by`), illetve a `LOWER` vagy `UPPER` használatát (`required_functions`) külön is előírhatja.

`INSERT`, `UPDATE` és `DELETE` esetén a pontozás a beszúrt, módosított vagy eltávolított sorokat vizsgálja. A végállapot összehasonlítása a többi ellenőrzött táblára és nézetre is kiterjed. A `CREATE TABLE` és `CREATE VIEW` feladatnál az objektum neve, típusa, oszlopai és adattípusai ellenőrizhetők. Táblánál a támogatott megszorításokért, nézetnél a visszaadott sorokért is járhat részpont. A `DROP TABLE` és `DROP VIEW` feladatnál a kiválasztott objektum eltűnését és a többi objektum állapotát lehet pontozni. A `CREATE USER` és a `GRANT` feladatokat a program kézi ellenőrzésre jelöli, az eredményt az oktató hagyja jóvá.

A `points` mező a feladat maximuma. A `partial` értéke automatikus elosztás (`auto`), teljes egyezéshez kötött pontozás (`off`) vagy a kulcsban felsorolt egyedi feltételek. Egyedi elosztásnál a feltételek egész pontértékének összege megegyezik a maximummal, és szerepel köztük a teljes egyezést jelölő `exact` feltétel.

Az egyező soroknál és adatváltozásoknál a javító arányosan pontoz. Az egyező elemek számát elosztja a várt és a kapott mennyiség közül a nagyobbal, így a hiányzó és a felesleges sor is csökkentheti a pontot. Az arányt megszorozza az adott feltétel pontértékével, és lefelé kerekít. Több adatkészletnél minden feltételhez a legalacsonyabb kapott részpont kerül a pontlapra. A levonás a feltétel maximuma és a megítélt részpont különbsége. [Részpontozás](docs/RESZPONTOZAS.md)

Egy 4 pontos soregyezési feltételnél előfordulhat, hogy az alapadatokon minden sor egyezik, a bővített adatokon viszont az elvárt öt sorból három szerepel a beadásban. Ha többletsor sincs, a bővített próba értéke 4 × 3/5, vagyis 2,4, ami lefelé kerekítve 2 pont. Ennél a feltételnél így 2 pont kerül a pontlapra.

### A végleges próbavizsga pontozása

A tíz feladat maximuma 2 és 9 pont közé esik. Összesen 50 pont szerezhető. Az alábbi bontás a végleges `solution.sql` egyedi szabályait követi. [Feladatlap](probak/zh-30-diak/FELADATLAP.md) · [Javítókulcs](probak/zh-30-diak/solution.sql)

| Feladat | Max. | Miért jár pont? | Hol veszíthet pontot a beadás? |
| --- | ---: | --- | --- |
| 1. Termékek szűrése (`SELECT`) | 2 | 1 pont az egyező sorokra, 1 a teljes egyezésre. | Hiányzó, hibás vagy felesleges sor esetén az 1 pontos soregyezési feltétel lefelé kerekítve 0 pontot ér. A teljes egyezésért járó pont is kiesik. |
| 2. Rendezés ár és azonosító szerint (`SELECT`) | 3 | 1 pont az oszlopszámra, 1 az egyező sorokra, 1 a teljes egyezésre. | Ha az adatok helyesek, de a sorrend eltér, csak a teljes egyezés pontja vész el. Az eredmény 2/3 pont. |
| 3. Rendelésszám vevőnként (`SELECT`) | 5 | 1 pont az oszlopszámra, legfeljebb 3 az egyező sorokra, 1 a teljes egyezésre. | A kihagyott, rendelés nélküli vevő vagy a hibás darabszám rontja a soregyezést. |
| 4. Rendelési érték számítása (`SELECT`) | 6 | 1 pont az oszlopszámra, legfeljebb 4 az egyező sorokra, 1 a teljes egyezésre. Igazolt szintaktikai hibánál külön szabály alapján 1 próbálkozási pont adható. | A hibás mennyiség–ár számítás vagy csoportosítás csökkenti a soregyezés pontját. A próbálkozási pont a szintaktikai hibás beadás eredménye, a normál részpontokhoz nem adódik hozzá. |
| 5. Vevő beszúrása (`INSERT`) | 4 | 1 pont a megfelelő azonosítóra, 1 az adott azonosítóhoz tartozó névre, 1 a városra, 1 a teljes egyezésre. | A hibás mező saját pontja elmarad. A név és a város a megfelelő azonosítóhoz kötött. Egy másik objektum megváltoztatása a teljes egyezés pontjába kerülhet. |
| 6. A 100 alatti árak emelése (`UPDATE`) | 5 | Legfeljebb 3 pont az egyező adatváltozásokra, 1 a változások darabszámára, 1 a teljes egyezésre. | A rosszul kiválasztott vagy hibás összeggel módosított sor csökkenti az egyezést. Eltérő változásszámnál az arra járó pont is elmarad. |
| 7. Törölt rendelések tételeinek eltávolítása (`DELETE`) | 6 | Legfeljebb 4 pont az egyező törlésekre, 1 a többi objektum elvárt állapotára, 1 a teljes egyezésre. | A kihagyott vagy tévesen törölt tétel csökkenti az egyezést. A rendelések módosítása a többi objektumért járó pontot is érinti. |
| 8. Tábla megszorításokkal (`CREATE TABLE`) | 9 | 1 pont a megfelelő objektumra, 1 az oszlopokra és sorrendjükre, 2 az adattípusokra és oszloptulajdonságokra, 4 a megszorítások egyezésére, 1 a teljes egyezésre. | A hiányzó kulcs vagy `CHECK`-feltétel miatt a megszorításokért járó 4 pont elmarad. A hibás oszloptulajdonság az adattípusokat és tulajdonságokat vizsgáló részpontot is érintheti. |
| 9. Fizetett rendelések nézete (`CREATE VIEW`) | 7 | 1 pont a megfelelő objektumra, 1 az oszlopokra és sorrendjükre, legfeljebb 4 a nézet egyező soraira, 1 a teljes egyezésre. | A rossz szűrés miatt hiányzó vagy többletsor csökkenti a nézet eredményéért járó pontot. |
| 10. Ideiglenes tábla törlése (`DROP TABLE`) | 3 | 1 pont a `temp_import` eltávolítására, 1 a többi objektum elvárt állapotára, 1 a teljes egyezésre. | Elmaradt törlésnél a törlésért járó pont kiesik. A többi objektumot érintő eltérés az arra járó pontot és a teljes egyezést is érintheti. |

Ha a referencia a célobjektumon változást vár, a többi objektum elvárt állapotáért akkor járhat pont, ha a beadás a célobjektumot is megváltoztatta. Ez a 7. és a 10. feladat egyik feltétele.

Üres válasz vagy az adott feladatban tiltott utasítás esetén 0 pont jár. A szintaktikai hibára adható pontot a `syntax_credit` mező határozza meg, amely ebben a vizsgában a 4. feladatnál 1, a többi feladatnál 0. A beadás futási hibája vagy adatbázis-szintű időtúllépése az érintett teszteseten 0 részpontot eredményez. Ha a referencia, a tesztadat vagy a futtatókörnyezet hibája miatt a javító nem tud pontot megállapítani, függőben jelöli az eredményt.

## Opcionális AI-visszajelzés

Az opcionális visszajelzés telepített Ollamát használ. Az Ollama a gépen futtatja a nyelvi modellt, amelyet a javító egy alkalmazásprogramozási felületen (API) ér el. A minta a `qwen3.5:2b-q4_K_M` modellt és a `http://127.0.0.1:11434/api/chat` címet használja. A modell nevét és a kérés időkorlátját a konfiguráció tartalmazza.

A modell megkapja az értékelési útmutatót, az adott feladat maximumát, a mért pontot és az igazolt eltéréseket. A hallgató neve, Neptun-kódja, beadott SQL-je és a referenciamegoldás SQL-szövege a javítóban marad. A válasz feladatonként JSON-formátumú. Az opcionális ténykiemelés, a 0 és a feladatmaximum közötti egész pontjavaslat, valamint a rövid indoklás formátumát a program ellenőrzi. A megállapított pont a szabályalapú ellenőrzésből származik. Az AI pontjavaslata és indoklása az oktató külön jelentésében szerepel. [AI-értékelési útmutató](docs/AI_PONTOZASI_UTMUTATO.md)

Ha a modell kérése időtúllépéssel végződik vagy a válasz használhatatlan, a pontlap a mért eredményekből kap magyarázatot. Megszakítás után a mentett pontlapokból lehet folytatni. A `--ujraproba` azokhoz a feladatokhoz kér új javaslatot, amelyeknél az AI használható, de nincs érvényes mentett javaslat.

~~~bash
.venv/bin/python -m sqlgrader.feedback "eredmenyek/bemutato/IDOBELYEG"
~~~

Külső szolgáltatóval az AI-modul bővíthető. Egy ilyen illesztésben például OpenAI-modell hívható meg a szolgáltató API-ján keresztül, API-kulccsal.

## Kimenetek, naplózás és ellenőrzés

| Fájl vagy könyvtár | Mit lehet benne ellenőrizni? |
| --- | --- |
| `<Név>_<Neptun>.txt` | Az összpont, a feladatok azonosítója, pontja és maximuma, a teszteredmények és a levont részpontok. Az `S` jelölés szabályalapú pontot jelent. |
| `<Név>_<Neptun>.json` | Az egyéni pontlap géppel feldolgozható változata. A folytatás és a futások összehasonlítása ezeket a fájlokat használja. |
| `osszesito.xls` | A név, a Neptun-kód és az összpont után feladatonkénti oszlopok következnek. A hallgatói sorok után üres sor és az `Átlagok` sor áll. A végleges próbában a `--spec-output` tabulátorral tagolt, UTF-8 kódolású fájlt ír. |
| `osszesito.xlsx` | Az alapértelmezett futáskor elkészülő Excel-munkafüzet. Az alapértelmezett `osszesito.xls` ugyanazokat az adatokat tartalmazza pontosvesszővel tagolva. |
| `ai-folyamat/` | Az oktatónak szóló AI-javaslatok és a folytatáshoz szükséges mentések. |
| `logs/` | Ezredmásodperc pontosságú, időbélyeges futási naplók. |

A csoportátlagokba a megállapított pontszámok kerülnek be. A napló `INFO` szinten rögzíti az indulást, a paramétereket, a beadások fájlnevét, az ellenőrzés állapotát és a befejezést. Az `ERROR` bejegyzésekkel követhetők például a formátumhibák, az időtúllépések és a külső szolgáltatások hibái. A `--debug` a projekt függvényhívásait is naplózza.

A futás korlátai a konfigurációban állíthatók be. A `statement_ms` az egy SQL-utasításra jutó időt ezredmásodpercben, a `task_seconds` a feladat idejét és a `batch_seconds` a pontozási szakasz időkeretét másodpercben adja meg. A `max_rows` a beolvasható sorok számát korlátozza. A tárolt eljárások futtatása kívül esik a támogatott beadási formákon.

A végleges PostgreSQL-próbában a program 30 beadást és 300 feladateredményt ellenőrzött. Az egyéni pontlapok egyeztek a tabulátoros összesítővel. Az átlag 34,93/50 lett, 255 feladathoz készült külön AI-pontjavaslat.

Az egységtesztek a projekt gyökeréből futtathatók.

~~~bash
.venv/bin/python -m unittest discover -s tests -v
~~~

Két azonos javítókulccsal készült futás a `python -m sqlgrader.verify RÉGI_MAPPA ÚJ_MAPPA` paranccsal vethető össze. Az eszköz az összpontot, a feladatonkénti pontot és maximumot, valamint az állapotot ellenőrzi. [Ellenőrzési jegyzet](docs/ELLENORZES.md) · [Megfelelés a specifikációhoz](docs/SPECIFIKACIO.md)

## Gyakorlati haszon

Egy többtucatnyi beadásból álló SQL-dolgozatnál az oktató ugyanazt a pontozást és ugyanazokat a tesztadatokat alkalmazhatja mindenkire. A javító azonos eredményt adó, eltérően megírt lekérdezéseket is el tud fogadni, ha teljesülnek a feladat előírt feltételei. Egy vitatott pontnál az egyéni lapon visszakereshető, melyik adatkészleten tért el a megoldás és melyik feltétel miatt csökkent a pont.

A hallgató látja, mit érdemes javítania a saját megoldásán. Az oktató a feladatonkénti átlagokból és a pontlapokból azt is meg tudja nézni, mely hibák tértek vissza több beadásban. Ha például többen kihagyják az összesítésből a rendelés nélküli vevőket, a következő gyakorlaton külön elő lehet venni ezt az esetet.
