// Example Express.js middleware preserving legacy cookies/JWT names and 401 handling
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

// Preserve original cookie/header names
const COOKIE_NAME = process.env.SESSION_COOKIE_NAME || 'sid';
const AUTH_HEADER = 'authorization';
const JWT_PUBLIC_KEY = process.env.JWT_PUBLIC_KEY || '';

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  try {
    const header = req.headers[AUTH_HEADER] as string | undefined;
    const bearer = header && header.startsWith('Bearer ') ? header.slice(7) : undefined;
    const cookieToken = req.cookies?.[COOKIE_NAME];
    const token = bearer || cookieToken;

    if (!token) {
      return res.status(401).json({ error: 'unauthorized' });
    }

    const payload = jwt.verify(token, JWT_PUBLIC_KEY, { algorithms: ['RS256', 'HS256'] });
    (req as any).user = payload;
    return next();
  } catch (err) {
    return res.status(401).json({ error: 'unauthorized' });
  }
}

// Attach to API routes powering /dashboard
// app.use('/api', requireAuth)
