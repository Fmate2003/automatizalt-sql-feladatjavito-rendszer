--név: Árvai Márk
--neptun: 3SKJLF

--1
SELECT p.id,p.name FROM products p WHERE NOT (p.price<100);

--2
SELECT id,price FROM products ORDER BY -price,id;

--3
SELECT c.id,COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELECT i.order_id,SUM(i.quantity*p.price) FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Szeged');

--6
UPDATE products SET price=price*1.10 WHERE price<100;

--7
DELETE FROM order_items i USING orders o WHERE o.id=i.order_id AND o.status='cancelled';

--8
CREATE TABLE review_queue(id INT, product_id INT NOT NULL, score INT NOT NULL, CONSTRAINT qa_pk PRIMARY KEY(id), CONSTRAINT qa_product FOREIGN KEY(product_id) REFERENCES products(id), CONSTRAINT qa_score CHECK(score BETWEEN 1 AND 5));

--9
-- A megoldás kezdete
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10
DROP TABLE temp_import;

