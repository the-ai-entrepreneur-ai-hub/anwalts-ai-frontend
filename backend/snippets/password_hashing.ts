// Node.js example preserving legacy bcrypt with on-login rehash capability
import bcrypt from 'bcryptjs';

const LEGACY_COST = Number(process.env.BCRYPT_COST || 12);

export async function hashPassword(plain: string) {
  return bcrypt.hash(plain, LEGACY_COST);
}

export async function verifyPassword(plain: string, hash: string) {
  // Supports legacy bcrypt hashes; if algorithm changed, extend detect
  const isValid = await bcrypt.compare(plain, hash);
  return isValid;
}

export async function verifyAndRehash(plain: string, hash: string) {
  const valid = await verifyPassword(plain, hash);
  if (!valid) return { valid: false, hash: undefined };

  // Optionally rehash if cost changed
  const currentRounds = getBcryptRounds(hash);
  if (currentRounds !== LEGACY_COST) {
    const newHash = await hashPassword(plain);
    return { valid: true, hash: newHash };
  }
  return { valid: true, hash: undefined };
}

function getBcryptRounds(hash: string) {
  const parts = hash.split('$');
  const rounds = Number(parts[2]);
  return rounds;
}
