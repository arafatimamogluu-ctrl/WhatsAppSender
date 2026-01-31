import React, { useEffect, useState } from 'react';
import api from '../api';
import { FileText, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

export default function LogViewer() {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const res = await api.get('/user/logs');
            setLogs(res.data.logs);
        } catch (error) {
            console.error("Log hatası", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000); // Auto refresh every 5s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-white p-6 rounded-lg shadow-md h-96 flex flex-col">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold flex items-center gap-2 text-gray-800">
                    <FileText className="text-purple-600" /> Gönderim Raporu
                </h3>
                <button
                    onClick={fetchLogs}
                    className="p-2 hover:bg-gray-100 rounded-full transition"
                    title="Yenile"
                >
                    <RefreshCw size={18} className={loading ? "animate-spin text-gray-400" : "text-gray-600"} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto border rounded-lg bg-gray-50 p-2 space-y-2 font-mono text-sm">
                {logs.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-400">
                        <FileText size={48} className="mb-2 opacity-20" />
                        <p>Henüz işlem kaydı yok.</p>
                    </div>
                ) : (
                    logs.map((log, index) => (
                        <div key={index} className="bg-white p-3 rounded border shadow-sm flex items-start justify-between">
                            <div>
                                <div className="flex items-center gap-2">
                                    <span className="font-bold text-gray-700">{log.group_name}</span>
                                    <span className="text-xs text-gray-400">({log.scheduled_time})</span>
                                </div>
                                <p className="text-gray-500 text-xs mt-1 truncate max-w-xs">{log.message_type}</p>
                            </div>
                            <div className="flex flex-col items-end">
                                {log.status === 'completed' ? (
                                    <span className="flex items-center gap-1 text-green-600 text-xs font-bold bg-green-50 px-2 py-1 rounded">
                                        <CheckCircle size={14} /> Başarılı
                                    </span>
                                ) : log.status === 'failed' || log.status === 'hatali' ? (
                                    <span className="flex items-center gap-1 text-red-600 text-xs font-bold bg-red-50 px-2 py-1 rounded">
                                        <XCircle size={14} /> Hata
                                    </span>
                                ) : (
                                    <span className="flex items-center gap-1 text-yellow-600 text-xs font-bold bg-yellow-50 px-2 py-1 rounded">
                                        <Clock size={14} /> Bekliyor
                                    </span>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
