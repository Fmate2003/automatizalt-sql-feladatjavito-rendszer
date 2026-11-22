# Oracle 12c üzembe helyezés

Az Oracle-adapter az Oracle 12c szintaxisához illesztett mintát és a Python `oracledb` illesztőprogramot használja. A PostgreSQL ellenőrzés nem igazolja az Oracle üzembe helyezését. A lenti mintafuttatás szükséges ahhoz, hogy az adott Oracle 12c példányon ellenőrzöttnek nevezhessük.

1. Az adatbázis-adminisztrátor hozzon létre elkülönített oktatási PDB-t (a konténer-adatbázis elkülönített része) vagy oktatási példányt. Ezen futtassa a `database/oracle_init.sql` fájlt, előbb cserélje ki a minta jelszót. Az illesztőprogram ideiglenes helyi fiókot hoz létre a tanári és a hallgatói futtatáshoz; a beadást kizárólag a korlátozott ideiglenes fiók futtatja. Az elkülönített környezetbe ne kerüljön éles vagy valódi hallgatói adatbázis.
2. Telepítsd: `.venv/bin/python -m pip install -r requirements-oracle.txt`. A `config.oracle.json` fájlban a `database` mező az Oracle szolgáltatásneve, nem az adatbázis-fájl neve. Töltsd ki a címet, portot és táblateret. Add meg a dedikált fiók jelszavát a `SQLGRADER_DB_PASSWORD` környezeti változóban, ne a JSON fájlba írd:

   ```bash
   read -rsp "Oracle jelszó: " SQLGRADER_DB_PASSWORD
   export SQLGRADER_DB_PASSWORD
   printf '\n'
   ```

3. Futtasd:

   ```bash
   .venv/bin/python -m sqlgrader minta/oracle --config config.oracle.json
   ```

Thin módban a meghajtó nem igényel Oracle Client telepítést. A helyi Oracle 12c telepítés hitelesítési beállításaitól függően szükség lehet a kompatibilis Oracle Instant Clientre; az `oracle_client` mezőben a könyvtár adható meg, a rendszeren a klienskönyvtárak betöltését is be kell állítani. A kliens és szerver kompatibilitását a helyi adminisztrátor ellenőrizze.

Ha egy megszakított futás után az Oracle nem engedi az ideiglenes fiók törlését, a naplóban szerepel az érintett `SG_`-azonosító. Ilyenkor az adminisztrátor ellenőrizze, hogy nincs-e aktív kapcsolat, majd távolítsa el az érintett javítói fiókot. Az önálló hallgatói `CREATE USER` és `GRANT` feladatok kézi ellenőrzésűek; a futtató fiók nem ad rendszerszintű jogosultságot a beadásnak.
