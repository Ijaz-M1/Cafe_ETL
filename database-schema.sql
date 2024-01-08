CREATE TABLE products (
  product_id VARCHAR(255) PRIMARY KEY NOT NULL,
  product_name VARCHAR(255) NOT NULL,
  product_flavour VARCHAR(255),
  product_size VARCHAR(255),
  price NUMERIC(10, 2) NOT NULL,
  CHECK (price >= 0)
);

CREATE TABLE branches (
  branch_id VARCHAR(255) PRIMARY KEY NOT NULL,
  branch_location VARCHAR(255)
);

  CREATE TABLE orders (
  order_id VARCHAR(255) PRIMARY KEY NOT NULL,
  order_date_time VARCHAR(255),
  branch_id VARCHAR(255),
  FOREIGN KEY(branch_id) REFERENCES branches(branch_id),
  customer_id VARCHAR(255),
  total_spend INT NOT NULL,
  payment_method VARCHAR(20)
);

CREATE TABLE orders_details (
  PRIMARY KEY (order_id, product_id),
  order_id VARCHAR(255),
  product_id VARCHAR(255),
  FOREIGN KEY(order_id) REFERENCES orders(order_id),
  FOREIGN KEY(product_id) REFERENCES products(product_id)
);