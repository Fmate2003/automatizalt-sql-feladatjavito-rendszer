--pregen create_db.sql
--case base
--case edge edge.sql

--1 comparetype
{"kind": "select", "points": 4, "description": "Listázd a budapesti vevők id és name mezőit. A sorrend nem számít.", "target": null, "ordered": false, "column_names": false, "partial": "auto"}
--1 solution
SELECT id, name FROM customers WHERE city='Budapest';

--2 comparetype
{"kind": "select", "points": 4, "description": "Listázd minden termék id és price mezőjét ár szerint csökkenően, azonos árnál id szerint növekvően.", "target": null, "ordered": true, "column_names": false, "partial": {"column_count": 1, "matching_rows": 2, "exact": 1}}
--2 solution
SELECT id, price FROM products ORDER BY price DESC, id ASC;

--3 comparetype
{"kind": "select", "points": 5, "description": "Add vissza minden fizetett rendelés id-ját és vevőjének nevét (name).", "target": null, "ordered": false, "column_names": false, "partial": "auto"}
--3 solution
SELECT o.id, c.name FROM orders o JOIN customers c ON c.id=o.customer_id WHERE o.status='paid';

--4 comparetype
{"kind": "select", "points": 5, "description": "Vevőnként add meg a customer_id-t és a rendelések darabszámát. Csak a legalább két rendeléssel rendelkező vevők szerepeljenek.", "target": null, "ordered": false, "column_names": false, "partial": "auto"}
--4 solution
SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id HAVING COUNT(*)>=2;

--5 comparetype
{"kind": "select", "points": 6, "description": "Minden vevő id-ja mellé add meg rendeléseinek számát. A rendelés nélküli vevők is szerepeljenek nulla értékkel.", "target": null, "ordered": false, "column_names": false, "partial": {"column_count": 1, "matching_rows": 4, "exact": 1}}
--5 solution
SELECT c.id, COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--6 comparetype
{"kind": "select", "points": 6, "description": "Listázd az átlagnál drágább termékek id és price mezőit.", "target": null, "ordered": false, "column_names": false, "partial": "auto"}
--6 solution
SELECT id, price FROM products WHERE price>(SELECT AVG(price) FROM products);

--7 comparetype
{"kind": "select", "points": 5, "description": "Fizetett rendelésenként add meg az id-t és a tételek quantity*price összegét. CTE is használható, de bármely azonos eredményű megoldás elfogadható.", "target": null, "ordered": false, "column_names": false, "partial": "auto"}
--7 solution
WITH totals AS (SELECT i.order_id, SUM(i.quantity*p.price) AS amount FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id) SELECT o.id,t.amount FROM orders o JOIN totals t ON t.order_id=o.id WHERE o.status='paid';

--8 comparetype
{"kind": "insert", "points": 5, "description": "Szúrj be egy vevőt: id=100, name='Teszt Elek', city='Pecs'. Más adat ne változzon.", "target": "customers", "ordered": false, "column_names": false, "partial": {"azonosito": {"check": "changed_rows", "points": 1, "columns": [1], "label": "A megfelelő azonosítójú rekord beszúrása"}, "nev": {"check": "changed_rows", "points": 1, "columns": [1, 2], "label": "A beszúrt rekord azonosítója és neve"}, "varos": {"check": "changed_rows", "points": 1, "columns": [1, 3], "label": "A beszúrt rekord azonosítója és városa"}, "other_objects": 1, "exact": 1}}
--8 solution
INSERT INTO customers(id,name,city) VALUES (100,'Teszt Elek','Pecs');

--9 comparetype
{"kind": "update", "points": 5, "description": "Emeld 10%-kal az 5000 alatti árú termékek árát. Más adat ne változzon.", "target": "products", "ordered": false, "column_names": false, "partial": "auto"}
--9 solution
UPDATE products SET price=price*1.10 WHERE price<5000;

--10 comparetype
{"kind": "delete", "points": 5, "description": "Töröld a cancelled állapotú rendelések tételeit az order_items táblából. A rendelések maradjanak meg.", "target": "order_items", "ordered": false, "column_names": false, "partial": "auto"}
--10 solution
DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status='cancelled');

