--név: Somodi Előd
--neptun: 1IXYJL

--1
SELECT p.id,p.name FROM products p WHERE NOT (p.price<100);

--2
SELECT id,price FROM products ORDER BY price DESC,id DESC;

--3
SELECT c.id,COUNT(o.id) FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELECT i.order_id,SUM(i.quantity+p.price) FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id;

--5
INSERT INTO customers(city,id,name) SELECT 'Pecs',100,'Minta Elek';

--6
UPDATE products SET price=price*1.10 WHERE price<=100;

--7
-- A megoldás kezdete
DELETE FROM order_items WHERE order_id=13;

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5));

--9
-- A megoldás kezdete
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status IN ('paid','new');

--10
-- A megoldás kezdete
DROP TABLE temp_import;

