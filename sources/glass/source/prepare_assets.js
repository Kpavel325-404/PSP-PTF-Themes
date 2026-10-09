'use strict';
// Original vector artwork for the KP theme collection.
const fs = require('fs');
const path = require('path');
const modulePaths = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const sharp = require(modulePaths ? require.resolve('sharp', {paths:[modulePaths]}) : 'sharp');
const root = path.resolve(__dirname, '..');
const themes = JSON.parse(fs.readFileSync(path.join(root, 'themes.json')));

const categories = {
  0:['Default','gem'], 1:['Settings','gear'], 2:['Photo','photo'],
  3:['Music','music'], 4:['Video','video'], 5:['TV','tv'],
  6:['Game','game'], 7:['Network','globe'], 8:['Extras','star']
};
const first = {
  2:['Memory Stick','memory'], 4:['UMD','disc'], 6:['Camera','camera'],
  8:['Game Sharing','share'], 10:['Saved Data Utility','save'],
  12:['UMD Update','discupdate'], 14:['System Update','update'],
  16:['USB Connection','usb'], 18:['Video Settings','videosettings'],
  20:['Photo Settings','photosettings'], 22:['System Settings','gear'],
  24:['Theme Settings','palette'], 26:['Date and Time','clock'],
  28:['Power Save Settings','battery'], 30:['External Display','tv'],
  32:['Sound Settings','speaker'], 34:['Security Settings','shield'],
  36:['RSS Channel Settings','rsssettings'], 38:['Network Settings','wifi'],
  40:['Online Instruction Manuals','book'], 42:['Remote Play','remote'],
  44:['Internet Radio','radio'], 46:['RSS Channel','rss'],
  48:['Internet Browser','browser'], 50:['Internet Search','search'],
  52:['Account Management','account'], 54:['Default / Fallback','gem'],
  56:['Bluetooth Settings','bluetooth'], 58:['SensMe Channels','heartmusic']
};
const candyColors = {
  gear:'#c4adfa', photo:'#ffbcaa', music:'#f3a0ce', video:'#a0cbfb',
  tv:'#a4e5d7', game:'#eeb0df', globe:'#99dfeb', star:'#f1dca0', gem:'#d8baf6'
};

