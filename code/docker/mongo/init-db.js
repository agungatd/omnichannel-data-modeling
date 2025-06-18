// This script will be executed when the MongoDB container starts for the first time.
db = db.getSiblingDB('shopsphere');

db.createCollection('marketplace_orders');

db.marketplace_orders.insertMany([
    {
        mp_order_id: 'ORD-TP-XYZ',
        user_email: 'rianti.new@example.com',
        platform: 'tokopedia',
        product_name: 'Baju Kemeja Pria',
        order_time: new Date('2024-01-05T11:00:00Z'),
        amount: 210000
    },
    {
        mp_order_id: 'ORD-SHP-ABC',
        user_email: 'agung@example.com',
        platform: 'shopee',
        product_name: 'Sepatu Lari',
        order_time: new Date('2024-01-06T14:20:00Z'),
        amount: 350000
    }
]);
