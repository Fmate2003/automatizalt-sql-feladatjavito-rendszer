# Részpontozás a javítókulcsban

A részpontozó az SQL eredményét és az adatbázis állapotát vizsgálja. Az
alias, a formázás és az SQL megoldás szerkezete önmagában nem befolyásolja a
pontot. Az adott adatbázis-adapter támogatott SQL-részhalmaza érvényes.

- `"partial":"auto"`: feladattípus szerinti alapelosztás. Ez az alapérték.
  Legalább egy pont a teljes egyezéshez kötött. Kis maximumpontnál egyes
  szempontok súlya a pont egészre kerekítése miatt nulla.
- `"partial":"off"`: teljes pont vagy nulla. A külön megadott szintaktikai
  próbálkozási pont ettől függetlenül érvényes.
- `"partial":{...}`: egyedi pontozási feltételek. A súlyok pozitív egész számok,
  összegük a feladat maximuma. Kötelező egy `exact` ellenőrzés.

A `points` mezőben feladatonként külön adható meg a maximumpont. A
[30 fős próbavizsgán](../probak/zh-30-diak/FELADATLAP.md) az egyszerű szűrésért
2 pont, a fizetett rendelések nézetéért 7 pont, a több megszorítással
együtt létrehozott tábláért 9 pont jár. A részpontokat az adott feladat
követelményei szerint kell elosztani az új maximumon belül.

| Típus | Beállítható ellenőrzések az exact mellett |
| --- | --- |
| SELECT | column_count (oszlopszám), column_names (ha előírt), row_count (sorszám), matching_rows (egyező sorok aránya), matching_rows_ci (egyezés kis-/nagybetű nélkül), order (ha kötelező). |
| INSERT, UPDATE, DELETE | changed_rows (egyező adatváltozások), change_count (azonos darab hozzáadott és eltávolított sor), target_row_count (céltábla végső sorszáma), target_rows (végső adatai), other_objects (többi objektum állapota). |
| CREATE TABLE | object (név és típus), columns (oszlopnevek és sorrend), types (típusok és tulajdonságok), constraints (megszorítások), target_rows, other_objects. |
| CREATE VIEW | object, columns, types, target_rows, other_objects. |
| DROP TABLE, DROP VIEW | removed (a cél eltűnt), other_objects. |
| CREATE USER, GRANT | Kézi elbírálás; a beadás nem kap rendszerszintű jogosultságot. |

Az egyező sorok arányánál az ismétlődések is számítanak. A nevező a várt
és kapott sorok száma közül a nagyobb, ezért a hiányzó és a fölösleges
sor is számít. A pont az arány és a súly szorzata, lefelé kerekítve.
Több adatkészletnél feltételenként a leggyengébb teszt eredménye számít.
Az UPDATE régi és új sorát a program eltávolított és hozzáadott sorként
veszi figyelembe az adatváltozás összevetésekor. Külön előkészítésnél a
changed_rows feltételhez a várt és kapott változás legyen összevethető.

A 30 fős próba 2. feladatában a helyes sorok hibás sorrendben 2/3 pontot érnek.

```sql
--2 comparetype
{"kind":"select","points":3,"ordered":true,"partial":{"column_count":1,"matching_rows":1,"exact":1}}
--2 solution SELECT id,price FROM products ORDER BY price DESC,id ASC;
```

A matching_rows, target_rows és changed_rows ellenőrzéshez külön
oszloplista is megadható, egytől számozva. Adatmódosításnál a rekord
kulcsoszlopát is érdemes bevonni, hogy a jó mezőérték ne járjon ponttal,
ha másik rekordban szerepel. Az index az eredmény vagy tábla oszlopsorrendjét követi.

```sql
--5 comparetype
{"kind":"insert","target":"customers","points":4,"partial":{
  "azonosito":{"check":"changed_rows","points":1,"columns":[1],"label":"Helyes azonosító"},
  "nev":{"check":"changed_rows","points":1,"columns":[1,2],"label":"Helyes név"},
  "varos":{"check":"changed_rows","points":1,"columns":[1,3],"label":"Helyes város"},
  "exact":1}}
--5 solution INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Pecs');
```

A `"syntax_credit":1` egy próbálkozási pont igazolt szintaktikai hibára.
Nem bizonyít részben helyes végrehajtást. Alapértéke 0. A hiányzó beadás
0 pont, a rendszerhiba függőben marad. Nem engedélyezett utasítás vagy
adatintegritási hiba önmagában nem szintaktikai hiba.

Az egyéni pontlap és a JSON feltételenként tartalmazza a megadott és
levont pontot. A [Markdown AI útmutató](AI_PONTOZASI_UTMUTATO.md) a
pontbontással együtt kerül a helyi modellhez. A modell az adott feladat
maximumáig tehet pontjavaslatot. Az oktató külön jelentésben látja a javaslatot és az indoklást. A hallgatói pontlap az ellenőrzött tényadatokat tartalmazza.
