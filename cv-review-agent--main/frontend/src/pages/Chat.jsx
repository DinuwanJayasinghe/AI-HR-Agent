import { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  User,
  Loader2,
  Lightbulb,
  Trash2,
} from 'lucide-react';
import Button from '../components/ui/Button';
import { apiService } from '../services/api';
import { CHAT_SUGGESTIONS } from '../utils/constants';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Hello! I\'m your AI HR Assistant. I can help you download CVs, analyze candidates, send acknowledgment emails, and answer questions about your applicants. How can I help you today?',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  const handleSend = async (messageText = input) => {
    if (!messageText.trim() || loading) return;

    const userMessage = { role: 'user', content: messageText };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setStreamingMessage('');

    let finalResponse = '';

    try {
      // Use streaming API
      await apiService.chatStream(
        {
          message: messageText,
          conversationHistory: messages.slice(1).map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        },
        (data) => {
          // Handle streaming data
          if (data.response) {
            finalResponse = data.response;
            setStreamingMessage(data.response);
          }
        },
        (error) => {
          console.error('Streaming error:', error);
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: 'Sorry, I encountered an error. Please try again.',
            },
          ]);
          setLoading(false);
          setStreamingMessage('');
        }
      );

      // After streaming completes, add the final message
      if (finalResponse) {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: finalResponse },
        ]);
      }
      setStreamingMessage('');
    } catch (error) {
      // Fallback to non-streaming API
      try {
        const response = await apiService.chat({
          message: messageText,
          conversationHistory: messages.slice(1).map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        });

        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: response.response },
        ]);
      } catch (fallbackError) {
        console.error('Chat error:', fallbackError);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content:
              'Sorry, I couldn\'t connect to the backend. Please make sure the server is running.',
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSend(suggestion);
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content:
          'Chat cleared! How can I help you with CV management today?',
      },
    ]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] -mx-6 -mt-6 bg-dark-900">
      {/* Header */}
      <div className="bg-dark-800 border-b border-dark-700 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center shadow-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">AI Assistant</h1>
            <p className="text-xs text-gray-400">Your intelligent HR automation assistant</p>
          </div>
        </div>
        <Button
          variant="secondary"
          size="sm"
          icon={<Trash2 className="w-4 h-4" />}
          onClick={handleClearChat}
        >
          Clear Chat
        </Button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-4 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-900/30">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-2xl px-6 py-4 ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg shadow-primary-900/30'
                  : 'bg-dark-800 border border-dark-700'
              }`}
            >
              <p className="text-base leading-relaxed whitespace-pre-wrap">
                {message.content}
              </p>
            </div>
            {message.role === 'user' && (
              <div className="w-10 h-10 rounded-xl bg-dark-700 flex items-center justify-center flex-shrink-0 border border-dark-600">
                <User className="w-5 h-5 text-gray-400" />
              </div>
            )}
          </div>
        ))}

        {/* Streaming Message */}
        {streamingMessage && (
          <div className="flex gap-4 justify-start">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-900/30">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="max-w-[75%] bg-dark-800 border border-dark-700 rounded-2xl px-6 py-4">
              <p className="text-base leading-relaxed whitespace-pre-wrap">
                {streamingMessage}
              </p>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && !streamingMessage && (
          <div className="flex gap-4 justify-start">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-900/30 animate-pulse">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="bg-dark-800 border border-dark-700 rounded-2xl px-6 py-4">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-primary-400" />
                <span className="text-base text-gray-300">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-dark-700 bg-dark-800 px-6 py-4 flex-shrink-0">
        <div className="space-y-3">
          <div className="flex gap-3 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask me anything about CVs, candidates, or automation..."
              rows="1"
              className="flex-1 bg-dark-700 border border-dark-600 focus:border-primary-600 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-600/50 resize-none max-h-32 text-sm transition-all"
              disabled={loading}
            />
            <Button
              variant="primary"
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              icon={loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              className="px-6 py-3 rounded-xl"
            >
              Send
            </Button>
          </div>

          {/* Quick Suggestions */}
          <div className="flex flex-wrap gap-2">
            {CHAT_SUGGESTIONS.slice(0, 4).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                disabled={loading}
                className="px-3 py-1.5 rounded-lg bg-dark-700/50 hover:bg-dark-600 border border-dark-600 hover:border-primary-700/50 text-xs text-gray-300 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-primary-900/20"
              >
                <Lightbulb className="w-3 h-3 inline mr-1.5 text-yellow-500" />
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
