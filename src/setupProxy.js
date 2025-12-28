const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      // Use 127.0.0.1 instead of localhost to force IPv4
      target: 'http://127.0.0.1:8080',
      changeOrigin: true,
      logLevel: 'debug',
      onError: (err, req, res) => {
        console.error('Proxy error:', err.message);
        res.writeHead(500, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ 
          error: 'Backend connection error',
          message: 'Please wait for the backend to start...'
        }));
      },
      onProxyReq: (proxyReq, req, res) => {
        console.log(`Proxying ${req.method} ${req.url} to backend`);
      }
    })
  );
};

