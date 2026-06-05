with customers as (

    select
        customer_id,
        customer_email,
        first_order_date,
        customer_segment

    from {{ ref('stg_customers') }}

)

select *
from customers
