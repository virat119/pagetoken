const http = require('http');
const axios = require('axios');
const url = require('url');

// 1. API Key Setup
// TMDB_KEY Environment Variable से Key लेगा। इसे Koyeb सेटिंग्स में सेट करें।
const TMDB_KEY = process.env.TMDB_KEY; 

// अगर TMDB_KEY सेट नहीं है, तो सर्वर को बंद कर दें।
if (!TMDB_KEY) {
  console.error("ERROR: TMDB_KEY environment variable is not set.");
  process.exit(1); 
}

const PORT = process.env.PORT || 3000;
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';

// 2. HTTP सर्वर हैंडलर
const server = http.createServer(async (req, res) => {
  // CORS Headers सेट करें
  res.setHeader('Access-Control-Allow-Origin', '*'); // सभी डोमेन को अनुमति दें
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Content-Type', 'application/json');

  // OPTIONS अनुरोध को तुरंत हैंडल करें (CORS Pre-flight request)
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }
  
  // सिर्फ GET अनुरोधों को अनुमति दें
  if (req.method !== 'GET') {
    res.writeHead(405);
    res.end(JSON.stringify({ error: 'Method Not Allowed' }));
    return;
  }

  try {
    // 3. Request URL और Query Parameters को पार्स करें
    const parsedUrl = url.parse(req.url, true);
    const apiPath = parsedUrl.pathname; // जैसे: /movie/popular
    const userQueries = parsedUrl.query; // जैसे: { language: 'en-US' }

    // 4. TMDB को कॉल करें
    const tmdbUrl = `${TMDB_BASE_URL}${apiPath}`;
    
    // API Key को query parameters में जोड़ें
    const response = await axios.get(tmdbUrl, {
      params: { ...userQueries, api_key: TMDB_KEY },
      timeout: 8000 // 8 सेकंड का टाइमआउट
    });

    // 5. TMDB का Response वापस भेजें
    res.writeHead(200);
    res.end(JSON.stringify(response.data));

  } catch (error) {
    // 6. Errors को हैंडल करें
    const statusCode = error.response?.status || 500;
    const errorMessage = error.response?.data?.status_message || error.message;

    res.writeHead(statusCode);
    res.end(JSON.stringify({ 
      error: 'Proxy Error',
      details: errorMessage,
      statusCode: statusCode 
    }));
  }
});

// 7. सर्वर शुरू करें
server.listen(PORT, () => {
  console.log(`TMDB Proxy Server running on port ${PORT}`);
  console.log(`Base URL: http://localhost:${PORT}/`);
});
