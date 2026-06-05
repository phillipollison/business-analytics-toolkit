with customer_orders as (

    select
        customer_id,
        count(distinct order_id) as orders,
        sum(net_revenue) as lifetime_revenue,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date

    from {{ ref('fct_orders') }}

    group by 1

),

final as (

    select
        c.customer_id,
        c.customer_email,
        c.customer_segment,
        coalesce(o.orders, 0) as orders,
        coalesce(o.lifetime_revenue, 0) as lifetime_revenue,
        safe_divide(o.lifetime_revenue, o.orders) as average_order_value,
        o.first_order_date,
        o.last_order_date,
        case
            when coalesce(o.orders, 0) > 1 then 'Repeat'
            when coalesce(o.orders, 0) = 1 then 'One-Time'
            else 'No Orders'
        end as customer_type

    from {{ ref('dim_customers') }} c

    left join customer_orders o
        on c.customer_id = o.customer_id

)

select *
from final
