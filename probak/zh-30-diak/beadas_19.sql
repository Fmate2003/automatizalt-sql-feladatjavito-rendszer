--név: Tánczos Adél
--neptun: 9BWPES

--1
SELECT p.id,p.name FROM products p WHERE NOT (p.price<100);

--2
SELECT id,price FROM products ORDER BY -price,id;

--3
SELECT c.id,COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELECT i.order_id,SUM(i.quantity*p.price) FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id;

--5
-- A megoldás kezdete
INSERT INTO customers(city,id,name) SELECT 'Pecs',100,'Minta Elek';

--6
UPDATE products SET price=price*1.10 WHERE price<100;

--7
DELETE FROM order_items i USING orders o WHERE o.id=i.order_id AND o.status='cancelled';

--8
CREATE TABLE review_queue(id INT, product_id INT NOT NULL, score INT NOT NULL, CONSTRAINT qa_pk PRIMARY KEY(id), CONSTRAINT qa_product FOREIGN KEY(product_id) REFERENCES products(id), CONSTRAINT qa_score CHECK(score BETWEEN 1 AND 5));

--9
CREATE VIEW paid_view (id, customer_id) AS SELECT o.id,o.customer_id FROM orders o WHERE o.status IN ('paid');

--10
DROP TABLE IF EXISTS temp_import RESTRICT;

