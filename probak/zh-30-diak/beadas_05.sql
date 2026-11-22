--név: Árvai Emma
--neptun: B5FI0E

--1
SELECT id,name FROM products WHERE price>100;

--2
SELECT id,price FROM products ORDER BY price DESC,id DESC;

--3
SELECT c.id,COUNT(o.id) FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELECT i.order_id,SUM(i.quantity*p.price) FROM order_items i JOIN products p ON p.id=i.product_id WHERE i.order_id<15 GROUP BY i.order_id;

--5
INSERT INTO customers(city,id,name) SELECT 'Pecs',100,'Minta Elek';

--6
UPDATE products SET price=price*1.10 WHERE price<=100;

--7
DELETE FROM order_items WHERE quantity=1;

--8


--9
-- A megoldás kezdete
CREATE VIEW paid_view (id, customer_id) AS SELECT o.id,o.customer_id FROM orders o WHERE o.status IN ('paid');

--10
DROP TABLE unused_import;

