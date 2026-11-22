# Megfelelés a tanári specifikációhoz

A Word-dokumentum V1.0 és a tanári kiegészítés alapján. Ahol a
kiegészítés enyhíti az eredeti követelményt, ezt külön jelezzük.

| Tanári elvárás | Állapot és döntés |
| --- | --- |
| Operációs rendszertől független program | A program Pythonból indul, pathlib útvonalakat, UTF-8 fájlokat és mindkét rendszeren használható spawn munkafolyamatot alkalmaz. Külön Windows és Linux egységteszt-folyamat készült, de natív Windowsos adatbázisfutást nem végeztünk itt. |
| Oracle 12c vagy a későbbi engedmény szerint PostgreSQL psycopg2-vel | PostgreSQL psycopg2 az ellenőrzött bemutatóplatform. A külön Oracle-adapter megmaradt; élő Oracle 12c nincs igazolva. |
| Paraméterezhető SQL kapcsolat, külön adapter | A konfiguráció a hostot, portot, futtatási időket és modellbeállítást tartalmazza. Az elkülönített PostgreSQL-adatbázis és futtatói szerepkör neve szándékosan rögzített. Az adapter szerződése a MODULOK fájlban van. |
| Parancssori vizsgamappa és fix solution.sql | Megvalósítva. A kezdőállapot külön SQL-fájl. A beolvasott előkészítő fájlok nem értékelődnek beadásként. |
| Hallgatói .sql, név, Neptun, egész vagy betűs sorszám, több sor és üres válasz | Megvalósítva. A numerikus fejléc után SQL ugyanazon a soron szóközzel is megadható, vagy új sorban. Egy feladathoz egy SQL-utasítás tartozik. A Neptun-kód pontosan hat karakterből áll: betűkből és számjegyekből. |
| Tanári és hallgatói előkészítés | Külön solutionpre és studentpre blokkok, külön adatbázis-állapot; friss kezdőadat tesztenként. A feltételeket a megadott tesztadatokon ellenőrzi. |
| Fő modul és típusonkénti javítás | A fő modul olvas, naplóz, hallgatón és feladaton végigmegy. A javító külön SELECT, INSERT, UPDATE, DELETE, CREATE és DROP összevetésre küld. |
| SELECT megvalósítása | Oszlop- és sorszám, tartalom, ismétlődés, oszlopnév, kötelező sorrend, kis-/nagybetű és részpont ellenőrizhető. PostgreSQL-en opcionális szerkezeti elvárásként a külső ORDER BY, valamint LOWER/UPPER használata is előírható. |
| INSERT és részpont | A cél és az esetlegesen érintett más objektumok végállapotát, valamint a valódi sorváltozásokat ellenőrzi. A részpont részfeltételenként mérhető. |
| DELETE, UPDATE, CREATE TABLE/VIEW, DROP TABLE/VIEW | A támogatott egyutasításos feladatoknál megvalósítva. A CREATE eredménye a nevet, oszlopokat, adattípusokat, támogatott megszorításokat és a tesztadatokon megfigyelt nézettartalmat ellenőrzi. |
| CREATE USER / GRANT | Kézi elbírálás. A hallgatói SQL nem fut rendszerszintű jogosultsággal. A tanári minimumként kiemelt SELECT és INSERT ettől függetlenül működik. |
| Egységes AI modul, beállítás, prompt, fix forma | Helyi API, Markdown útmutató, feladatonkénti JSON-válasz és maximumhoz kötött egész pontjavaslat. Ellenőrzött tényekből dolgozik. Az AI pontjavaslata és szabad szövege elkülönített tanári fájlban van, nem írja felül a mért pontot. |
| AI bemenet személyes adatok nélkül | Név és Neptun-kód nem része az átadott sémának. A futtató eltávolítja a konkrét hallgató azonosítóit, ha véletlenül a tanári feladatszövegben szerepelnek. A beadott és a megoldó SQL nem megy át a modellnek. |
| Feladatonkénti AI-kontextus / helyi visszakeresés | Az AI ténycsomagokkal dolgozik, a kész javaslat feladatonként menthető és folytatható. Nem épült helyi RAG, mert a tanári kiegészítésben ez kipróbálandó ötlet, nem kötelező funkció. |
| Output modul: egyéni fájl, fejléc, rekord, összesítés, zárás | Külön fejléc-, feladatsor- és láblécfüggvények, UTF-8 név_Neptun.txt, feladatpont és S forrásjel. A csak tanári AI-javaslatot nem jelöljük alkalmazott A pontnak. |
| Összesítő: tabulált .xls, név, kód, összpont, feladatoszlopok és átlagok | A leadási próba a `--spec-output` kapcsolóval tabulátorral tagolt `osszesito.xls`-t ír. Az átlag a megállapított pontokból készül. |
| INFO/ERROR, ezredmásodperces fájlnév, -d/--debug | Megvalósítva. A napló tartalmaz indulást, paramétereket, beadás fájlnevét, státuszt, befejezést és hibát. Debug módban a projektmodulok függvényhívásai is megjelennek, argumentumértékek nélkül. Az AI-folytatás külön időbélyeges naplót ír; a helyi AI hibái ERROR szintűek. |
| Végtelen futás és időkorlátok | Adatbázis- és munkafolyamat-időkorlátok. Szabadon futó tárolt eljárás nincs a támogatott hallgatói feladattípusok között. |
| Közös tervezés, külön saját munka, megfontolt API | Modulhatár-leírás és munkamegosztási javaslat készült. A beállítás explicit paraméter; a futási állapot nem modulglobális. Az egyéni munkát a két hallgatónak saját tényleges hozzájárulása alapján kell rögzítenie. |
| Egyetemi AI-eszköz és Teams dokumentáció | Az egyetemi AI fejlesztést támogató lehetőség, nem futtatási függőség. A Teams-sablon nincs mellékelve; a közös fejlődési napló és a két külön, legalább kétoldalas beszámoló kitöltése és beadása a hallgatók feladata. Mellékelve van egy kitölthető vázlat. |
