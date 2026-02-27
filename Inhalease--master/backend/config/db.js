const mongoose = require('mongoose');

const connectDB = async () => {
    try {
        const conn = await mongoose.connect(process.env.MONGODB_URI);
        console.log(`MongoDB Connected: ${conn.connection.host}`);
    } catch (error) {
        console.error(`MongoDB connection Error: ${error.message}`);
        console.warn('⚠️ Warning: Server is running but database is not connected. API features depending on DB will fail. Please install & start MongoDB locally.');
        // Not gracefully exiting so that the application is still partially running:
        // process.exit(1); 
    }
};

module.exports = connectDB;
