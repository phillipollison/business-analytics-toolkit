with item_performance as (

    select
        product_id,
        sum(quantity) as quantity_sold,
        sum(item_revenue) as product_revenue,
        count(distinct order_id) as order_count

    from {{ ref('fct_order_items') }}

    group by 1

),

final as (

    select
        p.product_id,
        p.product_name,
        p.category,
        coalesce(i.quantity_sold, 0) as quantity_sold,
        coalesce(i.product_revenue, 0) as product_revenue,
        coalesce(i.order_count, 0) as order_count,
        safe_divide(i.product_revenue, i.quantity_sold) as revenue_per_unit

    from {{ ref('dim_products') }} p

    left join item_performance i
        on p.product_id = i.product_id

)

select *
from final
