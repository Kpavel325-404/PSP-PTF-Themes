'use strict';
const fs = require('fs');
const path = require('path');
const modules = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const sharp = require(modules ? require.resolve('sharp', { paths: [modules] }) : 'sharp');
const root = __dirname;
const assets = path.join(root, 'assets');
const output = path.join(assets, 'indexed');
fs.mkdirSync(output, { recursive: true });
const manifest = JSON.parse(fs.readFileSync(path.join(assets, 'manifest.json')));
(async () => {
  let count = 0;
  for (const item of manifest) {
    if ((item.obj === 0 && item.sub === 1) || item.obj === 1) continue;
    const source = path.join(assets, item.file);
    const dest = path.join(output, item.file);
    if (item.focus) fs.copyFileSync(source, dest);
    else await sharp(source).png({ palette: true, colours: 256, dither: 0, effort: 10 }).toFile(dest);
    count++;
  }
  console.log(JSON.stringify({ indexedIconAssets: count, encoder: 'libimagequant via sharp', dithering: false }));
})().catch(e => { console.error(e); process.exit(1); });