function attrs(t) {
  return `fill="url(#body)" stroke="${t.rim}" stroke-width="1.4" stroke-linejoin="round"`;
}
function art(type,t) {
  const a=attrs(t), dark='#153c59', white='#f4fcff';
  const line = (d,w=2.4,color=white) => `<path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`;
  const rect = (x,y,w,h,r=4) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" ${a}/>`;
  const circ = (x,y,r) => `<circle cx="${x}" cy="${y}" r="${r}" ${a}/>`;
  const gear = () => {
    let d='';
    for(let i=0;i<48;i++){
      const theta=(i/48)*Math.PI*2-Math.PI/2;
      const radial=[21,21,16.8,16.8][i%4];
      d+=`${i?'L':'M'}${(32+Math.cos(theta)*radial).toFixed(3)},${(32+Math.sin(theta)*radial).toFixed(3)} `;
    }
    return `<path d="${d}Z" ${a}/><circle cx="32" cy="32" r="10" fill="url(#chrome)" stroke="#627b92" stroke-width="1.8"/><circle cx="32" cy="32" r="4.8" fill="${t.deep}" stroke="${t.rim}" stroke-width="1.5"/>`;
  };
  const photo = () => `<g transform="rotate(-9 32 32)">${rect(11,16,40,33,3)}<rect x="15" y="20" width="32" height="21" rx="1" fill="#153e68"/><circle cx="39" cy="26" r="3.4" fill="#ffe7ad"/><path d="M15 40L25 28L33 37L38 31L47 41Z" fill="#94e6d0"/><path d="M17 46H45" stroke="${white}" stroke-width="1.5"/></g>`;
  const video = () => `${rect(11,18,42,32,4)}<path d="M12 18L14 9L55 16L53 25Z" fill="url(#chrome)" stroke="${t.rim}" stroke-width="1.5"/><path d="M20 10L24 20M33 12L37 22M46 14L50 24" stroke="#33556c" stroke-width="4"/><path d="M27 29L40 36L27 44Z" fill="${white}" opacity=".94"/>`;
  const music = () => `<path d="M27 17L48 11V40C48 48 35 49 35 42C35 36 42 34 44 36V21L27 26V46C27 54 14 55 14 48C14 41 21 40 23 42V21Z" ${a}/>${line('M27 18L45 13',1.5)}`;
  const cassette = () => `${rect(9,17,46,32,5)}<rect x="14" y="23" width="36" height="16" rx="4" fill="#142c43" stroke="${t.rim}" stroke-width="1"/><circle cx="23" cy="31" r="5.3" fill="url(#chrome)"/><circle cx="41" cy="31" r="5.3" fill="url(#chrome)"/><circle cx="23" cy="31" r="2.4" fill="#15304a"/><circle cx="41" cy="31" r="2.4" fill="#15304a"/><path d="M19 48L23 41H41L45 48Z" fill="url(#chrome)"/><circle cx="14" cy="21" r="1.1" fill="${white}"/><circle cx="50" cy="21" r="1.1" fill="${white}"/>`;
  const vhs = () => `${rect(9,18,46,30,3)}<rect x="14" y="24" width="36" height="13" rx="2" fill="#152d43" stroke="${t.rim}"/><circle cx="22" cy="30.5" r="4" fill="url(#chrome)"/><circle cx="42" cy="30.5" r="4" fill="url(#chrome)"/><path d="M18 43H46" stroke="${white}" stroke-width="2"/>`;
  const tv = () => `${rect(10,16,44,31,5)}<rect x="15" y="21" width="30" height="20" rx="3" fill="#164770"/><path d="M19 39L40 24" stroke="${t.rim}" stroke-width="1.8" opacity=".7"/><circle cx="49" cy="26" r="1.6" fill="${white}"/><path d="M24 52H40M32 47V52" stroke="${t.rim}" stroke-width="3" stroke-linecap="round"/>${line('M24 8L32 16L40 8',2)}`;
  const game = () => `<path d="M20 19H44C50 19 52 24 55 37C59 55 48 54 41 44H23C16 54 5 54 9 38C12 24 14 19 20 19Z" ${a}/><path d="M21 26V38M15 32H27" stroke="#163c59" stroke-width="4" stroke-linecap="round"/><path d="M21 26V38M15 32H27" stroke="${white}" stroke-width="2.4" stroke-linecap="round"/><circle cx="42" cy="29" r="2.4" fill="#f7d9a4"/><circle cx="49" cy="35" r="2.4" fill="#e1f9ff"/><circle cx="35" cy="38" r="2.7" fill="#275b7e"/><path d="M29 27H34" stroke="${white}" stroke-width="1.5"/>`;
  const globe = () => `${circ(32,31,22)}<ellipse cx="32" cy="31" rx="10" ry="22" fill="none" stroke="${t.rim}" stroke-width="1.7"/><ellipse cx="32" cy="31" rx="21" ry="8.5" fill="none" stroke="${t.rim}" stroke-width="1.7"/>${line('M10 31H54M32 9V53',1.7)}`;
  const gem = () => `<path d="M32 7L51 19L51 43L32 56L13 43V19Z" ${a}/><path d="M32 7V32L13 19M32 32L51 19M32 32V56M32 32L13 43M32 32L51 43" stroke="${t.rim}" stroke-width="1.4" opacity=".65"/>`;
  const star = () => `<path d="M32 8L38.8 22L54 24.2L43 35L45.6 50.6L32 43.3L18.4 50.6L21 35L10 24.2L25.2 22Z" ${a}/>${line('M32 13L35 24L45 26',1.6)}`;
  const disc = () => `${circ(32,32,23)}<path d="M15 17C24 6 38 7 47 17M17 48C26 56 41 54 48 44" fill="none" stroke="${t.rim}" stroke-width="2.5" opacity=".6"/><circle cx="32" cy="32" r="7" fill="url(#chrome)" stroke="#7c93a8"/><circle cx="32" cy="32" r="3" fill="#284766"/>`;
  const update = () => `${circ(32,32,21)}${line('M19 29C20 20 32 15 42 23M45 35C43 45 31 49 22 40',3.4)}<path d="M43 17L45 27L35 26M20 46L18 36L28 37" fill="${white}"/>`;
  const memory = () => `<path d="M19 9H41L46 15V54H18V10Z" ${a}/><path d="M23 10V20M29 10V20M35 10V20M41 13V20" stroke="#ffeab4" stroke-width="3"/><rect x="23" y="28" width="18" height="15" rx="2" fill="#164470" stroke="${t.rim}"/><path d="M26 48H38" stroke="${white}" stroke-width="2"/>`;
  const camera = () => `<path d="M12 21H23L27 14H39L43 21H53V48H11V24Z" ${a}/><circle cx="32" cy="34" r="11" fill="url(#chrome)" stroke="#385b76"/><circle cx="32" cy="34" r="7.5" fill="#16486e"/><circle cx="30" cy="31" r="2.6" fill="#cdf7ff" opacity=".8"/><rect x="44" y="25" width="5" height="3" rx="1" fill="#fff2c8"/>`;
  const save = () => `${rect(13,10,38,44,3)}<path d="M20 10H42V26H20Z" fill="url(#chrome)"/><rect x="33" y="12" width="5" height="10" fill="#25475d"/><rect x="20" y="34" width="24" height="20" rx="2" fill="#f1f7fa"/><path d="M24 40H40M24 45H40" stroke="#8cb0c3" stroke-width="1.5"/>`;
  const usb = () => `<path d="M29 55V33L17 26V18M29 42L44 34V24M29 33V12" fill="none" stroke="${t.deep}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>${line('M29 55V33L17 26V18M29 42L44 34V24M29 33V12',5)}<path d="M22 14L29 4L36 14Z" ${a}/><circle cx="17" cy="15" r="4.5" ${a}/><rect x="40" y="18" width="8" height="8" rx="1" ${a}/>`;
  const palette = () => `<path d="M32 9C46 9 55 18 55 32C55 43 50 45 42 41C34 37 35 42 36 46C40 58 18 58 11 42C2 23 13 9 32 9Z" ${a}/><circle cx="22" cy="22" r="4" fill="#ffd5b1"/><circle cx="36" cy="19" r="4" fill="#c3f3d9"/><circle cx="46" cy="28" r="4" fill="#e8d4ff"/><circle cx="19" cy="37" r="4" fill="#b8e4ff"/><circle cx="28" cy="47" r="4" fill="#1c4667"/>`;
  const clock = () => `${circ(32,32,22)}<circle cx="32" cy="32" r="17" fill="url(#chrome)" stroke="#6395ad"/>${line('M32 17V32L43 38',3,'#174364')}<path d="M32 13V17M32 47V51M13 32H17M47 32H51" stroke="#3b6178" stroke-width="2"/>`;
  const battery = () => `${rect(11,20,40,26,4)}<rect x="51" y="27" width="5" height="12" rx="2" fill="url(#chrome)"/><path d="M35 23L24 35H32L29 44L42 30H34Z" fill="#f5ffd6" stroke="#668b68" stroke-width=".6"/>`;
  const speaker = () => `<path d="M11 25H22L35 13V51L22 39H11Z" ${a}/>${line('M42 24C48 29 48 36 42 41M48 16C60 25 60 40 48 49',3)}${line('M25 26V38',1.2)}`;
  const shield = () => `<path d="M32 8L52 16V32C52 43 43 52 32 57C20 52 11 43 11 32V16Z" ${a}/><path d="M21 33L28 40L43 24" fill="none" stroke="${white}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>`;
  const rss = () => `<circle cx="16" cy="47" r="5" ${a}/><path d="M11 28C25 28 36 39 36 53M11 11C34 11 53 30 53 53" fill="none" stroke="${t.deep}" stroke-width="9"/><path d="M11 28C25 28 36 39 36 53M11 11C34 11 53 30 53 53" fill="none" stroke="url(#body)" stroke-width="6"/>`;
  const wifi = () => `${circ(32,32,23)}${line('M15 27Q32 13 49 27M21 35Q32 25 43 35M27 42Q32 38 37 42',3.3)}<circle cx="32" cy="49" r="2.9" fill="${white}"/>`;
  const book = () => `<path d="M8 13C17 10 25 12 32 17C39 12 47 10 56 13V49C46 47 39 48 32 53C25 48 18 47 8 49Z" ${a}/><path d="M32 17V53M13 23Q21 21 27 25M13 31Q21 29 27 33M38 25Q46 21 51 23M38 33Q46 29 51 31" fill="none" stroke="${t.rim}" stroke-width="1.7"/>`;
  const radio = () => `${rect(10,22,44,29,4)}${line('M19 22L45 9',2.7)}<circle cx="24" cy="36" r="9" fill="#173d58" stroke="${t.rim}"/><circle cx="24" cy="36" r="5" fill="#3b6681"/><path d="M37 28H49M37 32H49M37 42H43" stroke="${white}" stroke-width="1.6"/><circle cx="47" cy="44" r="3" fill="url(#chrome)"/>`;
  const search = () => `<circle cx="27" cy="26" r="17" fill="url(#body)" stroke="${t.rim}" stroke-width="2"/><circle cx="27" cy="26" r="12" fill="#1a4864"/><path d="M37 38L54 55" stroke="#1c3e54" stroke-width="9" stroke-linecap="round"/>${line('M37 38L54 55',5)}${line('M19 24Q21 18 27 17',2)}`;
  const account = () => `${circ(32,22,11)}<path d="M11 54C11 39 20 35 32 35C44 35 53 39 53 54Z" ${a}/>${line('M22 43Q32 38 42 43',1.4)}`;
  const bluetooth = () => `${circ(32,32,23)}${line('M31 13V51L43 41L22 23M31 13L43 23L22 42',3)}`;
  const heart = () => `<path d="M32 52C17 41 8 33 8 23C8 9 25 9 32 19C39 9 56 9 56 23C56 33 47 41 32 52Z" ${a}/>${line('M14 29H23L27 21L32 39L37 27H50',2.2)}`;
  const share = () => `${circ(16,32,8)}${circ(47,17,8)}${circ(47,47,8)}${line('M23 28L40 20M23 36L40 44',3)}`;
  const remote = () => `${tv()}<path d="M32 24L43 31L32 38Z" fill="${white}"/>`;
  const badge = inner => `<g transform="translate(31,33) scale(.42)"><circle cx="32" cy="32" r="23" fill="${t.deep}" stroke="${t.rim}" stroke-width="3"/>${inner}</g>`;
  if(type==='gear') return gear();
  if(type==='music') return t.style==='retro'?cassette():music();
  if(type==='video') return t.style==='retro'?vhs():video();
  const simple={photo, tv, game, globe, gem, star, disc, update, memory, camera, save,
    usb, palette, clock, battery, speaker, shield, rss, wifi, book, radio, search,
    account, bluetooth, share, remote};
  if(simple[type]) return simple[type]();
  if(type==='browser') return globe()+`<path d="M43 29L54 50L45 47L39 54Z" fill="url(#chrome)" stroke="#33536d" stroke-width="1.4"/>`;
  if(type==='discupdate') return disc()+badge(line('M32 45V19M22 29L32 19L42 29',6));
  if(type==='videosettings') return (t.style==='retro'?vhs():video())+badge(gear());
  if(type==='photosettings') return photo()+badge(gear());
  if(type==='rsssettings') return rss()+badge(gear());
  if(type==='heartmusic') return heart();
  throw new Error('Unknown vector glyph: '+type);
}

