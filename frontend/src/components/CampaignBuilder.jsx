import React, { useState } from 'react';
import api from '../api';
import { Send, Clock } from 'lucide-react';

export default function CampaignBuilder({ selectedGroupIds = [] }) {
    const [name, setName] = useState('');
    const [message, setMessage] = useState('');
    const [times, setTimes] = useState('09:00, 14:00');
    const [delay, setDelay] = useState(30);
    const userId = localStorage.getItem('user_id');

    const saveCampaign = async (e) => {
        e.preventDefault();
        if (!userId) return;

        // If no groups selected, warn user
        if (selectedGroupIds.length === 0) {
            if (!confirm("Hiçbir grup seçmediniz. Tüm aktif gruplara gönderilsin mi?")) {
                return;
            }
        }

        try {
            const targetIds = selectedGroupIds.length > 0 ? selectedGroupIds.join(",") : "all";

            await api.post('/manage/campaigns', {
                user_id: parseInt(userId),
                name: name,
                message_content: message,
                schedule_times: times,
                target_group_ids: targetIds,
                delay_seconds: parseInt(delay)
            });
            alert("Plan Kaydedildi! Otomasyon devreye girecek.");
            // Reset form but keeping times/delay might be useful
            setName('');
            setMessage('');
        } catch (error) {
            alert("Kaydetme hatası: " + (error.response?.data?.message || "Bilinmeyen hata"));
        }
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6 border-t-4 border-green-500">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
                <Send className="text-green-600" /> Gönderim Planı Oluştur
            </h3>

            <form onSubmit={saveCampaign} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Plan Adı</label>
                    <input
                        type="text"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        placeholder="Örn: Günaydın Mesajları"
                        className="mt-1 w-full rounded-md border-gray-300 border p-2 shadow-sm"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Mesaj İçeriği</label>
                    <textarea
                        value={message}
                        onChange={e => setMessage(e.target.value)}
                        placeholder="Gönderilecek metni buraya yazın..."
                        rows={4}
                        className="mt-1 w-full rounded-md border-gray-300 border p-2 shadow-sm"
                        required
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 flex items-center gap-1">
                            <Clock size={16} /> Gönderim Saatleri (Virgülle Ayırın)
                        </label>
                        <input
                            type="text"
                            value={times}
                            onChange={e => setTimes(e.target.value)}
                            placeholder="08:00, 12:30, 18:45"
                            className="mt-1 w-full rounded-md border-gray-300 border p-2 shadow-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Grup Arası Bekleme (Saniye)
                        </label>
                        <input
                            type="number"
                            value={delay}
                            onChange={e => setDelay(e.target.value)}
                            className="mt-1 w-full rounded-md border-gray-300 border p-2 shadow-sm"
                        />
                    </div>
                </div>

                <button type="submit" className="w-full bg-green-600 text-white font-bold py-3 px-4 rounded hover:bg-green-700 transition duration-200">
                    TASLAĞI KAYDET VE BAŞLAT
                </button>
            </form>
        </div>
    );
}
