# A vizsgamappa SQL formátuma

## Tanári javítókulcs

A fájlnév `solution.sql`. UTF-8 kódolás, BOM-mal vagy anélkül. Egy feladat azonosítója pozitív egész, opcionálisan utána egy betű. A javítókulcs első előfordulási sorrendje adja a pontlap oszlopsorrendjét. A fejléc után az SQL kezdődhet ugyanazon vagy az új sorban; a blokk a következő ismert fejlécig tart.

```sql
--pregen create_db.sql
--case base
--case edge edge.sql

--1a comparetype
{"kind":"select","points":4,"description":"Listázd a vevők azonosítóját növekvően.","ordered":true}

--1a solution
SELECT id
FROM customers
ORDER BY id;

--1a solutionpre
-- opcionális, csak a tanári futtatás előtt
--1a studentpre
-- opcionális, csak a hallgatói futtatás előtt

--1b comparetype
{"kind":"insert","target":"customers","points":3,"description":"Szúrj be egy új vevőt."}
--1b solution
INSERT INTO customers(id, name) VALUES (20, 'Minta');
```

| Beállítás | Jelentése |
| --- | --- |
| `kind` | `select`, `insert`, `update`, `delete`, `create_table`, `create_view`, `drop_table`, `drop_view`. A `create_user` és `grant` kézi elbírálással rögzíthető. |
| `points` | A feladat maximumpontja pozitív egész számként. Feladatonként eltérhet. Egyedi részpontozásnál a feltételek súlyának összege egyezzen ezzel az értékkel. |
| `target` | A módosítandó vagy létrehozandó helyi objektumnév. SELECT esetén elhagyható. |
| `ordered` | `true`: a sorok sorrendje is követelmény; egyébként az ismétlődéseket megőrizve hasonlítunk. |
| `column_names` | `true`: az oszlopnevek és sorrendjük is egyezzen. |
| `case_insensitive` | `true`: a cellák szövegértékeinél nem számít a kis- és nagybetű. Alapértéke `false`. |
| `description` | Feladatleírás az egyéni laphoz. |
| partial | auto (alapérték), off vagy egyedi rubrika. Lásd [részpontozás](RESZPONTOZAS.md). |
| syntax_credit | Opcionális egész próbálkozási pont szintaktikai hibára. Alapérték 0, a maximumnál kisebb. |

PostgreSQL-en opcionális SELECT-megkötések: a require_order_by igaz értéke
külső ORDER BY záradékot vár; a required_functions listában a lower és upper
írható elő. Ezeket csak kifejezett tanári követelmény esetén használd.
Az ordered kapcsoló ettől külön a mért sorrendre vonatkozik.
A fejléc után a SQL azonos sorban, szóközzel is megadható, például
a „--1a SELECT id FROM customers;” alakban.

A SELECT ellenőrzése nézi az oszlop- és sorszámot, az értékeket, ismétlődéseket és ha előírt, a sorrendet. Az adatváltoztató utasításoknál a végállapot számít, beleértve az egyéb táblákat és nézeteket. CREATE/DROP esetén objektumnév, szerkezet, megszorítások, valamint a megmaradó objektumok eredménye és adatai számítanak. Indexek, tárolt eljárások, teljesítmény, SQL-szöveg azonossága és kifejezetten egy adott függvény használata nem pontozott külön. A két előkészítő blokk eltérhet; ilyenkor az összevetett eredményt kell egyenértékűre tervezni.

## Hallgatói beadás

```sql
--név: Minta Hallgató
--neptun: ABC123
--1a
SELECT id
-- az első feladat megjegyzése
FROM customers
ORDER BY id;

--1b
```

A `--1b` után itt nincs válasz. A `--1a` pontosan egy önálló fejléc; a `-- az első feladat megjegyzése` a SQL része. A név és a hat karakteres Neptun-kód a feladatok előtt szerepeljen. A fájlnév tetszőleges `.sql` fájlnév lehet, kivéve a javítókulcsot és az abban megnevezett előkészítő fájlokat.

A hallgatói SQL csak korlátozott oktatási feladatkészletet támogat. Ne adj meg SQL*Plus vagy psql parancsot, tárolt eljárást, külső adatforrást, idegen sémát vagy rendszerszintű felhasználói utasítást.
