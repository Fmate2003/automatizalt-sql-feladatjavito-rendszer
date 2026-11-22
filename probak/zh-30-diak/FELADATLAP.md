# SQL próbavizsga

10 feladat, összesen 50 pont. Feladatonként egy SQL-utasítás adható meg.
Minden feladat külön, tiszta kezdőállapotból indul. Az oszlopok kért sorrendjét tartsd meg.

Az adatszerkezetet a create_db.sql tartalmazza. A helyes megoldást alap- és bővített adatokon is ellenőrizzük.

1. **SELECT (2 pont):** Sorold fel az id és name mezőt a legalább 100 árú termékekhez.
2. **SELECT (3 pont):** Listázd az id és price mezőt ár szerint csökkenően, egyező árnál id szerint növekvően.
3. **SELECT (5 pont):** Minden vevő id-ja mellett add vissza a rendelések számát; rendelés hiányában 0 legyen.
4. **SELECT (6 pont):** Rendelésenként add vissza az order_id-t és a tételenkénti mennyiség × ár összegét.
5. **INSERT (4 pont):** Szúrj be egy vevőt: id=100, name='Minta Elek', city='Pecs'. Más objektum ne változzon.
6. **UPDATE (5 pont):** Csak a 100 alatti árú termékek árát emeld 10 százalékkal.
7. **DELETE (6 pont):** Töröld a törölt állapotú rendelések tételeit. A rendelések maradjanak meg.
8. **CREATE TABLE (9 pont):** Hozd létre a review_queue táblát: id egész elsődleges kulcs, product_id egész kötelező idegen kulcs a products(id)-ra, score egész kötelező, 1 és 5 között.
9. **CREATE VIEW (7 pont):** Hozd létre a paid_view nézetet a fizetett rendelések id és customer_id oszlopaival.
10. **DROP TABLE (3 pont):** Töröld a temp_import táblát. Más objektum maradjon meg.
