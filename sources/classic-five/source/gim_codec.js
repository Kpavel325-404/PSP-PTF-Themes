/* GPL-3.0-only: headless adapter to unmodified PTF Studio codec functions.
 * Upstream source and its GPL licence are included in vendor/ptf_studio.
 */
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const upstream=fs.readFileSync(path.join(root,'vendor/ptf_studio/app.js'),'utf8');
function section(start,end){
  const a=upstream.indexOf(start),b=upstream.indexOf(end,a+start.length);
  if(a<0||b<a)throw Error('Upstream codec boundary is missing: '+start);
  return upstream.slice(a,b);
}
class NativeImageData{
  constructor(data,width,height){this.data=data;this.width=width;this.height=height;}
}
class FixedDate extends Date{
  constructor(...args){super(...(args.length?args:['2026-10-09T09:45:00Z']));}
  toString(){return 'Fri Oct 09 2026 09:45:00 GMT+0000 (UTC)';}
}
const sandbox={TextEncoder,TextDecoder,ImageData:NativeImageData,Date:FixedDate};
vm.createContext(sandbox);
vm.runInContext(section('function align(','function normalizeThemeColor(')+
  section('function decodeGim(','function formatBytes(')+
  section('function quantize(','async function encodeAssetImage('),sandbox,{timeout:1000});
const manifest=JSON.parse(fs.readFileSync(path.join(root,'build/assets_manifest.json')));
let done=0;
for(const asset of manifest){
  const pixels=fs.readFileSync(asset.input);
  if(pixels.length!==asset.width*asset.height*4)throw Error('RGBA size mismatch');
  const imageData=new NativeImageData(new Uint8ClampedArray(pixels),asset.width,asset.height);
  const result=sandbox.encodeGimIndexed(imageData,false);
  fs.writeFileSync(asset.output,Buffer.from(result.bytes));
  const decoded=sandbox.decodeGim(result.bytes);
  if(decoded.imageData.width!==asset.width||decoded.imageData.height!==asset.height)throw Error('GIM dimensions mismatch');
  if(result.used>256)throw Error('Palette exceeds PSP limit');
  if(asset.role.endsWith('focus')&&result.used>64)throw Error('Focus palette exceeds conservative limit');
  fs.writeFileSync(asset.decoded,Buffer.from(decoded.imageData.data));
  asset.colors=result.used;asset.gim_bytes=result.bytes.length;
  if(++done%70===0)process.stdout.write(`Encoded ${done}/${manifest.length} graphics\n`);
}
fs.writeFileSync(path.join(root,'build/encoded_manifest.json'),JSON.stringify(manifest,null,2));
process.stdout.write(`GIM encode/decode passed: ${done} graphics\n`);
