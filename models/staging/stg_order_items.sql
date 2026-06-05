select
    safe_cast(order_id as string) as order_id,
    safe_cast(product_id as string) as product_id,
    coalesce(safe_cast(quantity as numeric), 0) as quantity,
    coalesce(safe_cast(item_revenue as numeric), 0) as item_revenue

from {{ source('raw', 'order_items') }}
