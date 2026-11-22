--név: Békési Luca
--neptun: OOTD62

--1
SELECT p.id,p.name FROM products p WHERE NOT (p.price<100);

--2
SELECT id,name,price FROM products ORDER BY price DESC,id;

--3
SELECT c.id,(SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id) FROM customers c;

--4
SELECT i.order_id,SUM(p.price) FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id;

--5


--6
UPDATE products p SET price=p.price+p.price/10 WHERE NOT (p.price>=100);

--7
DELETE FROM order_items WHERE quantity=1;

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5));

--9
CREATE VIEW paid_view SELECT id,customer_id FROM orders WHERE status='paid';

--10
DROP TABLE unused_import;

