--név: Szirmay Dóra
--neptun: 6C9NJU

--1
SELECT id, FROM products WHERE price>=100;

--2


--3
SELECT c.id COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELEC i.order_id FROM order_items i;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Szeged');

--6
UPDATE products SET price=price*1.10 WHERE price<100;

--7
-- A megoldás kezdete
DELETE FROM order_items WHERE quantity=1;

--8
-- A megoldás kezdete
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, score INTEGER NOT NULL);

--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10
DROP TABLE IF EXISTS temp_import RESTRICT;

