--név: Várhalmi Ábel
--neptun: 514UBI

--1
SELECT id,name FROM products WHERE price>100;

--2
SELECT id,price FROM products ORDER BY price DESC,id ASC;

--3
SELECT c.id,COUNT(o.id) FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELECT i.order_id,SUM(i.quantity*p.price) FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Pecs');

--6
UPDATE products SET price=price*1.10 WHERE price<=100;

--7
DELETE FROM order_items i USING orders o WHERE o.id=i.order_id AND o.status='cancelled';

--8
CREATE TABLE review_queue(id INTEGER, product_id INTEGER NOT NULL, score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5));

--9


--10
-- A megoldás kezdete
DROP TABLE IF EXISTS temp_import RESTRICT;

