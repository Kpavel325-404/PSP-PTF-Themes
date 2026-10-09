'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { context, declaration, source } = require('./verify_theme.js');
const modules = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const canvas = require(modules ? require.resolve('@napi-rs/canvas', { paths: [modules] }) : '@napi-rs/canvas');
const root = __dirname;
const first = {
  2:'Memory Stick™', 4:'UMD™', 6:'Камера', 8:'Обмен играми', 10:'Управление сохранениями',
  12:'Обновление UMD™', 14:'Обновление системы', 16:'Соединение USB', 18:'Настройки видео',
  20:'Настройки фото', 22:'Настройки системы', 24:'Настройки темы', 26:'Дата и время',
  28:'Энергосбережение', 30:'Внешний дисплей', 32:'Настройки звука', 34:'Безопасность',
  36:'Настройки RSS', 38:'Настройки сети', 40:'Руководство пользователя', 42:'Дистанционное воспроизведение',
  44:'Интернет-радио', 46:'Канал RSS', 48:'Интернет-браузер', 50:'Поиск в Интернете',
  52:'Управление учетной записью', 54:'Дополнительно', 56:'Настройки Bluetooth', 58:'SensMe™'
};
const category = {0:'Дополнительно',1:'Настройки',2:'Фото',3:'Музыка',4:'Видео',5:'ТВ',6:'Игра',7:'Сеть',8:'Дополнительно'};
const functions = [
  'currentProfile','visibleCategoryAssets','visibleItemsForCategory','firstLevelDisplayLabel',
  'imageDataToCanvas','drawImageDataFit','getAsset','categoryAssets','bodyAsset','focusAsset',
  'isPspGoVirtualFirstLevel','resolvedBodyAsset','resolvedFocusAsset','clamp01','easeOutCubic',
  'setPspFont','drawPspText','registerPreviewHit','drawXmb','drawStatusBar','focusPulse',
  'firstLevelDimAlpha','drawVerticalItems','secondLevelAssetPair','drawSecondLevelMenu'
];

async function main() {
  const bytes = new Uint8Array(fs.readFileSync(path.join(root,'dist/Aero-Vista-Aurora.ptf')));
  const parsed = await context.parsePtf(bytes.buffer);
  context.state = { theme: parsed.theme, assets: parsed.assets, previewHitRegions: [],
    modelProfile:'3000', nav:{categoryPos:0,itemPos:0,secondPos:0,level:1}, animationStart:0, viewMode:'xmb', showGuides:false };
  context.FIRST_LABELS = first;
  context.CATEGORY_LABELS = category;
  for (const asset of parsed.assets) if (asset.objIdx === 2) asset.role.label = category[asset.subIdx];
  context.MODEL_PROFILES = {'3000':{categories:[1,2,3,4,5,6,7,8],excludedItems:[56]}};
  context.PROFILE_CATEGORY_ITEMS = {};
  context.PSP_GO_VIRTUAL_FIRST_LEVEL_IDS = new Set([60,62,64]);
  context.PSP_SCALE = 2;
  context.PSP_FONT_STACK = 'PSP Preview';
  context.els = { pulseToggle:{checked:false} };
  context.requestAnimationFrame = () => {};
  context.document = { createElement: tag => {
    if (tag !== 'canvas') throw new Error('Unexpected element: ' + tag);
    return canvas.createCanvas(1,1);
  }};
  context.assetVisibleForProfile = () => true;
  context.formatPspDateTime = () => '5/10 21:04';
  context.drawStorageItemLabel = () => false;
  const previewFont = path.join(root, 'sources/preview-font.ttf');
  canvas.GlobalFonts.registerFromPath(fs.existsSync(previewFont) ? previewFont : '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','PSP Preview');
  context.PSP_BATTERY_IMAGE = await canvas.loadImage(path.join(root,'sources/ptf-studio/assets/psp_battery.png'));
  const start = source.indexOf('const XMB_LAYOUT =');
  const end = source.indexOf('\n});',start) + 4;
  vm.runInContext(source.slice(start,end).replace('const XMB_LAYOUT =','globalThis.XMB_LAYOUT ='),context);
  const catStart = source.indexOf('const CATEGORY_ITEMS =');
  const catEnd = source.indexOf('\n};',catStart) + 3;
  vm.runInContext(source.slice(catStart,catEnd).replace('const CATEGORY_ITEMS =','globalThis.CATEGORY_ITEMS ='),context);
  vm.runInContext(functions.map(declaration).join('\n'), context);
  const target = canvas.createCanvas(960,544);
  context.ctx = target.getContext('2d');
  const screens = [
    {name:'settings',category:1,selected:24},
    {name:'music',category:3,selected:2},
    {name:'games',category:6,selected:10},
    {name:'network',category:7,selected:48},
    {name:'photo',category:2,selected:6},
    {name:'video',category:4,selected:2}
  ];
  for (const screen of screens) {
    const categories = context.visibleCategoryAssets();
    context.state.nav = { categoryPos:categories.findIndex(a=>a.subIdx===screen.category), itemPos:0, secondPos:0, level:1 };
    const ids = context.visibleItemsForCategory(screen.category);
    context.state.nav.itemPos = ids.indexOf(screen.selected);
    if (context.state.nav.itemPos < 0) throw new Error('Selected menu item missing');
    context.drawXmb(2000);
    fs.writeFileSync(path.join(root,'build',`xmb-${screen.name}.png`),target.toBuffer('image/png'));
  }
  console.log(JSON.stringify({ renderedScreens:screens.length, artworkSource:'Compiled PTF', renderer:'PTF Studio layout adapted to Skia; desktop preview, not a PSP screenshot' }));
}
main().catch(e => { console.error(e); process.exit(1); });
