--név: Minta Megoldó
--neptun: MINTA2

--1
SELECT id, name FROM customers WHERE city='Budapest';

--2
SELECT id, price FROM products ORDER BY price DESC, id ASC;

--3
SELECT o.id, c.name FROM orders o JOIN customers c ON c.id=o.customer_id WHERE o.status='paid';

--4
SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id HAVING COUNT(*)>=2;

--5
SELECT c.id, COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--6
SELECT id, price FROM products WHERE price>(SELECT AVG(price) FROM products);

--7
WITH totals AS (SELECT i.order_id, SUM(i.quantity*p.price) AS amount FROM order_items i JOIN products p ON p.id=i.product_id GROUP BY i.order_id) SELECT o.id,t.amount FROM orders o JOIN totals t ON t.order_id=o.id WHERE o.status='paid';

--8
INSERT INTO customers(id,name,city) VALUES (100,'Teszt Elek','Pecs');

--9
UPDATE products SET price=price*1.10 WHERE price<5000;

--10
DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status='cancelled');

