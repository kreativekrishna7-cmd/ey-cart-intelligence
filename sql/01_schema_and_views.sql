CREATE DATABASE ey_cart;

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_segment VARCHAR(30) NOT NULL,
    region VARCHAR(20) NOT NULL,
    city VARCHAR(80) NOT NULL,
    age_group VARCHAR(20),
    acquisition_channel VARCHAR(30),
    signup_date DATE
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(80) NOT NULL,
    subcategory VARCHAR(80),
    brand VARCHAR(80),
    cost_price NUMERIC(12,2) NOT NULL,
    selling_price NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(20) PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    region VARCHAR(20) NOT NULL,
    city VARCHAR(80) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL,
    discount NUMERIC(12,2) NOT NULL DEFAULT 0,
    revenue NUMERIC(14,2) NOT NULL,
    cost NUMERIC(14,2) NOT NULL,
    profit NUMERIC(14,2) NOT NULL,
    payment_method VARCHAR(30),
    order_status VARCHAR(30),
    fulfillment_type VARCHAR(30),
    device VARCHAR(30),
    gross_sales NUMERIC(14,2),
    order_month VARCHAR(7)
);

CREATE TABLE IF NOT EXISTS marketing_campaigns (
    campaign_id VARCHAR(20) PRIMARY KEY,
    campaign_date DATE NOT NULL,
    campaign_name VARCHAR(200) NOT NULL,
    marketing_channel VARCHAR(50) NOT NULL,
    region VARCHAR(20) NOT NULL,
    spend NUMERIC(14,2) NOT NULL,
    impressions BIGINT NOT NULL,
    clicks BIGINT NOT NULL,
    conversions BIGINT NOT NULL,
    revenue NUMERIC(14,2) NOT NULL,
    ctr NUMERIC(10,6),
    conversion_rate NUMERIC(10,6),
    roas NUMERIC(12,2),
    cac NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id VARCHAR(30) PRIMARY KEY,
    date DATE NOT NULL,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    warehouse VARCHAR(50) NOT NULL,
    opening_stock INTEGER NOT NULL,
    units_received INTEGER NOT NULL,
    units_sold INTEGER NOT NULL,
    closing_stock INTEGER NOT NULL,
    stockout BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS returns (
    return_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL REFERENCES orders(order_id),
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    return_date DATE NOT NULL,
    return_reason VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    refund_amount NUMERIC(14,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_region ON orders(region);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_month ON orders(order_month);
CREATE INDEX IF NOT EXISTS idx_inventory_date ON inventory(date);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_returns_date ON returns(return_date);
CREATE INDEX IF NOT EXISTS idx_returns_product ON returns(product_id);
CREATE INDEX IF NOT EXISTS idx_marketing_date ON marketing_campaigns(campaign_date);
CREATE INDEX IF NOT EXISTS idx_marketing_region ON marketing_campaigns(region);

CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    DATE_TRUNC('month', order_date)::date AS month,
    SUM(revenue) FILTER (WHERE order_status = 'Delivered') AS revenue,
    SUM(profit) FILTER (WHERE order_status = 'Delivered') AS profit,
    SUM(quantity) FILTER (WHERE order_status = 'Delivered') AS units_sold,
    COUNT(*) FILTER (WHERE order_status = 'Delivered') AS orders,
    ROUND(
        SUM(revenue) FILTER (WHERE order_status = 'Delivered')
        / NULLIF(COUNT(*) FILTER (WHERE order_status = 'Delivered'), 0), 2
    ) AS aov
FROM orders
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    p.category,
    SUM(o.revenue) FILTER (WHERE o.order_status = 'Delivered') AS revenue,
    SUM(o.profit) FILTER (WHERE o.order_status = 'Delivered') AS profit,
    SUM(o.quantity) FILTER (WHERE o.order_status = 'Delivered') AS units_sold,
    COUNT(*) FILTER (WHERE o.order_status = 'Delivered') AS orders,
    ROUND(
        100 * SUM(o.profit) FILTER (WHERE o.order_status = 'Delivered')
        / NULLIF(SUM(o.revenue) FILTER (WHERE o.order_status = 'Delivered'), 0), 2
    ) AS margin_percent
FROM orders o
JOIN products p ON p.product_id = o.product_id
GROUP BY p.category;

CREATE OR REPLACE VIEW vw_region_performance AS
SELECT
    region,
    SUM(revenue) FILTER (WHERE order_status = 'Delivered') AS revenue,
    SUM(profit) FILTER (WHERE order_status = 'Delivered') AS profit,
    COUNT(*) FILTER (WHERE order_status = 'Delivered') AS orders,
    SUM(quantity) FILTER (WHERE order_status = 'Delivered') AS units_sold
FROM orders
GROUP BY region;

CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    SUM(o.revenue) FILTER (WHERE o.order_status = 'Delivered') AS revenue,
    SUM(o.profit) FILTER (WHERE o.order_status = 'Delivered') AS profit,
    SUM(o.quantity) FILTER (WHERE o.order_status = 'Delivered') AS units_sold,
    COUNT(*) FILTER (WHERE o.order_status = 'Delivered') AS orders
FROM products p
LEFT JOIN orders o ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.brand;

CREATE OR REPLACE VIEW vw_customer_segment_performance AS
SELECT
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(o.order_id) FILTER (WHERE o.order_status = 'Delivered') AS orders,
    COALESCE(SUM(o.revenue) FILTER (WHERE o.order_status = 'Delivered'), 0) AS revenue,
    COALESCE(SUM(o.profit) FILTER (WHERE o.order_status = 'Delivered'), 0) AS profit
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_segment;

CREATE OR REPLACE VIEW vw_marketing_performance AS
SELECT
    marketing_channel,
    region,
    SUM(spend) AS spend,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(conversions) AS conversions,
    SUM(revenue) AS revenue,
    ROUND(SUM(revenue) / NULLIF(SUM(spend),0), 2) AS roas,
    ROUND(SUM(spend) / NULLIF(SUM(conversions),0), 2) AS cac
FROM marketing_campaigns
GROUP BY marketing_channel, region;

CREATE OR REPLACE VIEW vw_inventory_risk AS
SELECT
    i.product_id,
    p.product_name,
    p.category,
    COUNT(*) AS snapshots,
    SUM(CASE WHEN i.stockout THEN 1 ELSE 0 END) AS stockout_snapshots,
    ROUND(AVG(i.closing_stock), 2) AS avg_closing_stock,
    SUM(i.units_sold) AS units_sold
FROM inventory i
JOIN products p ON p.product_id = i.product_id
GROUP BY i.product_id, p.product_name, p.category;

CREATE OR REPLACE VIEW vw_return_performance AS
SELECT
    p.category,
    r.return_reason,
    COUNT(*) AS return_count,
    SUM(r.quantity) AS returned_units,
    SUM(r.refund_amount) AS refund_amount
FROM returns r
JOIN products p ON p.product_id = r.product_id
GROUP BY p.category, r.return_reason;