function svgFor(type,theme) {
  const t={...theme};
  if(t.style==='candy'){
    t.accent=candyColors[type]||'#b4daf2';
    t.deep='#766495'; t.rim='#fff3ff';
  }
  const defs=`<defs>
    <linearGradient id="body" x1="0" y1="0" x2=".28" y2="1">
      <stop stop-color="${t.rim}"/><stop offset=".22" stop-color="${t.accent}"/>
      <stop offset=".55" stop-color="${t.deep}"/><stop offset="1" stop-color="${t.accent}"/>
    </linearGradient>
    <linearGradient id="chrome" x1="0" y1="0" x2=".18" y2="1">
      <stop stop-color="#ffffff"/><stop offset=".38" stop-color="#c9e0ed"/>
      <stop offset=".53" stop-color="#66829a"/><stop offset="1" stop-color="#e4f5ff"/>
    </linearGradient>
    <radialGradient id="shadow"><stop stop-color="#071627" stop-opacity=".45"/><stop offset="1" stop-color="#071627" stop-opacity="0"/></radialGradient>
  </defs>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 64 64">${defs}<ellipse cx="32" cy="55" rx="27" ry="7" fill="url(#shadow)"/>${art(type,t)}</svg>`;
}

async function icon(type,theme,size,box) {
  const svg=svgFor(type,theme);
  const image=await sharp(Buffer.from(svg)).resize(box,box,{kernel:'lanczos3'}).png().toBuffer();
  return sharp({create:{width:size[0],height:size[1],channels:4,background:{r:0,g:0,b:0,alpha:0}}})
    .composite([{input:image,left:Math.floor((size[0]-box)/2),top:Math.floor((size[1]-box)/2)}]).png().toBuffer();
}

