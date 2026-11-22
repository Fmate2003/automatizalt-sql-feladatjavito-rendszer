--név: Pálos Dávid
--neptun: R38Y7Q

--1
SELECT id,name FROM products WHERE price>100;

--2
SELECT id,price FROM products ORDER price DESC;

--3
SELECT c.id,(SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id) FROM customers c;

--4
SELECT i.order_id,SUM(p.price*i.quantity) FROM products p INNER JOIN order_items i ON i.product_id=p.id GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Pecs');

--6
UPDATE products SET price=price*1.10 WHERE price<=100;

--7
DELETE FROM orders WHERE status='cancelled';

--8
-- A megoldás kezdete
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, score INTEGER NOT NULL);

--9
CREATE VIEW paid_view (id, customer_id) AS SELECT o.id,o.customer_id FROM orders o WHERE o.status IN ('paid');

--10
DROP TABLE temp_import;

