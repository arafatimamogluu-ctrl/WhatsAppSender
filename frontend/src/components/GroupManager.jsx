import React, { useEffect, useState } from 'react';
import api from '../api';
import { Trash2, Users } from 'lucide-react';

export default function GroupManager({ onSelectionChange }) {
    const [groups, setGroups] = useState([]);
    const [newGroupName, setNewGroupName] = useState('');
    const [newGroupTarget, setNewGroupTarget] = useState('');
    const [selectedIds, setSelectedIds] = useState([]);

    const userId = localStorage.getItem('user_id');

    const handleSelection = (id) => {
        const newSelection = selectedIds.includes(id)
            ? selectedIds.filter(x => x !== id)
            : [...selectedIds, id];

        setSelectedIds(newSelection);
        if (onSelectionChange) onSelectionChange(newSelection); // Identify by target_identifier usually, but here ID is safer for DB ops?
        // Wait, CampaignBuilder expects Group IDs (target_identifier string) or DB IDs?
        // Backend `Campaign` model uses `target_group_ids` string.
        // Let's pass the valid identifier. 
        // `groups` array elements have `group_id` as target_identifier (see user_routes get_my_groups). 
        // Let's verify what `fetchGroups` returns.
    };

    const toggleAll = () => {
        if (selectedIds.length === groups.length) {
            setSelectedIds([]);
            if (onSelectionChange) onSelectionChange([]);
        } else {
            // We need to know what identifier to use.
            // From user_routes.py: Response is { groups: [{name, group_id, ...}] }
            // group_id IS the target_identifier.
            const allIds = groups.map(g => g.group_id);
            setSelectedIds(allIds);
            if (onSelectionChange) onSelectionChange(allIds);
        }
    };

    const fetchGroups = async () => {
        if (!userId) return;
        try {
            const res = await api.get(`/manage/groups/${userId}`);
            // Fix: res.data might be { groups: [...] } or just [...] depend on backend router
            // user_routes get_my_groups returns { groups: [] }
            // API client might unwrap? No, usually res.data is the JSON.
            // Let's check api.js or assume standard axios.
            // If backend returns dict with "groups" key:
            const list = res.data.groups || res.data;
            setGroups(list);
        } catch (error) {
            console.error("Grup getirme hatası", error);
        }
    };

    useEffect(() => {
        fetchGroups();

        // Listen for refresh events from other components
        const handleRefresh = () => fetchGroups();
        window.addEventListener('refreshGroups', handleRefresh);
        return () => window.removeEventListener('refreshGroups', handleRefresh);
    }, [userId]);

    const addGroup = async (e) => {
        e.preventDefault();
        if (!newGroupName || !newGroupTarget) return;
        try {
            await api.post('/manage/groups', {
                user_id: parseInt(userId),
                name: newGroupName,
                group_id: newGroupTarget // Backend expects group_id in GroupCreate model
            });
            setNewGroupName('');
            setNewGroupTarget('');
            fetchGroups();
        } catch (error) {
            alert("Grup eklenirken hata oluştu");
        }
    };

    const deleteGroup = async (id) => {
        if (!confirm("Silmek istiyor musunuz?")) return;
        try {
            await api.delete(`/manage/groups/${id}`);
            fetchGroups();
        } catch (error) {
            alert("Silme hatası");
        }
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
                <Users className="text-blue-600" /> Hedef Gruplar ({groups.length})
            </h3>

            {/* Liste */}
            <div className="overflow-x-auto mb-6 max-h-96 overflow-y-auto border rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50 sticky top-0">
                        <tr>
                            <th className="px-6 py-3 text-left w-10">
                                <input type="checkbox" onChange={toggleAll} checked={groups.length > 0 && selectedIds.length === groups.length} />
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grup Adı</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hedef (ID)</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">İşlem</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {groups.map((g) => (
                            <tr key={g.group_id /* Use unique ID */}>
                                <td className="px-6 py-4">
                                    <input
                                        type="checkbox"
                                        checked={selectedIds.includes(g.group_id)}
                                        onChange={() => handleSelection(g.group_id)}
                                    />
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{g.name}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{g.group_id}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button onClick={() => deleteGroup(g.group_id)} className="text-red-600 hover:text-red-900">
                                        <Trash2 size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {groups.length === 0 && (
                            <tr>
                                <td colSpan="3" className="px-6 py-4 text-center text-gray-400">Henüz grup eklenmemiş.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Ekleme Formu */}
            <form onSubmit={addGroup} className="flex gap-4 items-end bg-gray-50 p-4 rounded-md">
                <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700">Grup Takma Adı</label>
                    <input
                        type="text"
                        value={newGroupName}
                        onChange={e => setNewGroupName(e.target.value)}
                        placeholder="Örn: Aile Grubu"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                        required
                    />
                </div>
                <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700">Hedef (Tam Ad veya Numara)</label>
                    <input
                        type="text"
                        value={newGroupTarget}
                        onChange={e => setNewGroupTarget(e.target.value)}
                        placeholder="Örn: Ailem veya 905..."
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                        required
                    />
                </div>
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 font-medium h-10">
                    Ekle
                </button>
            </form>
        </div>
    );
}
