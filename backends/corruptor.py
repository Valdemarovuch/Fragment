import webview
import random
import os
import shutil

# --- HTML/JS (Інтерфейс) ---
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fragment</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        body { -webkit-user-select: none; user-select: none; cursor: default; }
        .terminal-scroll::-webkit-scrollbar { width: 4px; }
        .terminal-scroll::-webkit-scrollbar-track { background: transparent; }
        .terminal-scroll::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
        .scanlines {
            background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.1));
            background-size: 100% 4px; pointer-events: none;
        }
    </style>
</head>
<body class="bg-[#050505] text-neutral-300 font-sans antialiased h-screen flex items-center justify-center overflow-hidden">
    
    <div class="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-orange-900/10 blur-[120px] rounded-full pointer-events-none"></div>

    <main class="w-full h-full flex flex-col bg-[#0A0A0A] relative z-10 overflow-hidden">
        <div class="absolute inset-0 scanlines opacity-20 pointer-events-none z-50"></div>

        <header class="flex items-center justify-between px-6 py-5 border-b border-neutral-800/60 bg-[#0A0A0A]/80 backdrop-blur-md draggable-region" style="-webkit-app-region: drag;">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-orange-500">
                    <iconify-icon icon="lucide:zap" width="18" height="18"></iconify-icon>
                </div>
                <div>
                    <h1 class="text-white text-lg font-medium tracking-tight leading-none">Fragment</h1>
                    <p class="text-neutral-500 text-xs font-medium tracking-wide mt-1">DIRECT DISK ACCESS</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <span id="status-light" class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
                <span id="status-text" class="text-[10px] font-mono text-neutral-500 uppercase tracking-widest">System Ready</span>
            </div>
        </header>

        <div class="p-6 space-y-6 flex-1 flex flex-col justify-center">
            
            <div id="uploadZone" class="group relative w-full cursor-pointer">
                <div class="border border-dashed border-neutral-800 bg-neutral-900/30 rounded-xl p-8 transition-all duration-300 group-hover:border-neutral-600 group-hover:bg-neutral-900/50 flex flex-col items-center justify-center text-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center text-neutral-400 group-hover:text-white group-hover:scale-110 transition-all duration-300">
                        <iconify-icon icon="lucide:folder-open" width="20" height="20"></iconify-icon>
                    </div>
                    <div>
                        <p id="fileNameDisplay" class="text-sm font-medium text-neutral-300 group-hover:text-white transition-colors">Click to select file</p>
                        <p class="text-xs text-neutral-500 mt-1" id="filePathDisplay">Waiting for selection...</p>
                    </div>
                </div>
            </div>

            <div class="flex items-center justify-between pb-4 border-b border-neutral-800/60">
                <div class="flex flex-col">
                    <span class="text-sm font-medium text-neutral-200">Safety Tagging</span>
                    <span class="text-xs text-neutral-500">Append "_corrupted" to filename</span>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" id="safetyToggle" class="sr-only peer" checked>
                    <div class="w-11 h-6 bg-neutral-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-neutral-400 after:border-neutral-300 after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-neutral-800 peer-checked:after:bg-orange-500 peer-checked:after:shadow-[0_0_10px_rgba(249,115,22,0.4)]"></div>
                </label>
            </div>

            <div class="bg-[#050505] rounded-lg border border-neutral-800 overflow-hidden flex-1 min-h-[100px]">
                <div class="flex items-center justify-between px-3 py-2 bg-neutral-900/50 border-b border-neutral-800">
                    <span class="text-[10px] font-mono text-neutral-500 uppercase tracking-wider">Process Log</span>
                </div>
                <div id="terminal" class="h-28 p-3 font-mono text-[11px] leading-relaxed text-neutral-400 terminal-scroll overflow-y-auto">
                    <div class="flex gap-2"><span class="text-neutral-600">SYS</span><span>Fragment Engine v2.0 initialized...</span></div>
                </div>
            </div>

            <button id="generateBtn" class="w-full h-11 relative group overflow-hidden rounded-lg bg-neutral-100 hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                <div class="absolute inset-0 flex items-center justify-center gap-2">
                    <span id="btnText" class="text-neutral-950 text-sm font-semibold tracking-tight">Generate Fragment</span>
                </div>
                <div class="absolute inset-0 bg-orange-500 mix-blend-overlay opacity-0 group-hover:opacity-20 transition-opacity"></div>
            </button>
        </div>
    </main>

    <script>
        const terminal = document.getElementById('terminal');
        const uploadZone = document.getElementById('uploadZone');
        const generateBtn = document.getElementById('generateBtn');
        let currentFilePath = null;

        function log(msg, type='normal') {
            const div = document.createElement('div');
            div.className = "flex gap-2";
            let color = type === 'err' ? 'text-red-500' : (type === 'proc' ? 'text-orange-500' : (type === 'succ' ? 'text-emerald-500' : 'text-neutral-400'));
            div.innerHTML = `<span class="text-neutral-600">${new Date().toLocaleTimeString('en-GB', {hour12:false})}</span><span class="${color}">${msg}</span>`;
            terminal.appendChild(div);
            terminal.scrollTop = terminal.scrollHeight;
        }

        uploadZone.addEventListener('click', async () => {
            log('Opening system dialog...', 'proc');
            const path = await window.pywebview.api.pick_file();
            
            if (path) {
                currentFilePath = path;
                const filename = path.split(/[\\\\/]/).pop(); // Get filename from path
                document.getElementById('fileNameDisplay').innerText = filename;
                document.getElementById('fileNameDisplay').classList.add('text-white');
                document.getElementById('filePathDisplay').innerText = path;
                
                log(`Target locked: ${filename}`, 'succ');
                document.getElementById('status-light').className = "w-2 h-2 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.4)]";
            } else {
                log('Selection cancelled.', 'normal');
            }
        });

        generateBtn.addEventListener('click', async () => {
            if (!currentFilePath) return log('Error: No target selected.', 'err');

            generateBtn.disabled = true;
            document.getElementById('btnText').innerText = "Corrupting...";
            log('Initializing corruption sequence...', 'proc');

            const safety = document.getElementById('safetyToggle').checked;

            try {
                const result = await window.pywebview.api.corrupt_file(currentFilePath, safety);
                
                if (result.success) {
                    log(`Success! Saved to:`, 'succ');
                    log(result.new_path, 'succ');
                } else {
                    log(`Error: ${result.error}`, 'err');
                }
            } catch (e) {
                log(`Critical Failure: ${e}`, 'err');
            } finally {
                generateBtn.disabled = false;
                document.getElementById('btnText').innerText = "Generate Fragment";
                document.getElementById('status-light').className = "w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]";
            }
        });
    </script>
