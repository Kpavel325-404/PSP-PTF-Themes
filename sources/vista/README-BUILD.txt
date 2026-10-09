СБОРКА ИЗ ПОДГОТОВЛЕННЫХ РЕСУРСОВ
Для установки на PSP исходники не нужны.

Нужны Python 3.9+ и Pillow. Выполни из Source:
  python -m pip install Pillow
  python build_theme.py

Результат: dist/Aero-Vista-Aurora.ptf.
Включённые assets/indexed уже квантованы: сборка не требует PSP SDK,
Node.js, доступа к Интернету или программ Sony. При тех же ресурсах
повторная сборка даёт тот же файл; SHA-256 смотри в общей инструкции.

Дополнительная независимая проверка:
Нужен современный Node.js с DecompressionStream (рекомендуется 22+).
  npm install @napi-rs/canvas
  node verify_theme.js
  python validate_theme.py
  node render_theme.js

Для подготовки изменённых изображений нужны также numpy и sharp:
  python -m pip install numpy
  npm install sharp
  python prepare_assets.py
  node quantize_assets.js
  python build_theme.py
  node verify_theme.js
  python validate_theme.py

prepare_assets.py использует включённые оригиналы значков и Aurora.
Схема ресурсов и ссылки указаны в assets/manifest.json.
package_theme.py — сборщик комплекта; для него нужен путь к DejaVu Sans
и его лицензии, как в Debian/Linux. Основная сборка PTF от него не зависит.

verify_theme.js вызывает неизменённый читатель из sources/ptf-app.js.
render_theme.js — отдельный адаптер расположения XMB для Skia, с русскими
подписями, подменой шрифта и условными данными даты/батареи предпросмотра.
Исходный PTF Studio и адаптеры читателя/предпросмотра доступны на условиях
GPL-3.0; лицензия в sources/ptf-studio/LICENSE.
DejaVu Sans используется только для компьютерного предпросмотра.
Графика Vista — Microsoft, для личного оформления. Источники и авторы
перечислены в основной инструкции и sources/windows/README.md.
