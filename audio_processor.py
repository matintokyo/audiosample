from pydub import AudioSegment
import os


class AudioProcessor:
    def __init__(self):
        # Default values for WAV files
        self.default_bitrate = '192k'
        self.default_sample_rate = '44100'

    def _get_audio_segment(self, input_file):
        """Helper method to load audio file and get its properties"""
        file_ext = os.path.splitext(input_file)[1].lower()

        if file_ext == '.wav':
            audio = AudioSegment.from_wav(input_file)
        elif file_ext == '.mp3':
            audio = AudioSegment.from_mp3(input_file)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        return audio

    def create_sample(self, audio_files, sample_mp3, fade_duration=10000):
        log = ''
        try:
            audio = AudioSegment.empty()

            for input_file in audio_files:
                current_audio = self._get_audio_segment(input_file)
                audio += current_audio
                if audio.duration_seconds >= 300:
                    break

            audio = audio[:300000]
            audio = audio.fade_out(fade_duration)
            audio.export(
                out_f=sample_mp3,
                format='mp3',
                bitrate=self.default_bitrate,
                parameters=["-ar", self.default_sample_rate]
            )
            result = True
        except Exception as e:
            log = f"Error generating sample: {e}"
            print(log)
            result = False

        return result, log
