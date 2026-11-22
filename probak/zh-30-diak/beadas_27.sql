--név: Orbán Júlia
--neptun: 2FB6A0

--1
-- A megoldás kezdete
SELECT id,name FROM products WHERE price>100;

--2
SELECT id,price FROM products ORDER BY price DESC,id ASC;

--3
SELECT c.id COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4


--5
-- A megoldás kezdete
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Szeged');

--6
UPDATE products p SET price=p.price+p.price/10 WHERE NOT (p.price>=100);

--7
DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status='cancelled';

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, score INTEGER NOT NULL);

--9
-- A megoldás kezdete
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status IN ('paid','new');

--10
DROP TABLE;

