import React, { useState } from 'react';
import {
  Download,
  Calendar,
  Mail,
  FileText,
  CheckCircle,
  AlertCircle,
  Inbox,
} from 'lucide-react';
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import Textarea from '../components/ui/Textarea';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Badge from '../components/ui/Badge';
import { apiService } from '../services/api';
import { DATE_RANGE_OPTIONS } from '../utils/constants';
import { formatDate } from '../utils/formatters';

const DownloadCVs = () => {
  const [loading, setLoading] = useState(false);
  const [daysBack, setDaysBack] = useState('7');
  const [jobPosition, setJobPosition] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [analyze, setAnalyze] = useState(true);
  const [downloadResult, setDownloadResult] = useState(null);

  const handleDownload = async () => {
    setLoading(true);
    setDownloadResult(null);

    try {
      const response = await apiService.downloadCVsByDate({
        daysBack: parseInt(daysBack),
        jobPosition,
        jobDescription,
        analyze,
      });

      setDownloadResult(response);
    } catch (error) {
      console.error('Error downloading CVs:', error);
      alert('Failed to download CVs. Please check your backend connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Download CVs from Gmail</h1>
        <p className="text-gray-400 mt-1">
          Download and analyze CVs from your Gmail inbox by date range
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Download Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Download Settings</CardTitle>
              <CardDescription>
                Configure your CV download and analysis preferences
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Date Range */}
                <div>
                  <Select
                    label="Time Period"
                    options={DATE_RANGE_OPTIONS}
                    value={daysBack}
                    onChange={(e) => setDaysBack(e.target.value)}
                    required
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Download CVs received in the last {daysBack} days
                  </p>
                </div>

                {/* Job Position Filter */}
                <Input
                  label="Job Position Filter (Optional)"
                  placeholder="e.g., Software Engineer, Data Scientist"
                  value={jobPosition}
                  onChange={(e) => setJobPosition(e.target.value)}
                  icon={<FileText className="w-5 h-5" />}
                />

                {/* Job Description */}
                <Textarea
                  label="Job Description (Optional)"
                  placeholder="Enter job description for better matching and analysis..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={6}
                />

                {/* Analyze Option */}
                <div className="glass p-4 rounded-lg">
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      id="analyze"
                      checked={analyze}
                      onChange={(e) => setAnalyze(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-2 focus:ring-primary-600"
                    />
                    <div className="flex-1">
                      <label htmlFor="analyze" className="font-medium text-gray-200 cursor-pointer">
                        Analyze CVs after download
                      </label>
                      <p className="text-sm text-gray-400 mt-1">
                        Automatically analyze and rank downloaded CVs using AI
                      </p>
                    </div>
                  </div>
                </div>

                {/* Action Button */}
                <Button
                  variant="primary"
                  onClick={handleDownload}
                  loading={loading}
                  icon={<Download className="w-4 h-4" />}
                  className="w-full"
                  size="lg"
                >
                  Download & Process CVs
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          {downloadResult && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-primary-500" />
                  Download Completed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Summary */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="glass p-4 rounded-lg text-center">
                      <Mail className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-gray-100">
                        {downloadResult.download_summary?.emails_processed || 0}
                      </p>
                      <p className="text-sm text-gray-400">Emails</p>
                    </div>
                    <div className="glass p-4 rounded-lg text-center">
                      <Download className="w-6 h-6 text-primary-400 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-gray-100">
                        {downloadResult.download_summary?.cvs_downloaded || 0}
                      </p>
                      <p className="text-sm text-gray-400">Downloaded</p>
                    </div>
                    <div className="glass p-4 rounded-lg text-center">
                      <FileText className="w-6 h-6 text-purple-400 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-gray-100">
                        {downloadResult.analysis_summary?.total_analyzed || 0}
                      </p>
                      <p className="text-sm text-gray-400">Analyzed</p>
                    </div>
                    <div className="glass p-4 rounded-lg text-center">
                      <Calendar className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-gray-100">
                        {downloadResult.download_summary?.days_back || 0}
                      </p>
                      <p className="text-sm text-gray-400">Days</p>
                    </div>
                  </div>

                  {/* Summary Text */}
                  <div className="glass p-4 rounded-lg">
                    <p className="text-gray-300 leading-relaxed">
                      {downloadResult.summary || 'CVs downloaded successfully.'}
                    </p>
                  </div>

                  {/* Top Candidates */}
                  {downloadResult.top_10_candidates &&
                    downloadResult.top_10_candidates.length > 0 && (
                      <div>
                        <h4 className="text-lg font-semibold text-gray-100 mb-3">
                          Top Candidates
                        </h4>
                        <div className="space-y-2">
                          {downloadResult.top_10_candidates.slice(0, 5).map((candidate, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-3 rounded-lg bg-dark-700/50"
                            >
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-600 to-primary-700 text-white font-bold text-sm flex items-center justify-center">
                                  {candidate.rank || index + 1}
                                </div>
                                <div>
                                  <p className="text-gray-200 font-medium">{candidate.original_filename}</p>
                                  <p className="text-sm text-gray-500">{candidate.sender}</p>
                                </div>
                              </div>
                              <Badge
                                variant={
                                  candidate.ats_score >= 80
                                    ? 'success'
                                    : candidate.ats_score >= 60
                                    ? 'warning'
                                    : 'error'
                                }
                              >
                                {candidate.ats_score}/100
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Info Sidebar */}
        <div className="space-y-6">
          {/* Info Card */}
          <Card>
            <CardHeader>
              <CardTitle>How it Works</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 text-sm text-gray-400">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary-400 font-semibold">1</span>
                  </div>
                  <p>Connect to your Gmail account using IMAP</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary-400 font-semibold">2</span>
                  </div>
                  <p>Search for CVs within the selected time period</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary-400 font-semibold">3</span>
                  </div>
                  <p>Download CV attachments (PDF, DOC, DOCX)</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary-400 font-semibold">4</span>
                  </div>
                  <p>Send acknowledgment emails to applicants</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary-400 font-semibold">5</span>
                  </div>
                  <p>Analyze and rank CVs using AI (optional)</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tips Card */}
          <Card className="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-yellow-500" />
                Tips
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>• Use job position filter to target specific roles</li>
                <li>• Provide job description for better matching</li>
                <li>• Enable analysis to automatically rank candidates</li>
                <li>• Check cv_collection folder for downloaded files</li>
                <li>• Review cv_senders_log.csv for applicant contacts</li>
              </ul>
            </CardContent>
          </Card>

          {/* Status Card */}
          <Card className="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Inbox className="w-5 h-5 text-primary-500" />
                Gmail Connection
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse"></div>
                <span className="text-sm text-gray-400">Ready to download</span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                hr.agent.automation@gmail.com
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DownloadCVs;
