from audio_processor import AudioProcessor
from pathlib import Path
import wx
import main_gui
import concurrent.futures


class MyFrame(main_gui.MyFrame):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.config = wx.Config("AudioConv")
        self.vlc_path = self.config.Read("VlcPath", "")
        self.failed = False
        self.futures = []
        self.BindUI()
        self.Layout()
        self.Show()

    def BindUI(self):
        self.input_folder_selector.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_select_input_dir)
        self.sample_button.Bind(wx.EVT_BUTTON, self.on_sample_button_click)

    def UpdateStatus(self, future):
        success, log = future.result()
        self.log_text.SetValue(self.log_text.GetValue() + "\n" + log)
        if not success:
            self.failed = True

        self.futures.remove(future)
        self.status_bar.SetStatusText(f'Tasks remaining: {len(self.futures)}')

        if len(self.futures) == 0:
            if self.failed:
                self.status_bar.SetStatusText('One or more tasks failed.')
            else:
                self.status_bar.SetStatusText('Completed successfully.')

    def read_folder(self, input_folder):
        input_folder = Path(input_folder)
        # Get both wav and mp3 files
        audio_files = [f for f in input_folder.glob('*.wav')] + [f for f in input_folder.glob('*.mp3')]
        # Sort all files
        audio_files.sort()
        return audio_files

    def generate_sample(self, audio_files, output_folder):
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file = output_folder / "sample.mp3"
        processor = AudioProcessor()
        fade_duration = 10000

        future = self.executor.submit(processor.create_sample, audio_files, output_file, fade_duration)
        self.futures.append(future)
        future.add_done_callback(self.UpdateStatus)
        self.status_bar.SetStatusText(f'Tasks remaining: {len(self.futures)}')

    def on_sample_button_click(self, event):
        input_folder = self.input_folder_selector.GetPath()
        output_folder = self.output_folder_selector.GetPath()
        input_files = self.read_folder(input_folder)
        self.generate_sample(input_files, output_folder)

    def on_select_input_dir(self, event):
        self.output_folder_selector.SetPath(self.input_folder_selector.GetPath())


class AudioConvApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = AudioConvApp(0)
    app.MainLoop()
