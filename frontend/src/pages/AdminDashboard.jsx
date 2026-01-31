import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Users, BarChart, Settings, LogOut, Package } from 'lucide-react';

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState({ total_users: 0, active_users: 0 });
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchStats();
        fetchUsers();
    }, []);

    const fetchStats = async () => {
        try {
            const res = await api.get('/admin/stats');
            setStats(res.data);
        } catch (error) {
            console.error("Stats error", error);
        }
    };

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const res = await api.get('/admin/users');
            setUsers(res.data.users);
        } catch (error) {
            console.error("Users error", error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdatePlan = async (email, newPlan) => {
        if (!confirm(`Kullanıcının planını ${newPlan} olarak güncellemek istiyor musunuz?`)) return;
        try {
            await api.put(`/admin/users/${email}/plan`, null, { params: { plan: newPlan } });
            alert("Plan güncellendi");
            fetchUsers();
        } catch (error) {
            alert("Güncelleme hatası");
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 font-sans">
            {/* Admin Navbar */}
            <div className="bg-gray-900 text-white shadow-md">
                <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
                    <h1 className="text-xl font-bold flex items-center gap-2">
                        <Settings className="text-blue-400" /> Admin Paneli
                    </h1>
                    <div className="flex gap-4">
                        <button onClick={() => navigate('/dashboard')} className="text-gray-300 hover:text-white">User Dashboard</button>
                        <button onClick={() => { localStorage.clear(); navigate('/login'); }} className="text-red-400 hover:text-red-300">
                            <LogOut size={18} />
                        </button>
                    </div>
                </div>
            </div>

            <main className="max-w-7xl mx-auto py-8 px-4">
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-blue-500">
                        <div className="text-gray-500 text-sm">Toplam Kullanıcı</div>
                        <div className="text-2xl font-bold">{stats.total_users}</div>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500">
                        <div className="text-gray-500 text-sm">Aktif Paketli</div>
                        <div className="text-2xl font-bold">{stats.active_users}</div>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-purple-500">
                        <div className="text-gray-500 text-sm">Bugünkü Mesajlar</div>
                        <div className="text-2xl font-bold">-</div>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-yellow-500">
                        <div className="text-gray-500 text-sm">Sistem Durumu</div>
                        <div className="text-sm font-bold text-green-600">Aktif</div>
                    </div>
                </div>

                {/* Users Table */}
                <div className="bg-white rounded-lg shadow-md overflow-hidden">
                    <div className="px-6 py-4 border-b flex justify-between items-center bg-gray-50">
                        <h3 className="font-bold text-gray-700 flex items-center gap-2">
                            <Users size={18} /> Kullanıcı Yönetimi
                        </h3>
                        <button onClick={fetchUsers} className="text-blue-600 text-sm hover:underline">Yenile</button>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-gray-100 text-gray-600 uppercase text-xs">
                                <tr>
                                    <th className="px-6 py-3">Kullanıcı</th>
                                    <th className="px-6 py-3">Email</th>
                                    <th className="px-6 py-3">Mevcut Plan</th>
                                    <th className="px-6 py-3">İşlemler</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((u, i) => (
                                    <tr key={i} className="border-b hover:bg-gray-50">
                                        <td className="px-6 py-4 font-medium">{u.full_name || '-'}</td>
                                        <td className="px-6 py-4">{u.email}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${u.subscription_plan === 'pro' ? 'bg-purple-100 text-purple-700' :
                                                    u.subscription_plan === 'basic' ? 'bg-blue-100 text-blue-700' :
                                                        'bg-gray-100 text-gray-600'
                                                }`}>
                                                {u.subscription_plan.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 flex gap-2">
                                            <button
                                                onClick={() => handleUpdatePlan(u.email, 'free')}
                                                className="text-gray-500 hover:text-black text-xs border px-2 py-1 rounded"
                                            >Free</button>
                                            <button
                                                onClick={() => handleUpdatePlan(u.email, 'basic')}
                                                className="text-blue-500 hover:text-blue-700 text-xs border px-2 py-1 rounded"
                                            >Basic</button>
                                            <button
                                                onClick={() => handleUpdatePlan(u.email, 'pro')}
                                                className="text-purple-500 hover:text-purple-700 text-xs border px-2 py-1 rounded"
                                            >Pro</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    );
}
