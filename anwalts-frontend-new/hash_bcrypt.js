const bcrypt = require('bcryptjs');
const pwd = process.argv[2] || 'Test12345!';
const salt = bcrypt.genSaltSync(12);
const hash = bcrypt.hashSync(pwd, salt);
console.log(hash);
