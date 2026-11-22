--pregen create_db.sql
--case base
--case edge edge.sql

--1 comparetype
{"kind": "select", "points": 2, "description": "Sorold fel az id és name mezőt a legalább 100 árú termékekhez.", "partial": {"matching_rows": 1, "exact": 1}}
--1 solution
SELECT id,name FROM products WHERE price>=100;

--2 comparetype
{"kind": "select", "points": 3, "description": "Listázd az id és price mezőt ár szerint csökkenően, egyező árnál id szerint növekvően.", "ordered": true, "partial": {"column_count": 1, "matching_rows": 1, "exact": 1}}
--2 solution
SELECT id,price FROM products ORDER BY price DESC,id ASC;

--3 comparetype
{"kind": "select", "points": 5, "description": "Minden vevő id-ja mellett add vissza a rendelések számát; rendelés hiányában 0 legyen.", "partial": {"column_count": 1, "matching_rows": 3, "exact": 1}}
--3 solution
SELECT c.id,COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4 comparetype
{"kind": "select", "points": 6, "description": "Rendelésenként add vissza az order_id-t és a tételenkénti mennyiség × ár összegét.", "partial": {"column_count": 1, "matching_rows": 4, "exact": 1}, "syntax_credit": 1}
--4 solution
SELECT i.order_id,SUM(i.quantity*p.price) FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id;

--5 comparetype
{"kind": "insert", "points": 4, "description": "Szúrj be egy vevőt: id=100, name='Minta Elek', city='Pecs'. Más objektum ne változzon.", "target": "customers", "partial": {"azonosito": {"check": "changed_rows", "points": 1, "columns": [1], "label": "Megfelelő azonosító"}, "nev": {"check": "changed_rows", "points": 1, "columns": [1, 2], "label": "Megfelelő név az adott azonosítónál"}, "varos": {"check": "changed_rows", "points": 1, "columns": [1, 3], "label": "Megfelelő város az adott azonosítónál"}, "exact": 1}}
--5 solution
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Pecs');

--6 comparetype
{"kind": "update", "points": 5, "description": "Csak a 100 alatti árú termékek árát emeld 10 százalékkal.", "target": "products", "partial": {"changed_rows": 3, "change_count": 1, "exact": 1}}
--6 solution
UPDATE products SET price=price*1.10 WHERE price<100;

--7 comparetype
{"kind": "delete", "points": 6, "description": "Töröld a törölt állapotú rendelések tételeit. A rendelések maradjanak meg.", "target": "order_items", "partial": {"changed_rows": 4, "other_objects": 1, "exact": 1}}
--7 solution
DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status='cancelled');

--8 comparetype
{"kind": "create_table", "points": 9, "description": "Hozd létre a review_queue táblát: id egész elsődleges kulcs, product_id egész kötelező idegen kulcs a products(id)-ra, score egész kötelező, 1 és 5 között.", "target": "review_queue", "partial": {"object": 1, "columns": 1, "types": 2, "constraints": 4, "exact": 1}}
--8 solution
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5));

--9 comparetype
{"kind": "create_view", "points": 7, "description": "Hozd létre a paid_view nézetet a fizetett rendelések id és customer_id oszlopaival.", "target": "paid_view", "partial": {"object": 1, "columns": 1, "target_rows": 4, "exact": 1}}
--9 solution
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10 comparetype
{"kind": "drop_table", "points": 3, "description": "Töröld a temp_import táblát. Más objektum maradjon meg.", "target": "temp_import", "partial": {"removed": 1, "other_objects": 1, "exact": 1}}
--10 solution
DROP TABLE temp_import;

