CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) NOT NULL,  -- 'monthly' or 'yearly'
    status VARCHAR(50) NOT NULL,      -- 'active', 'grace_period', 'expired'
    start_date TIMESTAMP NOT NULL,
    expiry_date TIMESTAMP NOT NULL,
    grace_period_end TIMESTAMP NOT NULL,
    last_payment_date TIMESTAMP,
    next_payment_date TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    stripe_subscription_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_user_subscription UNIQUE (user_id)
);

-- Index for faster lookups
CREATE INDEX idx_user_id ON subscriptions(user_id);
CREATE INDEX idx_status ON subscriptions(status); 