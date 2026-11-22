--név: Egresdi Viola
--neptun: R0VNE3

--1
SELECT id,name FROM products WHERE id IN (1,2,3,5);

--2
SELECT id,price FROM products ORDER BY price DESC,id DESC;

--3


--4
SELECT i.order_id,SUM(i.quantity*p.price) FROM order_items i JOIN products p ON p.id=i.product_id WHERE i.order_id<15 GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Pecs');

--6
UPDATE products SET price=price*1.01 WHERE price<100;

--7
-- A megoldás kezdete
DELETE FROM order_items WHERE quantity=1;

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, score INTEGER NOT NULL);

--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status IN ('paid','new');

--10
-- A megoldás kezdete
DROP TABLE unused_import;