</body>
</html>
"""

# --- PYTHON ЛОГІКА ---

class Api:
    def pick_file(self):
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False)
        return result[0] if result else None

    def corrupt_file(self, file_path, safety_mode):
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'Target missing'}

            # --- SETUP PATHS ---
            dirname = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # Якщо safety_mode вимкнено - ім'я ідентичне (для заміни), 
            # але ми додаємо префікс для безпеки демо-версії.
            suffix = "_decoy" if safety_mode else "_corrupted"
            new_filename = f"{name}{suffix}{ext}"
            new_path = os.path.join(dirname, new_filename)

            # Отримуємо статистику оригіналу (розмір + дати)
            stats = os.stat(file_path)
            file_size = stats.st_size

            # --- PHASE 1: SMART CORRUPTION ---
            chunk_size = 64 * 1024 # 64KB blocks (Optimal for disk I/O)
            written = 0

            with open(new_path, 'wb') as f_dst:
                # [PRO TRICK] Smart Header Retention
                # Ми копіюємо перші 128 байт оригіналу, щоб зберегти сигнатуру файлу.
                # Це змусить ОС і програми вірити, що файл валідний.
                header_len = min(128, file_size)
                
                with open(file_path, 'rb') as f_src:
                    header_data = f_src.read(header_len)
                    f_dst.write(header_data)
                    written += header_len

                # Решту забиваємо криптографічним шумом
                while written < file_size:
                    remaining = file_size - written
                    current_chunk = min(chunk_size, remaining)
                    
                    # os.urandom - це повільно для гігабайтів. 
                    # Для "HoneyPot" можна використати швидшу генерацію, 
                    # але для "знищення" краще urandom. 
                    # Тут беремо urandom для якості.
                    f_dst.write(os.urandom(current_chunk))
                    written += current_chunk

            # --- PHASE 2: TIMESTOMPING (FORENSIC CLEANING) ---
            # Переносимо дати створення (atime, mtime) з оригіналу на копію
            os.utime(new_path, (stats.st_atime, stats.st_mtime))
            
            # На Windows дата створення (creation time) вимагає окремого підходу,
            # але os.utime покриває основні атрибути для Explorer.
            # (Для повного клонування ctime потрібні WinAPI виклики, 
            # але для Python-рівня цього достатньо).

            return {'success': True, 'new_path': new_filename}

        except Exception as e:
            return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'Fragment // Data Corruptor', 
        html=html_content, 
        js_api=api,
        width=500, 
        height=700,
        resizable=False,
        background_color='#050505'
    )
    webview.start()