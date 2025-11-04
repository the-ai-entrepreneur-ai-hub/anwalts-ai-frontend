/**
 * Security Middleware
 * Security headers and HTTPS enforcement
 */

const helmet = require('helmet');

/**
 * Configure helmet security headers
 */
const securityHeaders = helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
  hsts: {
    maxAge: 31536000, // 1 year
    includeSubDomains: true,
    preload: true,
  },
});

/**
 * Force HTTPS in production
 */
function forceHttps(req, res, next) {
  if (process.env.NODE_ENV !== 'production') {
    return next();
  }

  const protoHeader = req.headers['x-forwarded-proto'];
  const proto = Array.isArray(protoHeader)
    ? protoHeader[0]
    : (protoHeader || '').split(',')[0].trim();

  if (proto && proto.toLowerCase() === 'https') {
    return next();
  }

  if (req.protocol === 'https') {
    return next();
  }

  const host = req.headers['x-forwarded-host'] || req.headers.host || req.hostname;
  return res.redirect(301, `https://${host}${req.url}`);
}

/**
 * Add security-related headers
 */
function additionalSecurityHeaders(req, res, next) {
  // Prevent clickjacking
  res.setHeader('X-Frame-Options', 'DENY');
  
  // Prevent MIME type sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');
  
  // XSS protection (legacy but still good)
  res.setHeader('X-XSS-Protection', '1; mode=block');
  
  next();
}

module.exports = {
  securityHeaders,
  forceHttps,
  additionalSecurityHeaders,
};
