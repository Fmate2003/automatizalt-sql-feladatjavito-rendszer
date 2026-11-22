--név: Mészkő Ábel
--neptun: 5HTD1J

--1
SELECT id,name FROM products WHERE price>=100;

--2
SELECT id,price FROM products ORDER BY -price,id;

--3
SELECT c.id,(SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id) FROM customers c;

--4
SELECT i.order_id,SUM(p.price*i.quantity) FROM products p INNER JOIN order_items i ON i.product_id=p.id GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Szeged');

--6
-- A megoldás kezdete
UPDATE products SET price=price*1.10 WHERE price<=100;

--7
DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status='cancelled');

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, score INTEGER NOT NULL);

--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10
DROP TABLE temp_import;

