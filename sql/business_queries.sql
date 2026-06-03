-- Total Revenue
SELECT SUM(sales_amount) AS total_revenue
FROM sales_raw;

-- Revenue By Category
SELECT
    category,
    SUM(sales_amount) AS revenue
FROM sales_raw
GROUP BY category;

-- Units Sold By Category
SELECT
    category,
    SUM(quantity_sold) AS units_sold
FROM sales_raw
GROUP BY category;

-- Top Products
SELECT
    product_name,
    SUM(sales_amount) AS revenue
FROM sales_raw
GROUP BY product_name
ORDER BY revenue DESC;
