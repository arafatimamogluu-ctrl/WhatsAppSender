const localtunnel = require('localtunnel');
const { spawn } = require('child_process');
const path = require('path');

// Configuration
const BACKEND_PORT = 8000;
const FRONTEND_PORT = 5173;

console.log("\x1b[36m%s\x1b[0m", "=== Otonom WhatsApp Sistemi Başlatılıyor ===");

async function startSystem() {
    try {
        // 1. Start Backend with Python
        console.log("1. Backend sunucusu başlatılıyor...");
        const backendProcess = spawn('python', ['main.py'], {
            cwd: path.resolve(__dirname, 'backend'),
            shell: true,
            stdio: 'ignore'
        });

        // 2. Open Backend Tunnel
        console.log("2. Backend tüneli açılıyor...");
        const backendTunnel = await localtunnel({ port: BACKEND_PORT });
        const backendUrl = backendTunnel.url;
        console.log("\x1b[32m%s\x1b[0m", `   Backend URL: ${backendUrl}`);

        if (!backendUrl) {
            throw new Error("Backend tüneli açılamadı.");
        }

        // 3. Start Frontend with Backend URL in Env
        console.log("3. Frontend sunucusu başlatılıyor...");
        const frontendProcess = spawn('npm', ['run', 'dev'], {
            cwd: path.resolve(__dirname, 'frontend'),
            shell: true,
            env: { ...process.env, VITE_API_URL: backendUrl + '/api' },
            stdio: 'ignore'
        });

        // Wait a bit for frontend to possibly start
        await new Promise(r => setTimeout(r, 5000));

        // 4. Open Frontend Tunnel
        console.log("4. Frontend tüneli açılıyor...");
        const frontendTunnel = await localtunnel({ port: FRONTEND_PORT });
        const frontendUrl = frontendTunnel.url;

        // Fetch Public IP for Localtunnel Password
        console.log("   Tunnel şifresi (IP) alınıyor...");
        let publicIp = "Bulunamadı";
        try {
            const ipRes = await fetch('https://loca.lt/mytunnelpassword');
            publicIp = await ipRes.text();
            publicIp = publicIp.trim();
        } catch (e) {
            console.log("   IP alınamadı, manuel bakmanız gerekebilir.");
        }

        console.log("\n========================================================");
        console.log("\x1b[32m%s\x1b[0m", "SİSTEM HAZIR! 🚀");
        console.log("Aşağıdaki linki tarayıcıda açın:");
        console.log("\x1b[33m%s\x1b[0m", `\n👉 ${frontendUrl} 👈\n`);
        console.log("\x1b[31m%s\x1b[0m", "!!! ŞİFRE İSTERSE AŞAĞIDAKİ IP'Yİ GİRİN !!!");
        console.log("\x1b[47m\x1b[30m%s\x1b[0m", ` ${publicIp} `); // White bg, black text
        console.log("========================================================");
        console.log("(Çıkmak için bu pencereyi kapatın veya Ctrl+C yapın)");

        // Keep processes alive
        backendTunnel.on('close', () => {
            console.log("Backend tüneli kapandı.");
        });
        frontendTunnel.on('close', () => {
            console.log("Frontend tüneli kapandı.");
        });

    } catch (error) {
        console.error("Hata oluştu:", error);
    }
}

startSystem();
