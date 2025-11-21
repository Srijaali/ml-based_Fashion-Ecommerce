-- Log customer activity into event table

CREATE OR REPLACE FUNCTION niche_data.fn_log_customer_event()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO niche_data.events (customer_id, article_id, event_type, created_at)
    VALUES (
        NEW.customer_id,
        COALESCE(NEW.article_id, NULL),
        TG_ARGV[0],     -- event type passed in trigger
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION niche_data.fn_log_customer_event()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO niche_data.events (customer_id, article_id, event_type, created_at)
    VALUES (
        NEW.customer_id,
        COALESCE(NEW.article_id, NULL),
        TG_ARGV[0],     -- event type passed in trigger
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_event_review
AFTER INSERT ON niche_data.reviews
FOR EACH ROW
EXECUTE FUNCTION niche_data.fn_log_customer_event('review');


CREATE TRIGGER trg_event_wishlist
AFTER INSERT ON niche_data.wishlist
FOR EACH ROW
EXECUTE FUNCTION niche_data.fn_log_customer_event('wishlist');


CREATE TRIGGER trg_event_add_to_cart
AFTER INSERT OR UPDATE ON niche_data.cart
FOR EACH ROW
EXECUTE FUNCTION niche_data.fn_log_customer_event('add_to_cart');



CREATE TRIGGER trg_event_order_item
AFTER INSERT ON niche_data.order_items
FOR EACH ROW
EXECUTE FUNCTION niche_data.fn_log_customer_event('order_item');
