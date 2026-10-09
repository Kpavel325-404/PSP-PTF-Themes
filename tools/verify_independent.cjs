/* SPDX-License-Identifier: GPL-3.0-only
 * Headless adapter to PTF Studio. The upstream parser is kept unmodified.
 * Full upstream source and licence: sources/classic-five/vendor/ptf_studio.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'sources/classic-five/vendor/ptf_studio/app.js'), 'utf8');
const declarations = [...source.matchAll(/^(?:async )?function (\w+)\(/gm)];
function declaration(name) {
  const i = declarations.findIndex(m => m[1] === name);
  if (i < 0) throw new Error('Upstream function missing: ' + name);
  const fragment = source.slice(declarations[i].index, declarations[i + 1]?.index || source.length);
  return fragment.slice(0, fragment.lastIndexOf('}') + 1);
}
class NativeImageData {
  constructor(data, width, height) { this.data = data; this.width = width; this.height = height; }
}
function decodeBmp24(raw) {
  const b = Buffer.from(raw);
  if (b.length < 54 || b.toString('ascii', 0, 2) !== 'BM' || b.readUInt16LE(28) !== 24 || b.readUInt32LE(30) !== 0)
    throw new Error('Independent decoder expects uncompressed BMP24');
  const width = b.readInt32LE(18), signedHeight = b.readInt32LE(22), height = Math.abs(signedHeight);
  if (width <= 0 || height <= 0 || width * height > 480 * 272) throw new Error('Invalid BMP dimensions');
  const begin = b.readUInt32LE(10), stride = Math.ceil(width * 3 / 4) * 4;
  if (begin + stride * height > b.length) throw new Error('BMP pixels exceed file');
  const rgba = new Uint8ClampedArray(width * height * 4);
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const p = begin + (signedHeight > 0 ? height - y - 1 : y) * stride + x * 3;
    const o = (y * width + x) * 4;
    rgba[o] = b[p + 2]; rgba[o + 1] = b[p + 1]; rgba[o + 2] = b[p]; rgba[o + 3] = 255;
  }
  return new NativeImageData(rgba, width, height);
}
function makeReader() {
  let context;
  const sandbox = {TextEncoder, TextDecoder, ImageData:NativeImageData, DecompressionStream, CompressionStream,
    Response, Blob, window:{DecompressionStream}, CATEGORY_LABELS:{}, FIRST_LABELS:{},
    decodeAsset: async asset => {
      if (asset.fileType === 5) {
        const decoded = context.decodeGim(asset.rawCurrent);
        asset.imageData = decoded.imageData; asset.gimMeta = decoded.meta; asset.paletteCount = decoded.paletteCount;
      } else if (asset.fileType === 4) asset.imageData = decodeBmp24(asset.rawCurrent);
      else throw new Error('Unexpected graphic format');
    }};
  context = vm.createContext(sandbox);
  const names = ['align', 'u16', 'u32', 'readFixedString', 'normalizeThemeColor', 'roleFor',
    'decompressDeflate', 'parsePtf', 'decodeGim', 'countColors'];
  vm.runInContext(names.map(declaration).join('\n'), context, {timeout:1000});
  return context;
}
async function main() {
  if (!process.argv[2]) throw new Error('An output directory is required');
  const destination = path.resolve(process.argv[2]);
  for (const theme of JSON.parse(fs.readFileSync(path.join(root, 'themes.json')))) {
    const reader = makeReader(), data = new Uint8Array(fs.readFileSync(path.join(root, 'PSP/THEME', theme.file)));
    const parsed = await reader.parsePtf(data.buffer, theme.file);
    const directory = path.join(destination, theme.slug);
    fs.mkdirSync(directory, {recursive:true});
    for (const asset of parsed.assets) {
      if (asset.decodeError || !asset.imageData) throw new Error(`${theme.file}: ${asset.decodeError || 'Missing decoded image'}`);
      const image = asset.imageData, role = asset.role;
      if (role.required && (image.width !== role.required[0] || image.height !== role.required[1])) throw new Error('Independent image size mismatch');
      const rgba = Buffer.from(image.data);
      for (let p = 0; p < rgba.length; p += 4) if (!rgba[p + 3]) rgba.fill(0, p, p + 3);
      fs.writeFileSync(path.join(directory, `${asset.objIdx}_${asset.subIdx}.rgba`), rgba);
    }
    fs.writeFileSync(path.join(directory, 'reader.json'), JSON.stringify({graphics:parsed.assets.length,
      metadata:{title:parsed.theme.title, productId:parsed.theme.productId, version:parsed.theme.version,
        color:parsed.theme.backgroundMode}}, null, 2));
  }
}
main().catch(error => { process.stderr.write(error.stack + '\n'); process.exit(1); });
