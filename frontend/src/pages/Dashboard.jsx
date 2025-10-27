import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Briefcase, CheckCircle, Clock } from 'lucide-react';
import { projectsApi } from '../api/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_clients: 0,
    total_projects: 0,
    active_projects: 0,
    completed_projects: 0,
    total_hours_month: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await projectsApi.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Błąd ładowania statystyk:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Klienci',
      value: stats.total_clients,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Wszystkie projekty',
      value: stats.total_projects,
      icon: Briefcase,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Aktywne projekty',
      value: stats.active_projects,
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'Zakończone projekty',
      value: stats.completed_projects,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
  ];

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-1">Przegląd Twojej działalności</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Work Hours This Month */}
      <Card>
        <CardHeader>
          <CardTitle>Godziny pracy w tym miesiącu</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-baseline space-x-2">
            <span className="text-4xl font-bold text-gray-900">{stats.total_hours_month}</span>
            <span className="text-xl text-gray-600">godzin</span>
          </div>
        </CardContent>
      </Card>

      {/* Simple Chart - Projects Status */}
      <Card>
        <CardHeader>
          <CardTitle>Status Projektów</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Aktywne</span>
                <span className="text-sm text-gray-600">{stats.active_projects} projektów</span>
              </div>
              <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-yellow-500"
                  style={{ width: `${stats.total_projects ? (stats.active_projects / stats.total_projects * 100) : 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Zakończone</span>
                <span className="text-sm text-gray-600">{stats.completed_projects} projektów</span>
              </div>
              <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500"
                  style={{ width: `${stats.total_projects ? (stats.completed_projects / stats.total_projects * 100) : 0}%` }}
                ></div>
              </div>
            </div>
            <div className="pt-4 border-t">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{stats.total_projects}</p>
                <p className="text-sm text-gray-600">Wszystkich projektów</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
