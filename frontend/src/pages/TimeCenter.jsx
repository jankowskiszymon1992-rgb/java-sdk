import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Clock, Timer, PlayCircle, PauseCircle, RotateCcw, Bell, Plus, Trash2, Power } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import axios from 'axios';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const TimeCenter = () => {
  // Clock
  const [currentTime, setCurrentTime] = useState(new Date());

  // Timer
  const [timerMinutes, setTimerMinutes] = useState(15);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [timerRunning, setTimerRunning] = useState(false);
  const [timerTotal, setTimerTotal] = useState(0);

  // Stopwatch
  const [stopwatchTime, setStopwatchTime] = useState(0);
  const [stopwatchRunning, setStopwatchRunning] = useState(false);

  // Alarms
  const [alarms, setAlarms] = useState([]);
  const [showAlarmDialog, setShowAlarmDialog] = useState(false);
  const [newAlarm, setNewAlarm] = useState({ time: '09:00', label: '' });
  const [notificationPermission, setNotificationPermission] = useState('default');

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window) {
      setNotificationPermission(Notification.permission);
      if (Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
          setNotificationPermission(permission);
          if (permission === 'granted') {
            toast.success('Powiadomienia włączone! Budziki będą działać.');
          }
        });
      }
    }
  }, []);

  // Clock update
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Timer countdown
  useEffect(() => {
    let interval;
    if (timerRunning && (timerMinutes > 0 || timerSeconds > 0)) {
      interval = setInterval(() => {
        if (timerSeconds === 0) {
          if (timerMinutes === 0) {
            setTimerRunning(false);
            playAlarmSound();
            toast.success('⏰ Timer zakończony!');
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification('Timer zakończony!', {
                body: 'Czas minął!',
                icon: '/logo.png'
              });
            }
          } else {
            setTimerMinutes(timerMinutes - 1);
            setTimerSeconds(59);
          }
        } else {
          setTimerSeconds(timerSeconds - 1);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [timerRunning, timerMinutes, timerSeconds]);

  // Stopwatch
  useEffect(() => {
    let interval;
    if (stopwatchRunning) {
      interval = setInterval(() => {
        setStopwatchTime(prev => prev + 10);
      }, 10);
    }
    return () => clearInterval(interval);
  }, [stopwatchRunning]);

  // Load alarms
  useEffect(() => {
    loadAlarms();
  }, []);

  // Check alarms
  useEffect(() => {
    const checkAlarms = () => {
      const now = new Date();
      const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
      const currentDay = now.getDay();

      alarms.forEach(alarm => {
        if (alarm.enabled && alarm.time === currentTime) {
          // Check if alarm should ring today
          if (!alarm.repeat_days || alarm.repeat_days.length === 0 || alarm.repeat_days.includes(currentDay)) {
            playAlarmSound();
            toast.success(`⏰ Budzik: ${alarm.label}`);
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification(`Budzik: ${alarm.label}`, {
                body: `Czas: ${alarm.time}`,
                icon: '/logo.png'
              });
            }
          }
        }
      });
    };

    const interval = setInterval(checkAlarms, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [alarms]);

  const playAlarmSound = () => {
    // Lepszy dźwięk budzika - 3 sekundy dzwonka
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800; // Częstotliwość dźwięku
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    
    // Odtwórz 3 razy (bip-bip-bip)
    for (let i = 0; i < 3; i++) {
      setTimeout(() => {
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        osc.connect(gain);
        gain.connect(audioContext.destination);
        osc.frequency.value = 800 + (i * 200);
        osc.type = 'sine';
        gain.gain.setValueAtTime(0.3, audioContext.currentTime);
        osc.start(audioContext.currentTime);
        osc.stop(audioContext.currentTime + 0.3);
      }, i * 500);
    }
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.3);
  };

  const testAlarm = () => {
    playAlarmSound();
    toast.success('🔔 Test budzika!');
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Test Budzika', {
        body: 'Jeśli widzisz to powiadomienie, budziki będą działać!',
        icon: '/logo192.png',
        requireInteraction: true
      });
    } else if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification('Test Budzika', {
            body: 'Powiadomienia włączone!',
            icon: '/logo192.png'
          });
        }
      });
    } else {
      toast.error('Powiadomienia zablokowane! Włącz je w ustawieniach przeglądarki.');
    }
  };

  const loadAlarms = async () => {
    try {
      const response = await axios.get(`${API}/api/alarms`);
      setAlarms(response.data);
    } catch (error) {
      console.error('Błąd ładowania budzików:', error);
    }
  };

  const startTimer = () => {
    if (timerMinutes > 0 || timerSeconds > 0) {
      setTimerTotal(timerMinutes * 60 + timerSeconds);
      setTimerRunning(true);
    }
  };

  const resetTimer = () => {
    setTimerRunning(false);
    setTimerMinutes(15);
    setTimerSeconds(0);
  };

  const formatStopwatch = (time) => {
    const minutes = Math.floor(time / 60000);
    const seconds = Math.floor((time % 60000) / 1000);
    const milliseconds = Math.floor((time % 1000) / 10);
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(milliseconds).padStart(2, '0')}`;
  };

  const addAlarm = async () => {
    if (!newAlarm.label.trim()) {
      toast.error('Wpisz nazwę budzika');
      return;
    }

    try {
      await axios.post(`${API}/api/alarms`, newAlarm);
      toast.success('Budzik dodany');
      setShowAlarmDialog(false);
      setNewAlarm({ time: '09:00', label: '' });
      loadAlarms();
    } catch (error) {
      toast.error('Nie udało się dodać budzika');
    }
  };

  const toggleAlarm = async (alarm) => {
    try {
      await axios.put(`${API}/api/alarms/${alarm.id}`, { enabled: !alarm.enabled });
      loadAlarms();
    } catch (error) {
      toast.error('Nie udało się zmienić budzika');
    }
  };

  const deleteAlarm = async (id) => {
    if (!window.confirm('Usunąć budzik?')) return;
    
    try {
      await axios.delete(`${API}/api/alarms/${id}`);
      toast.success('Budzik usunięty');
      loadAlarms();
    } catch (error) {
      toast.error('Nie udało się usunąć budzika');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Clock className="h-8 w-8 text-blue-600" />
          Centrum Czasu
        </h2>
        <p className="text-gray-600 mt-1">Zegar, Timer, Stoper i Budzik</p>
      </div>

      <Tabs defaultValue="clock" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="clock">Zegar</TabsTrigger>
          <TabsTrigger value="timer">Timer</TabsTrigger>
          <TabsTrigger value="stopwatch">Stoper</TabsTrigger>
          <TabsTrigger value="alarm">Budzik</TabsTrigger>
        </TabsList>

        {/* Clock Tab */}
        <TabsContent value="clock">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="text-8xl font-bold text-blue-600 mb-4">
                  {currentTime.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </div>
                <div className="text-2xl text-gray-600">
                  {currentTime.toLocaleDateString('pl-PL', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Timer Tab */}
        <TabsContent value="timer">
          <Card>
            <CardHeader>
              <CardTitle>Timer Odliczający</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                <div className="text-7xl font-bold text-orange-600 mb-4">
                  {String(timerMinutes).padStart(2, '0')}:{String(timerSeconds).padStart(2, '0')}
                </div>
                
                {!timerRunning && (
                  <div className="flex gap-4 justify-center mb-4">
                    <div>
                      <label className="text-sm text-gray-600">Minuty</label>
                      <Input
                        type="number"
                        value={timerMinutes}
                        onChange={(e) => setTimerMinutes(Math.max(0, parseInt(e.target.value) || 0))}
                        className="w-24 text-center text-2xl"
                        min="0"
                        max="99"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Sekundy</label>
                      <Input
                        type="number"
                        value={timerSeconds}
                        onChange={(e) => setTimerSeconds(Math.max(0, Math.min(59, parseInt(e.target.value) || 0)))}
                        className="w-24 text-center text-2xl"
                        min="0"
                        max="59"
                      />
                    </div>
                  </div>
                )}

                <div className="flex gap-3 justify-center">
                  <Button
                    onClick={() => timerRunning ? setTimerRunning(false) : startTimer()}
                    className="bg-orange-600 hover:bg-orange-700"
                    size="lg"
                  >
                    {timerRunning ? <PauseCircle className="h-6 w-6 mr-2" /> : <PlayCircle className="h-6 w-6 mr-2" />}
                    {timerRunning ? 'Pauza' : 'Start'}
                  </Button>
                  <Button onClick={resetTimer} variant="outline" size="lg">
                    <RotateCcw className="h-6 w-6 mr-2" />
                    Reset
                  </Button>
                </div>

                <div className="mt-6 flex gap-2 justify-center">
                  {[5, 10, 15, 30].map(min => (
                    <Button
                      key={min}
                      onClick={() => { setTimerMinutes(min); setTimerSeconds(0); }}
                      variant="outline"
                      size="sm"
                      disabled={timerRunning}
                    >
                      {min} min
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Stopwatch Tab */}
        <TabsContent value="stopwatch">
          <Card>
            <CardHeader>
              <CardTitle>Stoper</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                <div className="text-7xl font-bold text-green-600 mb-6">
                  {formatStopwatch(stopwatchTime)}
                </div>
                
                <div className="flex gap-3 justify-center">
                  <Button
                    onClick={() => setStopwatchRunning(!stopwatchRunning)}
                    className="bg-green-600 hover:bg-green-700"
                    size="lg"
                  >
                    {stopwatchRunning ? <PauseCircle className="h-6 w-6 mr-2" /> : <PlayCircle className="h-6 w-6 mr-2" />}
                    {stopwatchRunning ? 'Pauza' : 'Start'}
                  </Button>
                  <Button
                    onClick={() => { setStopwatchTime(0); setStopwatchRunning(false); }}
                    variant="outline"
                    size="lg"
                  >
                    <RotateCcw className="h-6 w-6 mr-2" />
                    Reset
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Alarm Tab */}
        <TabsContent value="alarm">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Budziki</CardTitle>
                <Button onClick={() => setShowAlarmDialog(true)} className="bg-purple-600 hover:bg-purple-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Dodaj budzik
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {alarms.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Bell className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                  <p>Brak budzików</p>
                  <Button onClick={() => setShowAlarmDialog(true)} className="mt-4">
                    Dodaj pierwszy budzik
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {alarms.map(alarm => (
                    <div key={alarm.id} className={`p-4 rounded-lg border-2 ${alarm.enabled ? 'bg-purple-50 border-purple-300' : 'bg-gray-50 border-gray-300'}`}>
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-4">
                          <div className="text-4xl font-bold">{alarm.time}</div>
                          <div>
                            <div className="font-semibold">{alarm.label}</div>
                            {alarm.repeat_days && alarm.repeat_days.length > 0 && (
                              <div className="text-sm text-gray-600">
                                Powtarzaj: {['Nd', 'Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb']
                                  .filter((_, i) => alarm.repeat_days.includes(i))
                                  .join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            onClick={() => toggleAlarm(alarm)}
                            variant={alarm.enabled ? 'default' : 'outline'}
                            size="sm"
                          >
                            <Power className="h-4 w-4" />
                          </Button>
                          <Button onClick={() => deleteAlarm(alarm.id)} variant="ghost" size="sm" className="text-red-600">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add Alarm Dialog */}
      <Dialog open={showAlarmDialog} onOpenChange={setShowAlarmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nowy Budzik</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Godzina</label>
              <Input
                type="time"
                value={newAlarm.time}
                onChange={(e) => setNewAlarm({ ...newAlarm, time: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Nazwa</label>
              <Input
                value={newAlarm.label}
                onChange={(e) => setNewAlarm({ ...newAlarm, label: e.target.value })}
                placeholder="Np. Obudzenie, Przerwa, Zebranie"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowAlarmDialog(false)}>
                Anuluj
              </Button>
              <Button onClick={addAlarm} className="bg-purple-600 hover:bg-purple-700">
                Dodaj
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TimeCenter;
