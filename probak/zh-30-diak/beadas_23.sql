--név: Almási Fanni
--neptun: 9UIIAW

--1
SELECT p.id,p.name FROM products p WHERE NOT (p.price<100);

--2
SELECT id,price FROM products ORDER BY price DESC,id DESC;

--3
SELECT c.id,COUNT(o.id) FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELECT i.order_id,SUM(p.price*i.quantity) FROM products p INNER JOIN order_items i ON i.product_id=p.id GROUP BY i.order_id;

--5
INSERT INTO customers VALUES (100,'Minta Elek','Pecs';

--6
UPDATE products SET price=price*1.10 WHERE price<=100;

--7
DELETE FROM order_items i USING orders o WHERE o.id=i.order_id AND o.status='cancelled';

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, score INTEGER NOT NULL;

--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10
DROP TABLE IF EXISTS temp_import RESTRICT;

