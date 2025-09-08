-- backend/shared/sql/init.sql
-- Database initialization script for Trading Platform

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set default schema
SET search_path TO trading, public;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    role VARCHAR(20) DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN', 'TRADER', 'ANALYST')),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED', 'PENDING_VERIFICATION', 'CLOSED')),
    kyc_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('MARKET', 'LIMIT', 'STOP_LOSS', 'STOP_LIMIT', 'TAKE_PROFIT')),
    side VARCHAR(10) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity DECIMAL(20,8) NOT NULL CHECK (quantity > 0),
    price DECIMAL(20,8),
    filled_quantity DECIMAL(20,8) DEFAULT 0 CHECK (filled_quantity >= 0),
    remaining_quantity DECIMAL(20,8) CHECK (remaining_quantity >= 0),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'OPEN', 'PARTIALLY_FILLED', 'FILLED', 'CANCELLED', 'REJECTED', 'EXPIRED')),
    time_in_force VARCHAR(10) DEFAULT 'GTC' CHECK (time_in_force IN ('GTC', 'IOC', 'FOK')),
    stop_price DECIMAL(20,8),
    average_fill_price DECIMAL(20,8),
    commission DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity DECIMAL(20,8) NOT NULL CHECK (quantity > 0),
    price DECIMAL(20,8) NOT NULL CHECK (price > 0),
    commission DECIMAL(20,8) DEFAULT 0,
    commission_asset VARCHAR(10) DEFAULT 'USDT',
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Balances table
CREATE TABLE IF NOT EXISTS balances (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    asset VARCHAR(10) NOT NULL,
    available_balance DECIMAL(20,8) DEFAULT 0 CHECK (available_balance >= 0),
    locked_balance DECIMAL(20,8) DEFAULT 0 CHECK (locked_balance >= 0),
    total_balance DECIMAL(20,8) GENERATED ALWAYS AS (available_balance + locked_balance) STORED,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, asset)
);

-- Market data table (for historical data)
CREATE TABLE IF NOT EXISTS market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8),
    bid DECIMAL(20,8),
    ask DECIMAL(20,8),
    high_24h DECIMAL(20,8),
    low_24h DECIMAL(20,8),
    change_24h DECIMAL(10,4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candlestick data table
CREATE TABLE IF NOT EXISTS candlestick_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    close_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    UNIQUE(symbol, timeframe, timestamp)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_order_id ON trades(order_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_balances_user_id ON balances(user_id);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_candlestick_symbol_timeframe ON candlestick_data(symbol, timeframe);
CREATE INDEX IF NOT EXISTS idx_candlestick_timestamp ON candlestick_data(timestamp);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_balances_updated_at BEFORE UPDATE ON balances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data
INSERT INTO users (email, password, first_name, last_name, role) VALUES
('admin@trading.com', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iYqiSfFVMLkMvTl8vBGE7BVaQPT6', 'Admin', 'User', 'ADMIN'),
('trader@trading.com', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iYqiSfFVMLkMvTl8vBGE7BVaQPT6', 'Demo', 'Trader', 'TRADER'),
('user@trading.com', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iYqiSfFVMLkMvTl8vBGE7BVaQPT6', 'Demo', 'User', 'USER')
ON CONFLICT (email) DO NOTHING;

-- Insert sample balances
INSERT INTO balances (user_id, asset, available_balance) VALUES
(1, 'USDT', 10000.00000000),
(1, 'BTC', 1.00000000),
(1, 'ETH', 10.00000000),
(2, 'USDT', 5000.00000000),
(2, 'BTC', 0.50000000),
(2, 'ETH', 5.00000000),
(3, 'USDT', 1000.00000000),
(3, 'BTC', 0.10000000),
(3, 'ETH', 1.00000000)
ON CONFLICT (user_id, asset) DO NOTHING;

-- Create a view for order book
CREATE OR REPLACE VIEW order_book AS
SELECT 
    symbol,
    side,
    price,
    SUM(remaining_quantity) as total_quantity,
    COUNT(*) as order_count
FROM orders
WHERE status IN ('OPEN', 'PARTIALLY_FILLED')
GROUP BY symbol, side, price
ORDER BY symbol, side, price;

COMMENT ON DATABASE trading_platform IS 'Trading Platform Database';
COMMENT ON TABLE users IS 'User accounts and authentication data';
COMMENT ON TABLE orders IS 'Trading orders placed by users';
COMMENT ON TABLE trades IS 'Executed trades history';
COMMENT ON TABLE balances IS 'User account balances by asset';
COMMENT ON TABLE market_data IS 'Real-time and historical market data';
COMMENT ON TABLE candlestick_data IS 'OHLCV candlestick data for charting';