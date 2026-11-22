--név: Tánczos Dóra
--neptun: 942D9V

--1
SELECT id,name FROM products WHERE price>=100;

--2
-- A megoldás kezdete
SELECT id,price FROM products ORDER BY price DESC,id ASC;

--3
SELECT c.id,(SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id) FROM customers c;

--4
SELECT i.order_id,SUM(p.price*i.quantity) FROM products p INNER JOIN order_items i ON i.product_id=p.id GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Pecs');

--6
UPDATE products p SET price=p.price+p.price/10 WHERE NOT (p.price>=100);

--7
DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status='cancelled');

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5));

--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10
DROP TABLE IF EXISTS temp_import RESTRICT;

