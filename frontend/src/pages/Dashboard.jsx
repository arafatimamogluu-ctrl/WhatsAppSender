import React from 'react';
import { useNavigate } from 'react-router-dom';
import WhatsAppConnect from '../components/WhatsAppConnect';
import GroupManager from '../components/GroupManager';
import CampaignBuilder from '../components/CampaignBuilder';
import LogViewer from '../components/LogViewer';

export default function Dashboard() {
    const navigate = useNavigate();
    const userEmail = localStorage.getItem('email');
    // Parse user object if available for name
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : {};

    // State for selected groups to share between GroupManager and CampaignBuilder
    const [selectedGroupIds, setSelectedGroupIds] = React.useState([]);

    const handleLogout = () => {
        localStorage.clear();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Üst Bar */}
            <nav className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center gap-2">
                            {/* Simple Logo Placeholder */}
                            <div className="bg-green-600 text-white p-2 rounded-lg font-bold">W</div>
                            <h1 className="text-xl font-bold text-gray-900">Otonom WhatsApp</h1>
                        </div>
                        <div className="flex items-center gap-4">
                            {user.role === 'admin' && (
                                <button
                                    onClick={() => navigate('/admin')}
                                    className="text-sm font-bold text-blue-600 border border-blue-600 px-3 py-1 rounded hover:bg-blue-50 transition"
                                >
                                    Admin Paneli
                                </button>
                            )}
                            <span className="text-sm text-gray-500 hidden sm:block">
                                {user.full_name || userEmail}
                                <span className="ml-1 text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
                                    {user.subscription_plan || 'Free'}
                                </span>
                            </span>
                            <button
                                onClick={handleLogout}
                                className="text-sm text-red-600 hover:text-red-800 font-medium border border-red-200 px-3 py-1 rounded hover:bg-red-50"
                            >
                                Çıkış
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Ana İçerik */}
            <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Sol Kolon: Gruplar ve Bağlantı */}
                    <div className="space-y-6">
                        <WhatsAppConnect onConnectionChange={(isConnected) => {
                            // If connected or just synced, we might want to refresh groups
                            // Use a simple key change or context to force refresh if simpler
                            // Or better: Pass a "refreshGroups" callback
                            if (isConnected) {
                                // Trigger group refresh via event or prop
                                // Simple way: Update ticket/key
                                window.dispatchEvent(new Event('refreshGroups'));
                            }
                        }} />
                        <GroupManager onSelectionChange={setSelectedGroupIds} />
                    </div>

                    {/* Sağ Kolon: Plan */}
                    <div className="space-y-6">
                        <CampaignBuilder selectedGroupIds={selectedGroupIds} />
                        <LogViewer />
                    </div>
                </div>
            </main>
        </div>
    );
}
