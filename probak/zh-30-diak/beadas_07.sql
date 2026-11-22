--név: Lantos Huba
--neptun: EQQ9CG

--1
SELECT id,name FROM products WHERE price>=100;

--2
SELECT id,name,price FROM products ORDER BY price DESC,id;

--3
SELECT c.id,COUNT(o.id) FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
-- A megoldás kezdete
SELECT i.order_id,SUM(p.price) FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Pecs');

--6


--7
DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status='cancelled');

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5));

--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10
DROP TABLE temp_import;

