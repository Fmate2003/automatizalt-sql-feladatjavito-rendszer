--név: Csermely Kata
--neptun: 9RB4FP

--1
SELECT id,name FROM products WHERE price>100;

--2
SELECT id,price FROM products ORDER price DESC;

--3
SELECT c.id,COUNT(o.id) FROM customers c JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELECT i.order_id,SUM(i.quantity+p.price) FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id;

--5
INSERT INTO customers(id,name,city) VALUES (100,'Minta Elek','Szeged');

--6
UPDATE products SET price=price*1.01 WHERE price<100;

--7


--8


--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status IN ('paid','new');

--10
DROP TABLE IF EXISTS temp_import; DROP TABLE unused_import;

