-- Új sorok a határértékekhez, holtversenyhez, NULL-hoz és ismétlődésekhez.
INSERT INTO customers VALUES (6,'Fanni Minta','Debrecen'),(7,'Gabor Minta',NULL);
INSERT INTO products VALUES (7,'Adapter','gear',120,1,TRUE),(8,'Doboztarto','gear',99,1,TRUE),(9,'Jegyzet','paper',100,5,FALSE),(10,'Karton','paper',60,0,FALSE);
INSERT INTO orders VALUES (16,NULL,'new',DATE '2026-01-20'),(17,6,'paid',DATE '2026-01-20'),(18,3,'paid',DATE '2026-01-02'),(19,6,'cancelled',DATE '2026-02-01');
INSERT INTO order_items VALUES (16,8,1),(17,7,2),(18,9,1),(19,8,2);
INSERT INTO scratch_flags VALUES (5,'low',DATE '2025-12-31'),(6,'high',DATE '2026-02-01');
