import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Mic, MicOff, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VoiceReport = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [commandType, setCommandType] = useState('daily_report');
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const audioChunksRef = useRef([]);
  const navigate = useNavigate();

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
    setProcessing(true);
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
        setTranscript(prev => prev + ' ' + transcribedText);
      }
    } catch (error) {
      console.error('Error processing voice:', error);
      setError('Nie udało się przetworzyć nagrania głosowego');
    } finally {
      setProcessing(false);
    }
  };

  const startListening = startRecording;
  const stopListening = stopRecording;

  const processTranscript = async () => {
    if (!transcript.trim()) {
      setError('Brak nagranej treści do przetworzenia');
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API}/voice/process`, {
        transcript: transcript,
        command_type: commandType
      });

      setResult(response.data);
      setTranscript('');
      
      // Pokazz sukces przez 3 sekundy, potem przekieruj
      setTimeout(() => {
        if (commandType === 'work_hours') {
          navigate('/workhours');
        } else {
          navigate('/reports');
        }
      }, 3000);
    } catch (error) {
      console.error('Error processing voice:', error);
      setError(error.response?.data?.detail || 'Błąd przetwarzania nagrania');
    } finally {
      setProcessing(false);
    }
  };

  const getInstructions = () => {
    if (commandType === 'work_hours') {
      return (
        <div className="text-sm text-gray-600 space-y-1">
          <p><strong>Przykład:</strong></p>
          <p className="italic">"Zapisz godziny pracy z dnia dzisiejszego. Bartosz Kowalski 9 godzin, Norbert Fronckiewicz 9 godzin."</p>
        </div>
      );
    } else {
      return (
        <div className="text-sm text-gray-600 space-y-1">
          <p><strong>Przykład:</strong></p>
          <p className="italic">"Zapisz raport z dzisiejszego dnia. Klient Jan Kowalski. Wykonane prace: rozciągnięcie instalacji oświetlenia garaż, wykopanie 20 metrów przyłącza. Materiały zużyte: kabel 5 na 10, 30 metrów, puszki 20 sztuk, bezpieczniki B16 8 sztuk, paliwo 6 litrów. Dodatkowe informacje: 3 osoby, 9 godzin, koparka 5 godzin, podnośnik 3 godziny, praca przebiegła bez problemów."</p>
        </div>
      );
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Raport Głosowy</h2>
        <p className="text-gray-600 mt-1">Nagraj swój raport za pomocą mikrofonu</p>
      </div>

      {/* Microphone permission will be requested when user clicks record button */}

      <Card>
        <CardHeader className="bg-gradient-to-r from-green-50 to-green-100 border-b">
          <CardTitle className="flex items-center gap-2 text-green-900">
            <Mic className="h-5 w-5" />
            Nagrywanie głosowe
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Typ komendy
            </label>
            <Select value={commandType} onValueChange={setCommandType} disabled={isRecording}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily_report">Raport dzienny</SelectItem>
                <SelectItem value="work_hours">Godziny pracy</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {getInstructions()}

          <div className="flex justify-center gap-4">
            {!isListening ? (
              <Button
                onClick={startListening}
                disabled={!supported || processing || micPermission === 'denied'}
                className="bg-green-500 hover:bg-green-600 text-white px-8 py-6 text-lg disabled:opacity-50"
              >
                <Mic className="h-6 w-6 mr-2" />
                Rozpocznij nagrywanie
              </Button>
            ) : (
              <Button
                onClick={stopListening}
                className="bg-red-500 hover:bg-red-600 text-white px-8 py-6 text-lg"
              >
                <MicOff className="h-6 w-6 mr-2" />
                Zatrzymaj nagrywanie
              </Button>
            )}
          </div>

          {isListening && (
            <div className="text-center">
              <div className="inline-flex items-center gap-2 text-red-600 animate-pulse">
                <div className="w-3 h-3 bg-red-600 rounded-full"></div>
                <span className="font-medium">Nagrywanie w toku...</span>
              </div>
            </div>
          )}

          {transcript && (
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rozpoznany tekst:
              </label>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-gray-800 whitespace-pre-wrap">{transcript}</p>
              </div>
              <div className="flex justify-end mt-4">
                <Button
                  onClick={processTranscript}
                  disabled={processing || !transcript.trim()}
                  className="bg-blue-500 hover:bg-blue-600"
                >
                  {processing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Przetwarzanie...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Zapisz raport
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                <strong>Sukces!</strong> 
                {result.type === 'work_hours' 
                  ? ` Zapisano godziny pracy dla ${result.data.workers?.length || 0} pracowników.`
                  : ` Utworzono raport dzienny: ${result.data.title}.`
                }
                {result.client_found === false && ' (Klient nie znaleziony w bazie - utworzono nowy raport)'}
                <br />
                <span className="text-sm">Przekierowywanie...</span>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default VoiceReport;
