--név: Szeder Réka
--neptun: FF94LT

--1
SELECT id, FROM products WHERE price>=100;

--2
SELECT id,price FROM products ORDER BY price DESC,id DESC;

--3
-- A megoldás kezdete
SELECT c.id,COUNT(o.id) FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELECT i.order_id,SUM(p.price*i.quantity) FROM products p INNER JOIN order_items i ON i.product_id=p.id GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Szeged');

--6
UPDATE products SET price=price*1.10 WHERE price<100;

--7
DELETE FROM order_items i USING orders o WHERE o.id=i.order_id AND o.status='cancelled';

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5));

--9
CREATE VIEW paid_view (id, customer_id) AS SELECT o.id,o.customer_id FROM orders o WHERE o.status IN ('paid');

--10
DROP TABLE unused_import;

