# Soru Cozum Video Pipeline

Bu proje, bir soru ekran görüntüsünden çözüm videosu üretmek için temel bir Python betiği sunar. Sistem, ekran görüntüsünden metni çıkartır, soruyu ChatGPT API ile çözer ve ardından el yazısı görünümlü kareler ile seslendirme kaydını birleştirerek video oluşturur.

## Kurulum

Gerekli paketleri `requirements.txt` dosyasından yükleyebilirsiniz:

```bash
pip install -r requirements.txt
```

`pytesseract` kullanmak için sisteminizde Tesseract OCR kurulu olmalıdır.

## Kullanım

```python
from pathlib import Path
from sorucozum.pipeline import generate_solution_video

video = generate_solution_video(
    image_path=Path("soru.png"),
    api_key="OPENAI_API_KEY",
    output_video=Path("sonuc.mp4"),
)
print("Video kaydedildi:", video)
```

Kod, eksik bağımlılıklar bulunduğunda `PipelineError` fırlatır. Bu nedenle gerekli kütüphanelerin kurulu olduğundan emin olun.
