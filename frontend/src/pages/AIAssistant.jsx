import { useState, useEffect, useRef, useCallback, useLayoutEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Bot, Send, Trash2, Loader2, User, Mic, MicOff, Volume2, VolumeX, X } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIAssistant = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const audioChunksRef = useRef([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [speakingIndex, setSpeakingIndex] = useState(null);
  const chatContainerRef = useRef(null);
  const [showHistory, setShowHistory] = useState(false);
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    // Generate or load session ID
    const savedSessionId = localStorage.getItem('ai_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
      loadChatHistory(savedSessionId);
    } else {
      const newSessionId = `session_${Date.now()}`;
      setSessionId(newSessionId);
      localStorage.setItem('ai_session_id', newSessionId);
    }
  }, []);

  useLayoutEffect(() => {
    // Scroll to bottom when messages change - React 19 compatible
    if (chatContainerRef.current) {
      const scrollHeight = chatContainerRef.current.scrollHeight;
      chatContainerRef.current.scrollTo({
        top: scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages]);

  const scrollToBottom = useCallback(() => {
    // Defensive scroll with proper null checks
    if (chatContainerRef.current) {
      requestAnimationFrame(() => {
        if (chatContainerRef.current) {
          chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
      });
    }
  }, []);

  const loadChatHistory = async (sid) => {
    try {
      const response = await axios.post(`${API}/ai/history`, {
        session_id: sid,
        limit: 50
      });

      const formattedMessages = [];
      response.data.conversations.forEach(conv => {
        formattedMessages.push({
          type: 'user',
          text: conv.user_message,
          timestamp: conv.timestamp
        });
        formattedMessages.push({
          type: 'ai',
          text: conv.ai_response,
          timestamp: conv.timestamp
        });
      });

      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || loading) return;

    const userMessage = {
      type: 'user',
      text: inputText,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API}/ai/chat`, {
        text: inputText,
        session_id: sessionId
      });

      const aiMessage = {
        type: 'ai',
        text: response.data.response,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setError(error.response?.data?.detail || 'Nie udało się wysłać wiadomości');
      
      // Remove user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    const newSessionId = `ai-session-${Date.now()}`;
    setSessionId(newSessionId);
    localStorage.setItem('ai_session_id', newSessionId);
    setMessages([]);
    setError(null);
  };

  const loadSessions = async () => {
    console.log('🔍 loadSessions wywołana!'); // DEBUG
    try {
      // Cache busting - dodaj timestamp do URL aby wymusić świeże dane
      const cacheBuster = `?limit=50&_t=${Date.now()}`;
      console.log('📡 Wysyłam request do:', `${API}/ai/sessions${cacheBuster}`); // DEBUG
      
      const response = await axios.get(`${API}/ai/sessions${cacheBuster}`);
      console.log('✅ Odpowiedź otrzymana:', response.data); // DEBUG
      
      setSessions(response.data.sessions || []);
      setShowHistory(true);
      console.log('✅ Historia załadowana, sessions:', response.data.sessions?.length); // DEBUG
    } catch (error) {
      console.error('❌ Błąd ładowania historii:', error); // DEBUG
      setError('Nie udało się załadować historii');
      alert('Błąd ładowania historii: ' + (error.response?.data?.detail || error.message)); // ALERT dla użytkownika
    }
  };

  const loadSession = async (sid) => {
    try {
      const response = await axios.post(`${API}/ai/history`, { session_id: sid });
      const history = response.data || [];
      
      const loadedMessages = history.flatMap(h => [
        { role: 'user', content: h.user_message },
        { role: 'assistant', content: h.ai_response }
      ]);
      
      setMessages(loadedMessages);
      setSessionId(sid);
      localStorage.setItem('ai_session_id', sid);
      setShowHistory(false);
    } catch (error) {
      console.error('Błąd ładowania rozmowy:', error);
      setError('Nie udało się wczytać rozmowy');
    }
  };

  const handleDeleteHistory = async () => {
    if (!window.confirm('Czy na pewno chcesz usunąć całą historię rozmów?')) {
      return;
    }

    try {
      await axios.delete(`${API}/ai/sessions`);
      setSessions([]);
      setShowHistory(false);
      setError(null);
    } catch (error) {
      console.error('Błąd usuwania historii:', error);
      setError('Nie udało się usunąć historii');
    }
  };

  const clearChat = async () => {
    if (!window.confirm('Czy na pewno chcesz wyczyścić całą historię rozmowy?')) {
      return;
    }

    try {
      await axios.delete(`${API}/ai/history/${sessionId}`);
      setMessages([]);
      
      // Generate new session
      const newSessionId = `session_${Date.now()}`;
      setSessionId(newSessionId);
      localStorage.setItem('ai_session_id', newSessionId);
    } catch (error) {
      console.error('Error clearing chat:', error);
      setError('Nie udało się wyczyścić historii');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      audioChunksRef.current = [];
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processVoiceInput(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setError(null);
    } catch (error) {
      console.error('Error starting recording:', error);
      setError('Nie udało się rozpocząć nagrywania. Sprawdź uprawnienia mikrofonu.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const processVoiceInput = async (audioBlob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      // Convert voice to text using Whisper
      const response = await axios.post(`${API}/ai/voice-to-text`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const transcribedText = response.data.text;
      
      if (transcribedText) {
        // Set the transcribed text and send it
        setInputText(transcribedText);
        
        // Automatically send the message
        const userMessage = {
          type: 'user',
          text: transcribedText,
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);

        const chatResponse = await axios.post(`${API}/ai/chat`, {
          text: transcribedText,
          session_id: sessionId
        });

        const aiMessage = {
          type: 'ai',
          text: chatResponse.data.response,
          timestamp: chatResponse.data.timestamp
        };

        setMessages(prev => [...prev, aiMessage]);
        setInputText('');
      }
    } catch (error) {
      console.error('Error processing voice:', error);
      setError('Nie udało się przetworzyć nagrania głosowego');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const speakText = (text, index) => {
    // Stop any current speech
    window.speechSynthesis.cancel();
    
    if (speakingIndex === index) {
      // If already speaking this message, stop it
      setSpeakingIndex(null);
      return;
    }
    
    // Start speaking
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pl-PL';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    utterance.onend = () => {
      setSpeakingIndex(null);
    };
    
    utterance.onerror = () => {
      setSpeakingIndex(null);
    };
    
    setSpeakingIndex(index);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-120px)] flex flex-col">
      <div className="mb-4">
        <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Bot className="h-8 w-8 text-blue-600" />
          Asystent AI
        </h2>
        <p className="text-gray-600 mt-1">
          Twój inteligentny pomocnik biznesowy
        </p>
      </div>

      <Card className="flex-1 flex flex-col">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b">
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2 text-blue-900">
              <Bot className="h-5 w-5" />
              Chat z Claude Sonnet 4
            </CardTitle>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  console.log('🔘 Przycisk Historia kliknięty!'); // DEBUG
                  loadSessions();
                }}
              >
                📜 Historia
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={startNewConversation}
              >
                ➕ Nowa
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={clearChat}
                disabled={messages.length === 0}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Wyczyść
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col pt-6 overflow-hidden">
          {/* Messages Area */}
          <div ref={chatContainerRef} className="flex-1 overflow-y-auto mb-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 py-12">
                <Bot className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">Witaj! Jestem Twoim asystentem AI.</p>
                <p className="text-sm mt-2">Jak mogę Ci dzisiaj pomóc?</p>
                <div className="mt-6 text-left max-w-md mx-auto">
                  <p className="text-sm font-medium mb-2">Przykładowe pytania:</p>
                  <ul className="text-sm space-y-1 text-gray-600">
                    <li>• Ile mam aktywnych projektów?</li>
                    <li>• Jak obliczć przekrój kabla dla 10kW?</li>
                    <li>• Pokaż raport z ostatniego tygodnia</li>
                    <li>• Jakie materiały potrzebuję do instalacji?</li>
                  </ul>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.type === 'ai' && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                      <Bot className="h-5 w-5 text-blue-600" />
                    </div>
                  </div>
                )}

                <div
                  className={`max-w-[70%] rounded-lg px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.text}</p>
                  <div className="flex items-center justify-between mt-1">
                    <p
                      className={`text-xs ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {new Date(message.timestamp).toLocaleTimeString('pl-PL', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                    {message.type === 'ai' && (
                      <button
                        onClick={() => speakText(message.text, index)}
                        className="ml-2 p-1 hover:bg-gray-200 rounded transition-colors"
                        title={speakingIndex === index ? "Zatrzymaj" : "Słuchaj"}
                      >
                        {speakingIndex === index ? (
                          <VolumeX className="h-4 w-4 text-blue-600" />
                        ) : (
                          <Volume2 className="h-4 w-4 text-gray-600" />
                        )}
                      </button>
                    )}
                  </div>
                </div>

                {message.type === 'user' && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                      <User className="h-5 w-5 text-gray-600" />
                    </div>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 justify-start">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-blue-600" />
                  </div>
                </div>
                <div className="bg-gray-100 rounded-lg px-4 py-3">
                  <Loader2 className="h-5 w-5 animate-spin text-gray-600" />
                </div>
              </div>
            )}
          </div>

          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Input Area */}
          <div className="border-t pt-4">
            <div className="flex gap-2">
              <Textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Napisz wiadomość... (Enter aby wysłać, Shift+Enter dla nowej linii)"
                className="flex-1 min-h-[60px] max-h-[200px] resize-none"
                disabled={loading || isRecording}
              />
              <div className="flex flex-col gap-2">
                <Button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={loading}
                  className={`${
                    isRecording 
                      ? 'bg-red-600 hover:bg-red-700' 
                      : 'bg-purple-600 hover:bg-purple-700'
                  } px-6`}
                >
                  {isRecording ? (
                    <MicOff className="h-5 w-5" />
                  ) : (
                    <Mic className="h-5 w-5" />
                  )}
                </Button>
                <Button
                  onClick={sendMessage}
                  disabled={loading || !inputText.trim() || isRecording}
                  className="bg-blue-600 hover:bg-blue-700 px-6"
                >
                  {loading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </Button>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Powered by Claude Sonnet 4 + OpenAI Whisper • {isRecording ? '🔴 Nagrywanie...' : 'Konwersacja jest zapisywana'}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIAssistant;
