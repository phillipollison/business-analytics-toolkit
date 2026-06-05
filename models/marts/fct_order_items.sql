with order_items as (

    select
        order_id,
        product_id,
        quantity,
        item_revenue

    from {{ ref('stg_order_items') }}

)

select *
from order_items
