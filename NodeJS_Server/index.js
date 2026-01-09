// 1. Import Express
const express = require('express');

// 2. Initialize the app
const app = express();

// 3. Define a port
const PORT = 3000;

// 4. Middleware (Optional but common)
// Allows us to read JSON data sent in requests
app.use(express.json()); 

// 5. Define a Route (Endpoint)
// When someone visits 'http://localhost:3000/', run this function
app.get('/', (req, res) => {
    res.send('Hello from the Backend!');
});

// 6. Start the Server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});