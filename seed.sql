-- Starter data. Safe to run many times (INSERT IGNORE).

INSERT IGNORE INTO food_categories (id, name) VALUES
 (1,'Biryani'),(2,'Fried Rice'),(3,'Meals'),(4,'Tiffin'),(5,'Starters'),(6,'Rolls'),(7,'Main Course');

INSERT IGNORE INTO food_items
 (id, category_id, name, description, food_type, image, original_price, discounted_price, rating, is_bestseller) VALUES
 (1, 1,'Veg Biryani','Basmati rice cooked with fresh vegetables and spices','veg','veg-biryani.jpg',180,149,4.2,1),
 (2, 1,'Paneer Biryani','Fragrant biryani layered with soft paneer cubes','veg','paneer-biryani.jpg',230,199,4.4,0),
 (3, 2,'Gobi Fried Rice','Indo-Chinese fried rice tossed with crispy gobi','veg','gobi-fried-rice.jpg',150,129,4.0,0),
 (4, 3,'Veg Meals','Rice, sambar, rasam, two kootu, poriyal, curd and papad','veg','veg-meals.jpg',170,139,4.3,1),
 (5, 4,'Dosa','Crispy golden dosa served with chutney and sambar','veg','dosa.jpg',90,70,4.5,1),
 (6, 4,'Parotta','Flaky layered parotta, 2 pieces, served with salna','veg','parotta.jpg',60,50,4.1,0),
 (7, 7,'Paneer Butter Masala','Creamy tomato gravy with butter and paneer','veg','paneer-butter-masala.jpg',240,210,4.6,1),
 (8, 1,'Chicken Biryani','Seeraga samba rice with tender chicken and masala','nonveg','chicken-biryani.jpg',250,199,4.5,1),
 (9, 1,'Mutton Biryani','Slow cooked mutton pieces layered with biryani rice','nonveg','mutton-biryani.jpg',350,299,4.6,0),
 (10,5,'Chicken 65','Spicy deep fried chicken with curry leaves','nonveg','chicken-65.jpg',200,169,4.4,1),
 (11,2,'Chicken Fried Rice','Wok tossed rice with chicken and egg','nonveg','chicken-fried-rice.jpg',190,159,4.2,0),
 (12,6,'Egg Roll','Egg and onion wrapped in a soft rumali roti','nonveg','egg-roll.jpg',110,89,4.0,0),
 (13,5,'Fish Fry','Marinated fish shallow fried with masala','nonveg','fish-fry.jpg',260,229,4.3,0),
 (14,3,'Chicken Meals','Rice with chicken gravy, kootu, poriyal, rasam and curd','nonveg','chicken-meals.jpg',220,189,4.4,1);

INSERT IGNORE INTO addons (id, name, price) VALUES
 (1,'Pepsi',40),(2,'Fresh Lime Juice',35),(3,'Onion Raita',30),(4,'Extra Gravy',25),
 (5,'Paneer 65',120),(6,'Chicken 65',130),(7,'Boiled Egg',15),(8,'Papad',15),
 (9,'Extra Chutney',10),(10,'Gulab Jamun',40),(11,'Omelette',35),(12,'Gobi Manchurian',90),
 (13,'Extra Sambar',20),(14,'Butter Naan',40);

INSERT IGNORE INTO food_addons (food_id, addon_id) VALUES
 (1,5),(1,2),(1,1),(1,3),(1,4),
 (2,5),(2,2),(2,1),(2,3),(2,4),
 (3,12),(3,2),(3,1),
 (4,8),(4,3),(4,10),(4,2),(4,1),
 (5,9),(5,13),(5,2),(5,1),
 (6,4),(6,3),(6,2),(6,1),
 (7,14),(7,3),(7,2),(7,1),
 (8,1),(8,2),(8,6),(8,7),(8,3),(8,4),
 (9,1),(9,2),(9,6),(9,7),(9,3),(9,4),
 (10,3),(10,11),(10,2),(10,1),
 (11,6),(11,7),(11,3),(11,2),(11,1),
 (12,11),(12,2),(12,1),
 (13,3),(13,4),(13,2),(13,1),
 (14,6),(14,7),(14,8),(14,3),(14,2),(14,1);
