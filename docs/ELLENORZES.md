# Ellenőrzési jegyzet

- Linuxon az automatizált egységtesztek lefutottak. Lefedik többek között
  a betűs feladatazonosítókat, a hatkarakteres kód ellenőrzését, a
  részpontozást, az előírt SQL-szerkezetet, a munkafolyamat-indítást és
  a szándékosan hibás modelljavaslat elkülönítését.
- PostgreSQL 16.2-n mind a 30 beadást újrapontoztuk. A 300 feladatpont,
  a feladatonkénti maximumok és a részpontok összhangban vannak a
  javítókulccsal. Az egyéni TXT- és JSON-fájlok, valamint a két összesítő
  és az átlagok egyeznek. A korábbi kiosztáshoz képest 22 hallgató
  összpontja változott, a vizsga maximuma 50 pont maradt.
- Az AI API-ra szimulált, szándékosan ellentmondó vagy megszakadt
  válaszokkal ellenőriztük a hibatűrést. A súlyozott próbán szimulált
  AI-válaszokkal ellenőriztük a feladatonkénti maximumot is. A program
  elutasította a felső határt túllépő pontjavaslatokat. A pontfájlok
  érintetlenek maradtak a visszajelzés készítése közben.
- A natív Windows és az élő Oracle 12c futás nem volt ellenőrizhető ezen
  a gépen. A súlyozott próbát valós Ollama-válaszok nélkül ellenőriztük.

Egységtesztek: python -m unittest discover -s tests -v

Két kész futás pontjainak összehasonlítása:

    python -m sqlgrader.verify "regi/eredmenymappa" "uj/eredmenymappa"

Az ellenőrző az összpontot, feladatpontot, maximumot és állapotot
hasonlítja össze. A pontozás ismételhetőségéhez azonos javítókulccsal
készült futásokat hasonlíts össze. Az ötpontos kiosztáshoz képest az
ellenőrző jelzi a szándékosan módosított feladatmaximumokat is.
