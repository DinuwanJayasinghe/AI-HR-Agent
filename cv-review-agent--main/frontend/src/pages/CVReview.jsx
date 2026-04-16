import React, { useState } from 'react';
import {
  Search,
  Filter,
  Download,
  Eye,
  Star,
  TrendingUp,
  FileText,
  Mail,
  X,
} from 'lucide-react';
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import Textarea from '../components/ui/Textarea';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { apiService } from '../services/api';
import { getScoreBadge, formatDate, extractNameFromEmail } from '../utils/formatters';

const CVReview = () => {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [candidates, setCandidates] = useState([]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [scoreFilter, setScoreFilter] = useState('all');
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [showAnalyzeModal, setShowAnalyzeModal] = useState(false);

  const scoreFilterOptions = [
    { value: 'all', label: 'All Scores' },
    { value: 'excellent', label: 'Excellent (80+)' },
    { value: 'good', label: 'Good (60-79)' },
    { value: 'average', label: 'Average (40-59)' },
    { value: 'poor', label: 'Poor (0-39)' },
  ];

  const handleAnalyzeCVs = async () => {
    setAnalyzing(true);
    try {
      const response = await apiService.reviewCVs({
        jobDescription,
        useDrive: false,
        folderId: '',
      });

      if (response.top_10_candidates) {
        setCandidates(response.top_10_candidates);
        setFilteredCandidates(response.top_10_candidates);
        setShowAnalyzeModal(false);
      }
    } catch (error) {
      console.error('Error analyzing CVs:', error);
      alert('Failed to analyze CVs. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
    filterCandidates(value, scoreFilter);
  };

  const handleScoreFilter = (value) => {
    setScoreFilter(value);
    filterCandidates(searchTerm, value);
  };

  const filterCandidates = (search, score) => {
    let filtered = [...candidates];

    // Search filter
    if (search) {
      filtered = filtered.filter(
        (candidate) =>
          candidate.file_name?.toLowerCase().includes(search.toLowerCase()) ||
          candidate.sender?.toLowerCase().includes(search.toLowerCase()) ||
          candidate.keywords?.some((keyword) =>
            keyword.toLowerCase().includes(search.toLowerCase())
          )
      );
    }

    // Score filter
    if (score !== 'all') {
      filtered = filtered.filter((candidate) => {
        const atsScore = candidate.ats_score || 0;
        switch (score) {
          case 'excellent':
            return atsScore >= 80;
          case 'good':
            return atsScore >= 60 && atsScore < 80;
          case 'average':
            return atsScore >= 40 && atsScore < 60;
          case 'poor':
            return atsScore < 40;
          default:
            return true;
        }
      });
    }

    setFilteredCandidates(filtered);
  };

  const viewDetails = (candidate) => {
    setSelectedCandidate(candidate);
    setShowDetailsModal(true);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-100">CV Review & Analysis</h1>
          <p className="text-gray-400 mt-1">
            Review, rank, and manage candidate applications
          </p>
        </div>
        <Button
          variant="primary"
          icon={<TrendingUp className="w-4 h-4" />}
          onClick={() => setShowAnalyzeModal(true)}
        >
          Analyze CVs
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              placeholder="Search by name, file, or skills..."
              icon={<Search className="w-5 h-5" />}
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
            />
            <Select
              options={scoreFilterOptions}
              value={scoreFilter}
              onChange={(e) => handleScoreFilter(e.target.value)}
              placeholder="Filter by ATS score"
            />
            <Button variant="secondary" icon={<Filter className="w-4 h-4" />}>
              More Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" text="Loading candidates..." />
        </div>
      ) : filteredCandidates.length === 0 ? (
        <Card className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-300 mb-2">No CVs Analyzed Yet</h3>
          <p className="text-gray-500 mb-6">
            Click "Analyze CVs" to review resumes from your cv_collection folder
          </p>
          <Button
            variant="primary"
            onClick={() => setShowAnalyzeModal(true)}
            icon={<TrendingUp className="w-4 h-4" />}
          >
            Start Analysis
          </Button>
        </Card>
      ) : (
        <>
          <div className="flex items-center justify-between mb-4">
            <p className="text-gray-400">
              Showing <span className="text-primary-400 font-semibold">{filteredCandidates.length}</span> candidates
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {filteredCandidates.map((candidate, index) => (
              <Card key={index} hover className="cursor-pointer">
                <CardContent>
                  <div className="flex flex-col md:flex-row md:items-center gap-4">
                    {/* Rank */}
                    <div className="flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-primary-600 to-primary-700 text-white font-bold text-lg flex-shrink-0">
                      {candidate.rank || index + 1}
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-100 truncate">
                          {extractNameFromEmail(candidate.sender) || candidate.file_name}
                        </h3>
                        <Badge variant={getScoreBadge(candidate.ats_score)}>
                          {candidate.ats_score}/100
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-400 mb-2 truncate">
                        {candidate.original_filename || candidate.file_name}
                      </p>

                      {/* Keywords */}
                      {candidate.keywords && candidate.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-3">
                          {candidate.keywords.slice(0, 5).map((keyword, i) => (
                            <span
                              key={i}
                              className="px-2 py-1 bg-dark-700 text-gray-300 text-xs rounded-md"
                            >
                              {keyword}
                            </span>
                          ))}
                          {candidate.keywords.length > 5 && (
                            <span className="px-2 py-1 bg-dark-700 text-gray-400 text-xs rounded-md">
                              +{candidate.keywords.length - 5} more
                            </span>
                          )}
                        </div>
                      )}

                      {/* Strengths Preview */}
                      {candidate.strengths && candidate.strengths.length > 0 && (
                        <div className="flex items-start gap-2">
                          <Star className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-gray-400 line-clamp-2">
                            {candidate.strengths[0]}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        icon={<Eye className="w-4 h-4" />}
                        onClick={() => viewDetails(candidate)}
                      >
                        Details
                      </Button>
                      {candidate.sender && (
                        <Button
                          variant="secondary"
                          size="sm"
                          icon={<Mail className="w-4 h-4" />}
                        >
                          Contact
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}

      {/* Analyze Modal */}
      <Modal
        isOpen={showAnalyzeModal}
        onClose={() => setShowAnalyzeModal(false)}
        title="Analyze CVs"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-400">
            Analyze all CVs in your collection folder and rank them based on ATS compatibility.
          </p>

          <Textarea
            label="Job Description (Optional)"
            placeholder="Enter the job description to get more accurate matching..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={6}
          />

          <div className="glass p-4 rounded-lg">
            <h4 className="text-sm font-semibold text-gray-300 mb-2">What will happen:</h4>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Analyze all CVs in cv_collection folder</li>
              <li>• Calculate ATS compatibility scores</li>
              <li>• Rank candidates by score</li>
              <li>• Extract keywords and skills</li>
              <li>• Identify strengths and improvements</li>
            </ul>
          </div>

          <div className="flex gap-3">
            <Button
              variant="primary"
              onClick={handleAnalyzeCVs}
              loading={analyzing}
              className="flex-1"
            >
              Start Analysis
            </Button>
            <Button
              variant="secondary"
              onClick={() => setShowAnalyzeModal(false)}
              disabled={analyzing}
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      {/* Details Modal */}
      <Modal
        isOpen={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
        title="Candidate Details"
        size="lg"
      >
        {selectedCandidate && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-2xl font-bold text-gray-100 mb-2">
                  {extractNameFromEmail(selectedCandidate.sender) || 'Candidate'}
                </h3>
                <p className="text-gray-400">{selectedCandidate.sender}</p>
              </div>
              <Badge
                variant={getScoreBadge(selectedCandidate.ats_score)}
                className="text-lg px-4 py-2"
              >
                Score: {selectedCandidate.ats_score}/100
              </Badge>
            </div>

            {/* File Info */}
            <div className="glass p-4 rounded-lg">
              <p className="text-sm text-gray-400 mb-1">CV File</p>
              <p className="text-gray-200 font-medium">{selectedCandidate.file_name}</p>
            </div>

            {/* Keywords */}
            {selectedCandidate.keywords && selectedCandidate.keywords.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-100 mb-3">Skills & Keywords</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedCandidate.keywords.map((keyword, i) => (
                    <span
                      key={i}
                      className="px-3 py-1.5 bg-primary-900/30 text-primary-400 text-sm rounded-lg border border-primary-800/50"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Strengths */}
            {selectedCandidate.strengths && selectedCandidate.strengths.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-100 mb-3 flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-500" />
                  Strengths
                </h4>
                <ul className="space-y-2">
                  {selectedCandidate.strengths.map((strength, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-primary-400 mt-1">•</span>
                      <span className="text-gray-300">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvements */}
            {selectedCandidate.improvements && selectedCandidate.improvements.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-100 mb-3">Areas for Improvement</h4>
                <ul className="space-y-2">
                  {selectedCandidate.improvements.map((improvement, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-yellow-400 mt-1">•</span>
                      <span className="text-gray-300">{improvement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Assessment */}
            {selectedCandidate.assessment && (
              <div>
                <h4 className="text-lg font-semibold text-gray-100 mb-3">Overall Assessment</h4>
                <div className="glass p-4 rounded-lg">
                  <p className="text-gray-300 leading-relaxed">{selectedCandidate.assessment}</p>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t border-dark-700">
              <Button variant="primary" icon={<Mail className="w-4 h-4" />} className="flex-1">
                Send Email
              </Button>
              <Button variant="secondary" icon={<Download className="w-4 h-4" />}>
                Download CV
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default CVReview;
