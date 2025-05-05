var express = require('express');
var app = express();
var redis = require('redis');

// Create a Redis client and connect
var client = redis.createClient({
    url: 'redis://redis:6379' // Assuming Redis container is named 'redis'
});

client.on("error", function (err) {
    console.error("Redis error", err);
});

// Connect to Redis
client.connect();

// Route to redirect to index.html
app.get('/', function (req, res) {
    res.redirect('/index.html');
});

// Route to fetch JSON data
app.get('/json', async function (req, res) {
    try {
        // Fetch the length of the 'wallet' hash
        const coins = await client.hLen('wallet');
        
        // Fetch the value of 'hashes'
        const hashes = await client.get('hashes');
        
        // Get the current time in seconds
        var now = Date.now() / 1000;
        
        // Respond with JSON data
        res.json({
            coins: coins,
            hashes: hashes,
            now: now
        });
    } catch (err) {
        console.error("Error fetching data from Redis:", err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Serve static files from the 'files' directory
app.use(express.static('files'));

// Start the server
var server = app.listen(80, function () {
    console.log('WEBUI running on port 80');
});
