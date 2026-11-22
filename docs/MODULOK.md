# Modulhatárok és közös API

| Modul | Fontos bemeneti és kimeneti szerződés |
| --- | --- |
| inputs | key(folder, limit): feladatok, kezdő SQL, tesztadatkészletek és kizárt fájlok. submission(path, task_ids, limit): név, kód és feladatonkénti SQL. Hibás formátumnál ValueError. |
| config | load(path): változtathatatlan Config. Az adatbázis-jelszó kívülről, környezeti változóban adható meg. |
| database és adapterek | check(config), validate(config, statement, task), run(config, task, scripts, answer, token), cleanup(config, tokens). A run állapotot, összehasonlítható értéket és hibakódot ad vissza. |
| comparison, rubric | A feladattípus szerinti eredmény-egyezés és részpontfeltételek, a fájlkezeléstől és AI-tól függetlenül. |
| grading | grade_task(config, task, answer, pregen, cases, tokens): állapot, pontos feltételek és feladatpont. report(name, neptun, results): egyéni eredmény. Nincs megállapított pont rendszerhibában. |
| ai | review(config, tasks): ellenőrzött tényekből kér formailag korlátozott AI-javaslatot. A jelölés, indoklás és javasolt pont nem változtatja meg a forrásadatot. |
| feedback | fill(run, reports, config): folytatható tanári AI-javaslatok és hiteles hallgatói szövegek készítése a mentett pontozásból. |
| output | individual(directory, report), summary(directory, reports, tasks), write_feedback(directory, report, notes). Elkülönített fájlírás és szövegformázás. |
| runtime | bounded(function, args, seconds, logfile=…, debug=…): platformfüggetlen munkafolyamat, határidő és explicit naplóbeállítás. |
| __main__ | main(argv): beolvasás, kapcsolati ellenőrzés, ciklusok, naplózás, fájlok és opcionális AI-fázis. |

## Közös tervezés és felosztás

A két hallgató közösen rögzítse az összevetés és a részpontozás szabályait,
az állapotokat és a fenti függvények szerződését. Ezután az egyik feladatköre
lehet az SQL-adapter, az elkülönítés és a SELECT/INSERT ellenőrzés; a másiké
a bemenet/kimenet, az AI, a naplózás és a bemutató. Ez javaslat, nem a
hallgatók már elvégzett munkájának nyilvántartása. A közös átadási pont a
formátum, a tesztadatok és a pontok ellenőrzése. A tényleges szerzőséget
az egyéni beszámolókban kell leírni.
