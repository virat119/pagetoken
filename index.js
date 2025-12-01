const axios = require('axios');

const TMDB_KEY = process.env.TMDB_KEY || '20cb24189ce4f0a559576f52d344a825';

export default async function handler(req, res) {
  try {
    const url = `https://api.themoviedb.org/3${req.url}`;
    const response = await axios.get(url, {
      params: { ...req.query, api_key: TMDB_KEY },
      timeout: 9000
    });

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Content-Type', 'application/json');
    res.status(200).json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: error.message });
  }
}
