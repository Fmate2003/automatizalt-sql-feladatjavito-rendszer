--név: Ablakos Huba
--neptun: WT59VO

--1
SELECT id,name FROM products WHERE price>=100;

--2
SELECT id,price FROM products ORDER BY price DESC,id DESC;

--3
-- A megoldás kezdete
SELECT c.id,COUNT(o.id) FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELEC i.order_id FROM order_items i;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Szeged');

--6
UPDATE products SET price=price*1.10 WHERE price<=100;

--7
DELETE FROM order_items WHERE quantity=1;

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, score INTEGER NOT NULL;

--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10
DROP TABLE temp_import;

