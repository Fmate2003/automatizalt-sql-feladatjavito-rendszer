--név: Mogyorósi Emil
--neptun: 9IB0IA

--1
SELECT id,name FROM products WHERE price>100;

--2
SELECT id,price FROM products ORDER BY price DESC,id DESC;

--3
SELECT c.id,COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4


--5
INSERT INTO customers VALUES (100,'Minta Elek','Pecs';

--6
-- A megoldás kezdete
UPDATE products SET price=price*1.10 WHERE price<=100;

--7
DELETE FROM order_items WHERE quantity=1;

--8
-- A megoldás kezdete
CREATE TABLE review_queue(id INT, product_id INT NOT NULL, score INT NOT NULL, CONSTRAINT qa_pk PRIMARY KEY(id), CONSTRAINT qa_product FOREIGN KEY(product_id) REFERENCES products(id), CONSTRAINT qa_score CHECK(score BETWEEN 1 AND 5));

--9


--10
DROP TABLE IF EXISTS temp_import RESTRICT;

