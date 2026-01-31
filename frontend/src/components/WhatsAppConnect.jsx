import React, { useState, useEffect } from 'react';
import api from '../api';

export default function WhatsAppConnect({ onConnectionChange }) {
    const [qrCode, setQrCode] = useState(null);
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(false);
    const [phoneNumber, setPhoneNumber] = useState('');
    const [pairingCode, setPairingCode] = useState('');
    const [pairingLoading, setPairingLoading] = useState(false);

    useEffect(() => {
        checkStatus();
        const interval = setInterval(checkStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    const checkStatus = async () => {
        try {
            const response = await api.get('/user/whatsapp/status');
            const isConnected = response.data.connected;

            if (isConnected !== connected) {
                setConnected(isConnected);
                if (onConnectionChange) onConnectionChange(isConnected);
            }

            if (!isConnected) {
                fetchQR();
            } else {
                setQrCode(null);
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    };

    const fetchQR = async () => {
        try {
            const response = await api.get('/user/whatsapp/qr');
            if (response.data.qr) {
                setQrCode(response.data.qr);
            }
        } catch (error) {
            console.error('QR fetch failed:', error);
        }
    };

    const handleSync = async () => {
        if (!connected) return alert("Önce WhatsApp'a bağlanın!");
        setLoading(true);
        try {
            const res = await api.post('/user/groups/sync');
            alert(res.data.message);
            if (onConnectionChange) onConnectionChange(true); // Trigger parent refresh
        } catch (error) {
            alert("Grup senkronizasyonu başarısız: " + (error.response?.data?.message || error.message));
        } finally {
            setLoading(false);
        }
    };

    const handleConnect = async () => {
        setLoading(true);
        try {
            await api.post('/user/whatsapp/connect');
            // The loop will pick up the QR
        } catch (error) {
            alert("Browser başlatılamadı");
        } finally {
            setLoading(false);
        }
    };

    const handleDisconnect = async () => {
        if (!confirm("Bağlantıyı kesmek istediğinize emin misiniz?")) return;
        try {
            await api.post('/user/whatsapp/logout');
            setConnected(false);
            setQrCode(null);
        } catch (error) {
            alert("Çıkış yapılamadı");
        }
    };

    const handlePairing = async (e) => {
        e.preventDefault();
        setPairingLoading(true);
        try {
            const res = await api.post('/user/whatsapp/pair', { phone: phoneNumber });
            if (res.data.code) {
                setPairingCode(res.data.code);
            }
        } catch (error) {
            alert("Kod alınamadı. Numaranızı kontrol edin (örn: 905551234567)");
        } finally {
            setPairingLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                        WhatsApp Bağlantısı
                        <span className={`text-xs px-2 py-1 rounded-full ${connected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                            {connected ? 'Bağlı' : 'Bağlı Değil'}
                        </span>
                    </h2>
                    <p className="text-gray-500 text-sm mt-1">Mesaj göndermek için hesabınızı bağlayın.</p>
                </div>
                {connected && (
                    <button
                        onClick={handleDisconnect}
                        className="bg-red-50 text-red-600 px-4 py-2 rounded-lg text-sm hover:bg-red-100 transition"
                    >
                        Bağlantıyı Kes
                    </button>
                )}
            </div>

            {!connected ? (
                <div className="grid md:grid-cols-2 gap-8">
                    {/* QR Code Section */}
                    <div className="flex flex-col items-center justify-center border-r border-gray-100 pr-8">
                        <h3 className="font-semibold text-gray-700 mb-4">QR Kod ile Tara</h3>
                        {qrCode ? (
                            <div className="p-2 border rounded-lg shadow-sm">
                                <img src={qrCode} alt="WhatsApp QR" className="w-48 h-48 object-contain" />
                            </div>
                        ) : (
                            <div className="w-48 h-48 bg-gray-100 rounded-lg flex items-center justify-center flex-col gap-2">
                                <span className="text-gray-400 text-sm">{loading ? 'Hazırlanıyor...' : 'QR Bekleniyor'}</span>
                                {!loading && (
                                    <button
                                        onClick={handleConnect}
                                        className="text-green-600 text-sm hover:underline"
                                    >
                                        QR Oluştur
                                    </button>
                                )}
                            </div>
                        )}
                        <p className="text-xs text-gray-400 mt-4 text-center">
                            WhatsApp &gt; Ayarlar &gt; Bağlı Cihazlar &gt; Cihaz Bağla
                        </p>
                    </div>

                    {/* Phone Pairing Section */}
                    <div className="pl-4">
                        <h3 className="font-semibold text-gray-700 mb-4">Telefon No ile Bağla (Beta)</h3>
                        {!pairingCode ? (
                            <form onSubmit={handlePairing} className="space-y-4">
                                <div>
                                    <label className="text-xs text-gray-500 block mb-1">Telefon Numarası</label>
                                    <input
                                        type="text"
                                        placeholder="905551234567"
                                        className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 outline-none"
                                        value={phoneNumber}
                                        onChange={e => setPhoneNumber(e.target.value)}
                                        required
                                    />
                                </div>
                                <button
                                    type="submit"
                                    disabled={pairingLoading}
                                    className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-500 transition disabled:opacity-50"
                                >
                                    {pairingLoading ? 'Kod Alınıyor...' : 'Eşleşme Kodu Al'}
                                </button>
                            </form>
                        ) : (
                            <div className="text-center space-y-4">
                                <div className="bg-gray-100 p-4 rounded-lg">
                                    <p className="text-sm text-gray-500 mb-1">Eşleşme Kodunuz:</p>
                                    <p className="text-2xl font-mono font-bold tracking-widest text-gray-800">{pairingCode}</p>
                                </div>
                                <p className="text-xs text-yellow-600">Bu kodu telefonunuzdaki WhatsApp bildirimine girin.</p>
                                <button
                                    onClick={() => setPairingCode('')}
                                    className="text-gray-500 text-sm underline"
                                >
                                    Geri Dön
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <div className="bg-green-50 rounded-lg p-6 flex flex-col items-center justify-center text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                    </div>
                    <h3 className="text-lg font-bold text-green-800">WhatsApp Bağlandı!</h3>
                    <p className="text-green-600 mt-2 mb-4">Artık gruplarınızı çekebilir ve mesaj gönderebilirsiniz.</p>

                    <button
                        onClick={handleSync}
                        disabled={loading}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition shadow-lg flex items-center gap-2"
                    >
                        {loading ? (
                            <>
                                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                İşleniyor...
                            </>
                        ) : (
                            <>
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                                Grupları ve Kişileri Çek / Güncelle
                            </>
                        )}
                    </button>
                    <p className="text-xs text-gray-400 mt-2">Bu işlem birkaç saniye sürebilir.</p>
                </div>
            )}
        </div>
    );
}
