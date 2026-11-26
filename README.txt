SCICALC - scientific calculator that runs on any device, fully offline
=======================================================================

What this is
  A web app (PWA) with the whole Python calculator engine inside it (Python runs in the browser through
  Pyodide / WebAssembly). Nothing is sent anywhere and nothing needs the internet after the first load.
  It works in current Chrome, Edge, Firefox, Safari (Windows, macOS, Linux, Android, iOS/iPadOS, Chromebook).

Try it on your computer (needs only Python 3)
  1. Unzip this folder.
  2. python serve.py
  3. Open http://localhost:8000
  The first start downloads nothing from the internet; it takes about 3 seconds to load the engine.
  In Chrome/Edge an "Install app" button appears: it installs SciCalc like a normal program (own window,
  desktop/start-menu icon) and it keeps working with Wi-Fi switched off.

Put it on phones, tablets and other computers
  A browser only allows "install" and "offline" for pages served from a secure address (https://, or localhost).
  So copy the folder webapp/ to any free static web host once, e.g.
    - GitHub Pages, Netlify (drag and drop the webapp folder), Cloudflare Pages, or your own server.
  Then on each device, open the address ONCE while online (about 14 MB are saved on the device):
    Android (Chrome)   menu (three dots) > Install app / Add to Home screen
    iPhone / iPad      Safari > Share > Add to Home Screen
    Windows/Mac/Linux  Chrome or Edge > the install icon in the address bar
  After that the app opens from its icon with no internet at all. Updates arrive by themselves the next time the
  device is online.
  (Opening index.html by double-click does not work: browsers block WebAssembly and workers for files on disk.)

Credit, copyright and patents
  Your name in the footer: open webapp/credits.js, change owner (and year / extra / rights), run  python build_app.py.
  Put your name in LICENSE (search for BIMAN SHIL, biman.shil.techbuddy@gmail.com, West Bengal, India),
  and in COPYRIGHT.txt. A footer or copyright line states authorship; it is not a patent.
  Do not write "Patented" or "Patent pending" unless a patent application has really been filed.

Files
  calculator.py        the command-line calculator (python calculator.py), same engine
  scicalc/             the engine, 47 modules (see scicalc/MODULES.md); scicalc/api.py is the app interface
  pyrightconfig.json   settings for VS Code Pylance (Python 3.12); the project is clean under it
  webapp/              the app: index.html, style.css, app.js, engine.js, py-worker.js, sw.js (offline),
                       manifest.webmanifest, icons/, pyodide/ (Python for the browser), scicalc.zip (engine copy)
  build_app.py         rebuilds webapp/scicalc.zip and the offline file list - run it after changing scicalc/ or webapp/
  serve.py             tiny local web server (python serve.py [port]; --test adds the /api test door)
  get_pyodide.py       re-downloads Pyodide if you ever need to (needs internet)
  run_tests.py         test one module at a time:  python run_tests.py lib_trig   (python run_tests.py --all)
                       (or just run the module file itself: python scicalc/lib_trig.py does the same)

Changing the calculator
  Edit a file in scicalc/, run  python run_tests.py <module>  and  python calculator.py --selftest --quiet,
  then  python build_app.py  to put the new engine into the app. Installed copies update on the next online visit.

What the app has
  Keypad (scientific + numeric), keyboard input on computers (Enter, Esc, arrow-up recall), history, a browser for
  all 1203 functions and 266 constants with search and examples, variables A-F/X/Y/M, your own functions (f(x)=...),
  angle modes, Norm/Fix/Sci/Eng, fractions, exact forms (2√3, π/6), complex numbers, base and DMS display,
  dark/light theme, saving/opening a session file. Your history and settings are kept on the device.

Known limits
  - First visit needs internet once (to save the app). Private/incognito windows may not keep offline copies.
  - Calculations running longer than 20 seconds are stopped (the engine restarts and your session is restored).
  - No graph plot yet (the engine has table and solve functions; plotting is the next feature).
  - Numbers are normal 64-bit floats (about 15 digits); exact fractions are used where possible.
