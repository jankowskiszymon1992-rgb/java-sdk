import { useEffect, useRef, useState } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Camera, X } from 'lucide-react';
import { toast } from 'sonner';

const QRScanner = ({ isOpen, onClose, onScan, title = "Skanuj QR Kod" }) => {
  const scannerRef = useRef(null);
  const [scanner, setScanner] = useState(null);

  useEffect(() => {
    if (isOpen && !scanner) {
      const newScanner = new Html5QrcodeScanner(
        "qr-reader",
        { 
          fps: 10,
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0
        },
        false
      );

      newScanner.render(
        (decodedText, decodedResult) => {
          // Sukces skanowania
          toast.success('QR kod zeskanowany!');
          onScan(decodedText, decodedResult);
          newScanner.clear();
          onClose();
        },
        (errorMessage) => {
          // Błąd skanowania - ignoruj (ciągłe skanowanie)
        }
      );

      setScanner(newScanner);
    }

    return () => {
      if (scanner) {
        scanner.clear().catch(console.error);
      }
    };
  }, [isOpen]);

  const handleClose = () => {
    if (scanner) {
      scanner.clear().catch(console.error);
      setScanner(null);
    }
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            {title}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div id="qr-reader" className="w-full"></div>
          <div className="text-sm text-gray-600 text-center">
            📷 Skieruj kamerę na kod QR
          </div>
          <Button onClick={handleClose} variant="outline" className="w-full">
            <X className="h-4 w-4 mr-2" />
            Anuluj
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default QRScanner;
