import React, { useState, useEffect } from 'react';
import {
  FileText,
  Users,
  TrendingUp,
  Clock,
  ArrowRight,
  Star,
  Mail,
  CheckCircle,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { apiService } from '../services/api';
import { formatRelativeTime, getScoreBadge } from '../utils/formatters';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [realData, setRealData] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    loadRealData();
  }, []);

  const loadRealData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Check backend health
      const health = await apiService.healthCheck();
      setBackendStatus('connected');

      // Get dashboard statistics from backend
      const response = await apiService.getDashboardStats();

      if (response && response.status === 'success' && response.stats) {
        const stats = response.stats;

        // Calculate high scorers (80+ ATS score)
        const highScorers = stats.top_candidates?.filter(c => c.score >= 80).length || 0;

        setRealData({
          totalCVs: stats.total_cvs || 0,
          processedToday: stats.total_analyses || 0,
          avgScore: stats.average_ats_score || 0,
          highScorers,
          candidates: stats.top_candidates || [],
          summary: stats.total_cvs === 0
            ? 'No CVs found. Start by downloading CVs from Gmail.'
            : `Found ${stats.total_cvs} CVs with ${stats.total_analyses} analyzed. ${stats.pending_review} pending review.`,
          analysisDate: new Date(),
        });
      } else {
        // No CVs found - show empty state
        setRealData({
          totalCVs: 0,
          processedToday: 0,
          avgScore: 0,
          highScorers: 0,
          candidates: [],
          summary: 'No CVs found. Start by downloading CVs or analyzing existing ones.',
          analysisDate: new Date(),
        });
      }
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Unable to load data. Please ensure the backend is running.');
      setBackendStatus('disconnected');

      // Show empty state on error
      setRealData({
        totalCVs: 0,
        processedToday: 0,
        avgScore: 0,
        highScorers: 0,
        candidates: [],
        summary: 'Backend connection failed.',
        analysisDate: null,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadRealData();
    setRefreshing(false);
  };

  const statCards = realData ? [
    {
      title: 'Total CVs',
      value: realData.totalCVs.toString(),
      change: realData.totalCVs > 0 ? '+' + realData.totalCVs : '0',
      icon: FileText,
      color: 'from-blue-600 to-blue-700',
      trend: 'up',
    },
    {
      title: 'High Performers',
      value: realData.highScorers.toString(),
      change: `${realData.highScorers} with 80+`,
      icon: Star,
      color: 'from-primary-600 to-primary-700',
      trend: 'up',
    },
    {
      title: 'Avg ATS Score',
      value: realData.avgScore > 0 ? `${realData.avgScore}/100` : 'N/A',
      change: realData.avgScore >= 70 ? 'Good' : realData.avgScore >= 50 ? 'Fair' : realData.avgScore > 0 ? 'Low' : 'N/A',
      icon: TrendingUp,
      color: 'from-purple-600 to-purple-700',
      trend: realData.avgScore >= 70 ? 'up' : 'down',
    },
    {
      title: 'Recently Analyzed',
      value: realData.processedToday.toString(),
      change: 'CVs in collection',
      icon: CheckCircle,
      color: 'from-yellow-600 to-yellow-700',
      trend: 'up',
    },
  ] : [];

  const quickActions = [
    {
      title: 'Review CVs',
      description: 'Analyze and rank candidates',
      icon: FileText,
      action: () => navigate('/cv-review'),
      color: 'bg-blue-600',
    },
    {
      title: 'Download New CVs',
      description: 'Get CVs from Gmail',
      icon: Mail,
      action: () => navigate('/download'),
      color: 'bg-primary-600',
    },
    {
      title: 'Chat with AI',
      description: 'Ask about candidates',
      icon: Users,
      action: () => navigate('/'),
      color: 'bg-purple-600',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-12rem)]">
        <LoadingSpinner size="xl" text="Loading dashboard data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with Refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">
            Welcome to <span className="gradient-text">HR Agent</span>
          </h1>
          <p className="text-gray-400 text-lg">
            AI-powered CV screening and candidate management
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Backend Status */}
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg glass">
            <div className={`w-2 h-2 rounded-full ${
              backendStatus === 'connected' ? 'bg-green-500 animate-pulse' :
              backendStatus === 'disconnected' ? 'bg-red-500' :
              'bg-yellow-500 animate-pulse'
            }`} />
            <span className="text-sm text-gray-400">
              {backendStatus === 'connected' ? 'Connected' :
               backendStatus === 'disconnected' ? 'Disconnected' :
               'Checking...'}
            </span>
          </div>
          <Button
            variant="secondary"
            size="sm"
            icon={<RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="glass border-2 border-red-900/50 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-400 font-medium">{error}</p>
            <p className="text-sm text-gray-400 mt-1">
              Make sure the backend is running at http://127.0.0.1:8000
            </p>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="relative overflow-hidden">
              <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${stat.color} opacity-10 rounded-full blur-2xl`}></div>
              <CardContent className="relative">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color}`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <Badge variant={stat.trend === 'up' ? 'success' : 'warning'}>
                    {stat.change}
                  </Badge>
                </div>
                <p className="text-3xl font-bold text-gray-100 mb-1">{stat.value}</p>
                <p className="text-sm text-gray-400">{stat.title}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and workflows</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  return (
                    <div
                      key={index}
                      onClick={action.action}
                      className="glass glass-hover p-6 rounded-xl cursor-pointer group"
                    >
                      <div className={`w-12 h-12 rounded-xl ${action.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="font-semibold text-gray-100 mb-1">{action.title}</h3>
                      <p className="text-sm text-gray-400">{action.description}</p>
                      <div className="mt-4 flex items-center text-primary-400 text-sm font-medium group-hover:gap-2 transition-all">
                        <span>Get started</span>
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Summary Card */}
          {realData && realData.summary && (
            <Card className="mt-6 glass">
              <CardHeader>
                <CardTitle>Analysis Summary</CardTitle>
                {realData.analysisDate && (
                  <CardDescription>
                    Last updated: {formatRelativeTime(realData.analysisDate)}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 leading-relaxed">{realData.summary}</p>
                {realData.totalCVs === 0 && (
                  <div className="mt-4 flex gap-3">
                    <Button
                      variant="primary"
                      onClick={() => navigate('/download')}
                      icon={<Mail className="w-4 h-4" />}
                    >
                      Download CVs from Gmail
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => navigate('/')}
                      icon={<Users className="w-4 h-4" />}
                    >
                      Chat with AI
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Top Candidates */}
        <div>
          <Card className="sticky top-24">
            <CardHeader>
              <CardTitle>Top Candidates</CardTitle>
              <CardDescription>
                {realData && realData.candidates.length > 0
                  ? `Highest ATS scores (${realData.candidates.length} total)`
                  : 'No candidates analyzed yet'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {realData && realData.candidates.length > 0 ? (
                <>
                  <div className="space-y-4">
                    {realData.candidates.slice(0, 5).map((candidate, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 p-3 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors cursor-pointer"
                        onClick={() => navigate('/cv-review')}
                      >
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-primary-600 to-primary-700 text-white font-bold text-sm">
                          {index + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-200 truncate">
                            {candidate.name || candidate.filename || 'Unknown'}
                          </p>
                          <p className="text-xs text-gray-500 truncate">
                            {candidate.summary || 'No summary available'}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                          <Badge variant={getScoreBadge(candidate.score)}>
                            {candidate.score}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                  <Button
                    variant="outline"
                    className="w-full mt-4"
                    onClick={() => navigate('/cv-review')}
                  >
                    View All Candidates
                  </Button>
                </>
              ) : (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm mb-4">
                    No CVs analyzed yet
                  </p>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => navigate('/cv-review')}
                  >
                    Analyze CVs
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
