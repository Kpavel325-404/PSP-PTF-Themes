'use strict';
// Independent reimport uses PTF Studio's unchanged reader, not the builder.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const modules = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const canvas = require(modules ? require.resolve('@napi-rs/canvas', { paths: [modules] }) : '@napi-rs/canvas');
const root = __dirname;
const source = fs.readFileSync(path.join(root, 'sources/ptf-app.js'), 'utf8');
const declarations = [...source.matchAll(/^(?:async )?function (\w+)\(/gm)];
function declaration(name) {
  const index = declarations.findIndex(m => m[1] === name);
  if (index < 0) throw new Error('Reader function absent: ' + name);
  const start = declarations[index].index;
  const next = declarations[index + 1]?.index || source.length;
  const text = source.slice(start, next);
  // These selected reader declarations have no subsequent UI initializers.
  return text.slice(0, text.lastIndexOf('}') + 1);
}
const functions = ['align', 'u16', 'u32', 'readFixedString', 'normalizeThemeColor', 'roleFor',
                   'decompressDeflate', 'parsePtf', 'decodeGim', 'countColors',
                   'readThemeColorRecord', 'readThemeColorFromPtf', 'verifyBuiltPtfMetadata'];
const sandbox = {
  console, TextEncoder, TextDecoder, ImageData: canvas.ImageData,
  CompressionStream, DecompressionStream, Response, Blob,
  window: { DecompressionStream },
  CATEGORY_LABELS: {}, FIRST_LABELS: {},
  decodeAsset: async asset => {
    if (asset.fileType === 5) {
      const decoded = context.decodeGim(asset.rawCurrent);
      asset.imageData = decoded.imageData;
      asset.gimMeta = decoded.meta;
      asset.paletteCount = decoded.paletteCount;
    } else {
      const image = await canvas.loadImage(Buffer.from(asset.rawCurrent));
      const target = canvas.createCanvas(image.width, image.height);
      const ctx = target.getContext('2d');
      ctx.drawImage(image, 0, 0);
      asset.imageData = ctx.getImageData(0, 0, image.width, image.height);
    }
  }
};
const context = vm.createContext(sandbox);
vm.runInContext(functions.map(declaration).join('\n'), context);
async function main() {
  const file = path.join(root, 'dist/Aero-Vista-Aurora.ptf');
  const bytes = new Uint8Array(fs.readFileSync(file));
  const parsed = await context.parsePtf(bytes.buffer, path.basename(file));
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'assets/manifest.json')));
  if (parsed.assets.length !== manifest.length) throw new Error('Asset count mismatch');
  const failures = [];
  const output = path.join(root, 'build/decoded');
  fs.mkdirSync(output, { recursive: true });
  for (const asset of parsed.assets) {
    const original = manifest.find(e => e.obj === asset.objIdx && e.sub === asset.subIdx);
    if (!original || asset.decodeError || !asset.imageData) {
      failures.push({ slot: `${asset.objIdx}:${asset.subIdx}`, error: asset.decodeError || 'Missing image' });
      continue;
    }
    if (asset.imageData.width !== original.size[0] || asset.imageData.height !== original.size[1]) failures.push({ slot: `${asset.objIdx}:${asset.subIdx}`, error: 'Dimensions changed' });
    if (asset.fileType === 5 && asset.gimMeta.format !== 3) failures.push({ slot: `${asset.objIdx}:${asset.subIdx}`, error: 'Palette format is not RGBA8888' });
    if (asset.fileType === 5 && asset.paletteCount > 256) failures.push({ slot: `${asset.objIdx}:${asset.subIdx}`, error: 'Palette exceeds 256' });
    if (original.focus && asset.paletteCount > 64) failures.push({ slot: `${asset.objIdx}:${asset.subIdx}`, error: 'Focus exceeds 64 colours' });
    fs.writeFileSync(path.join(output, original.file + '.rgba'), Buffer.from(asset.imageData.data));
    const c = canvas.createCanvas(asset.imageData.width, asset.imageData.height);
    c.getContext('2d').putImageData(asset.imageData, 0, 0);
    fs.writeFileSync(path.join(output, original.file), c.toBuffer('image/png'));
  }
  context.verifyBuiltPtfMetadata(bytes, { title: 'Aero Vista - Aurora', productId: 'KP_AERO_VISTA_AURORA', version: '1.0', themeColor: 7 });
  const report = {
    reader: 'PTF Studio 1.0 independent PTF/GIM reader + Skia BMP decoder',
    decodedAssets: parsed.assets.length,
    metadata: { title: parsed.theme.title, productId: parsed.theme.productId, version: parsed.theme.version, firmware: parsed.theme.pspVersion, color: parsed.theme.backgroundMode },
    failures
  };
  fs.writeFileSync(path.join(root, 'build/independent-verification.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  if (failures.length) process.exitCode = 1;
}
module.exports = { context, declaration, source };
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
