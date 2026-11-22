--név: Szeder Emil
--neptun: 90NJ0C

--1
SELECT p.id,p.name FROM products p WHERE NOT (p.price<100);

--2
-- A megoldás kezdete
SELECT id,price FROM products ORDER BY -price,id;

--3
SELECT c.id,(SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id) FROM customers c;

--4
-- A megoldás kezdete
SELECT i.order_id,SUM(p.price*i.quantity) FROM products p INNER JOIN order_items i ON i.product_id=p.id GROUP BY i.order_id;

--5
INSERT INTO customers(city,id,name) SELECT 'Pecs',100,'Minta Elek';

--6
UPDATE products p SET price=p.price+p.price/10 WHERE NOT (p.price>=100);

--7
DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status='cancelled');

--8
-- A megoldás kezdete
CREATE TABLE review_queue(id INT, product_id INT NOT NULL, score INT NOT NULL, CONSTRAINT qa_pk PRIMARY KEY(id), CONSTRAINT qa_product FOREIGN KEY(product_id) REFERENCES products(id), CONSTRAINT qa_score CHECK(score BETWEEN 1 AND 5));

--9
CREATE VIEW paid_view (id, customer_id) AS SELECT o.id,o.customer_id FROM orders o WHERE o.status IN ('paid');

--10
DROP TABLE temp_import;

