--név: Dombai Dávid
--neptun: 0J6O5Y

--1
SELECT id,name FROM products WHERE price>=100;

--2
SELECT id,price FROM products ORDER BY price DESC,id ASC;

--3
SELECT c.id,COUNT(o.id) FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id;

--4
SELEC i.order_id FROM order_items i;

--5
-- A megoldás kezdete
INSERT INTO customers(city,id,name) SELECT 'Pecs',100,'Minta Elek';

--6
-- A megoldás kezdete
UPDATE products p SET price=p.price+p.price/10 WHERE NOT (p.price>=100);

--7
DELETE FROM order_items i USING orders o WHERE o.id=i.order_id AND o.status='cancelled';

--8
CREATE TABLE review_queue(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, score INTEGER NOT NULL);

--9
CREATE VIEW paid_view AS SELECT id,customer_id FROM orders WHERE status='paid';

--10


