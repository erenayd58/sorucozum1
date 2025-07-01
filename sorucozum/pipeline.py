"""Pipeline to convert problem screenshots into solution videos."""

from pathlib import Path
from typing import List

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - runtime check
    Image = ImageDraw = ImageFont = None  # type: ignore

try:
    import pytesseract
except ImportError:  # pragma: no cover - runtime check
    pytesseract = None

try:
    import openai
except ImportError:  # pragma: no cover - runtime check
    openai = None

try:
    from gtts import gTTS
except ImportError:  # pragma: no cover - runtime check
    gTTS = None

try:
    from moviepy.editor import ImageSequenceClip, AudioFileClip
except ImportError:  # pragma: no cover - runtime check
    ImageSequenceClip = AudioFileClip = None


class PipelineError(Exception):
    """Custom pipeline exception."""


def ocr_image(image_path: Path) -> str:
    """Perform OCR on the given image path and return the extracted text."""
    if pytesseract is None or Image is None:
        raise PipelineError("pytesseract and Pillow are required for OCR")
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)


def solve_question(question: str, *, api_key: str) -> str:
    """Use OpenAI API to generate a solution for the given question text."""
    if openai is None:
        raise PipelineError("openai package is required to solve questions")
    openai.api_key = api_key
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
    )
    answer = resp["choices"][0]["message"]["content"]
    return answer.strip()


def render_handwriting(text: str, output_dir: Path, *, width: int = 800) -> List[Path]:
    """Render the solution text into sequential images resembling handwriting."""
    if Image is None or ImageDraw is None or ImageFont is None:
        raise PipelineError("Pillow is required for handwriting rendering")
    output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    lines = text.splitlines()
    paths = []
    y_offset = 10
    img = Image.new("RGB", (width, 50 * len(lines) + 20), "white")
    draw = ImageDraw.Draw(img)
    for line in lines:
        draw.text((10, y_offset), line, fill="black", font=font)
        y_offset += 50
    frame_path = output_dir / "frame0.png"
    img.save(frame_path)
    paths.append(frame_path)
    return paths


def text_to_speech(text: str, output_audio: Path) -> Path:
    """Convert the solution text to speech."""
    if gTTS is None:
        raise PipelineError("gTTS is required for text-to-speech")
    tts = gTTS(text=text, lang="tr")
    tts.save(str(output_audio))
    return output_audio


def combine_audio_frames(audio_path: Path, frame_paths: List[Path], output_video: Path) -> Path:
    """Combine frames and audio into a video file."""
    if ImageSequenceClip is None or AudioFileClip is None:
        raise PipelineError("moviepy is required for video rendering")
    clip = ImageSequenceClip([str(p) for p in frame_paths], fps=1)
    audio = AudioFileClip(str(audio_path))
    clip = clip.set_audio(audio)
    clip.write_videofile(str(output_video), codec="libx264", audio_codec="aac")
    return output_video


def generate_solution_video(image_path: Path, api_key: str, output_video: Path) -> Path:
    """High level helper to generate the solution video from a screenshot."""
    question_text = ocr_image(image_path)
    solution = solve_question(question_text, api_key=api_key)
    frames = render_handwriting(solution, output_video.parent / "frames")
    audio = text_to_speech(solution, output_video.parent / "audio.mp3")
    video = combine_audio_frames(audio, frames, output_video)
    return video