async function halo(body,size) {
  const metadata=await sharp(body).metadata();
  const padded=await sharp({create:{width:size[0],height:size[1],channels:4,background:{r:0,g:0,b:0,alpha:0}}})
    .composite([{input:body,left:(size[0]-metadata.width)/2,top:(size[1]-metadata.height)/2}]).ensureAlpha().raw().toBuffer();
  const alpha=Buffer.alloc(size[0]*size[1]);
  for(let i=0;i<alpha.length;i++)alpha[i]=padded[i*4+3];
  const blurred=await sharp(alpha,{raw:{width:size[0],height:size[1],channels:1}}).blur(2.15).toColourspace('b-w').raw().toBuffer();
  const rgba=Buffer.alloc(alpha.length*4);
  for(let i=0;i<alpha.length;i++){
    const raw=Math.max(0,blurred[i]*.98-alpha[i]);
    const level=raw<3?0:Math.max(1,Math.round(raw/255*63));
    const a=Math.round(level*255/63);
    if(a){rgba[i*4]=rgba[i*4+1]=rgba[i*4+2]=255;rgba[i*4+3]=a;}
  }
  return sharp(rgba,{raw:{width:size[0],height:size[1],channels:4}}).png().toBuffer();
}

async function main(){
  for(const theme of themes){
    const assets=path.join(root,'themes',theme.slug,'assets');
    const vectors=path.join(root,'themes',theme.slug,'vectors');
    fs.mkdirSync(assets,{recursive:true});fs.mkdirSync(vectors,{recursive:true});
    const entries=[];
    async function put(obj,sub,label,buffer,focus=false,source='Original KP vector artwork'){
      const name=`${obj}-${String(sub).padStart(2,'0')}.png`;
      fs.writeFileSync(path.join(assets,name),buffer);
      const m=await sharp(buffer).metadata();
      entries.push({obj,sub,label,file:name,size:[m.width,m.height],focus,source});
    }
    const seen=new Set();
    async function glyph(type,size,box){
      if(!seen.has(type)){fs.writeFileSync(path.join(vectors,type+'.svg'),svgFor(type,theme));seen.add(type);}
      return icon(type,theme,size,box);
    }
    for(const [id,[label,type]] of Object.entries(categories))
      await put(2,Number(id),label,await glyph(type,[64,48],44));
    for(const [id,[label,type]] of Object.entries(first)){
      const body=await glyph(type,[48,48],42);
      await put(3,Number(id),label,body);
      await put(3,Number(id)+1,label+' focus',await halo(body,[64,64]),true,'White alpha-only halo of matching body');
    }
    for(const [id,type] of [[0,'gear'],[2,'shield']]){
      const body=await glyph(type,[32,32],28);
      await put(4,id,'Settings detail',body);
      await put(4,id+1,'Settings detail focus',await halo(body,[48,48]),true,'White alpha-only halo of matching body');
    }
    await put(0,0,'Theme preview icon',await glyph(theme.style==='retro'?'music':'gem',[16,16],15));
    const wallpaper=path.join(root,'artwork',theme.slug+'.png');
    if(!fs.existsSync(wallpaper))throw new Error('Final wallpaper absent: '+wallpaper);
    const wall=await sharp(wallpaper).resize(480,272,{fit:'cover',position:'centre',kernel:'lanczos3'}).removeAlpha().png().toBuffer();
    await put(1,0,'Wallpaper',wall,false,'Original generated background; PSP downsample');
    const preview=await sharp(wall).resize(300,170,{kernel:'lanczos3'}).png().toBuffer();
    await put(0,1,'Theme preview image',preview,false,'Wallpaper preview');
    entries.sort((a,b)=>a.obj-b.obj||a.sub-b.sub);
    fs.writeFileSync(path.join(assets,'manifest.json'),JSON.stringify(entries,null,2)+'\n');
    console.log(JSON.stringify({theme:theme.slug,assets:entries.length,originalVectorGlyphs:seen.size}));
  }
}
main().catch(e=>{console.error(e);process.exit(1)});
