const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = __dirname;
const files = [
  'admin.html',
  'index.html',
  'articles/index.json',
  'articles/sample-listening-article.json'
];

for (const file of files) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Missing file: ${file}`);
  }
}

for (const file of ['articles/index.json', 'articles/sample-listening-article.json']) {
  JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
}

for (const file of ['admin.html', 'index.html']) {
  const html = fs.readFileSync(path.join(root, file), 'utf8');
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/gi)].map(match => match[1]);
  if (scripts.length === 0) {
    throw new Error(`No inline script found in ${file}`);
  }
  scripts.forEach((script, index) => {
    new vm.Script(script, { filename: `${file}#script-${index + 1}` });
  });
}

console.log('Static validation passed.');
