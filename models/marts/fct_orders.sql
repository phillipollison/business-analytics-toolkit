with orders as (

    select
        order_id,
        customer_id,
        order_date,
        date_trunc(order_date, month) as order_month,
        channel,
        revenue,
        refund_amount,
        revenue - refund_amount as net_revenue

    from {{ ref('stg_orders') }}

)

select *
from orders
