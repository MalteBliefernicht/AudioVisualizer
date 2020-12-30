import wx
import wx.media
import numpy as np
import librosa
import os



class Visualizer(wx.Panel):
    def __init__(self, parent):
        super(Visualizer, self).__init__(parent, size=(450,170))
        self.freq_list = []
        self.SetBackgroundColour((0,0,0))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.freq_init()
        
    def freq_init(self):
        for i in range(20,60,10):
            self.freq_list.append(i)
        for i in range(60,240,20):
            self.freq_list.append(i)
        for i in range(240,500,20):
            self.freq_list.append(i)
        for i in range(500,2000,100):
            self.freq_list.append(i)
        for i in range(2000,8000,100):
            self.freq_list.append(i)    
        
    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        self.pen = wx.Pen()
        self.pen.SetWidth(2)
        self.pen.SetColour((255,255,255))
        dc.SetPen(self.pen)
        try:
            time = audio_player.current_time
            if time == 0:
                event.Skip()
            else:
                for index, f in enumerate(self.freq_list):
                    index += 1
                    dc.DrawLine(int(index*(self.GetSize()[0]/len(self.freq_list))),
                        self.GetSize()[1],int(index*(self.GetSize()[0]/len(self.freq_list))),
                        int((self.GetSize()[1]-160)-(audio_player.get_decibel(time,f)*2)))
                event.Skip()
        except:
            event.Skip()
        
        
class Player(wx.Panel):
    def __init__(self, parent):
        super(Player, self).__init__(parent, size=(400,80), style=wx.BORDER_RAISED)
        play_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Play.bmp", wx.BITMAP_TYPE_ANY)
        pause_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Pause.bmp", wx.BITMAP_TYPE_ANY)
        stop_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Stop.bmp", wx.BITMAP_TYPE_ANY)
        self.speaker_on_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Speaker_On.bmp", wx.BITMAP_TYPE_ANY)
        self.speaker_off_bm = wx.Bitmap(os.getcwd()+r"\Ressources\Speaker_Off.bmp", wx.BITMAP_TYPE_ANY)
        
        self.slider_being_changed = False
        self.auto_pause = True
        self.audio_on = True
        self.Bind(wx.media.EVT_MEDIA_PAUSE, self.pause_problem)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.time_slider = wx.Slider(self, value=0, minValue=0, maxValue=100,
            pos=wx.DefaultPosition, size=(350,20), style=wx.SL_HORIZONTAL)
        self.time_slider.Bind(wx.EVT_COMMAND_SCROLL_THUMBTRACK, self.slider_change_track)
        self.time_slider.Bind(wx.EVT_COMMAND_SCROLL_THUMBRELEASE, self.slider_change_release)
        self.time_slider.Bind(wx.EVT_COMMAND_SCROLL_PAGEUP, self.slider_page_change)
        self.time_slider.Bind(wx.EVT_COMMAND_SCROLL_PAGEDOWN, self.slider_page_change)
        
        self.main_sizer.Add(self.time_slider, flag=wx.CENTRE | wx.EXPAND)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.play_button = wx.BitmapButton(self, bitmap=play_bm, size=(33,33))
        self.play_button.Bind(wx.EVT_BUTTON, self.play_button_pressed)
        button_sizer.Add(self.play_button, flag=wx.LEFT | wx.TOP, border=7)
        
        self.pause_button = wx.BitmapButton(self, bitmap=pause_bm, size=(33,33))
        self.pause_button.Bind(wx.EVT_BUTTON, self.pause_button_pressed)
        button_sizer.Add(self.pause_button, flag=wx.LEFT | wx.TOP, border=7)
        
        self.stop_button = wx.BitmapButton(self, bitmap=stop_bm, size=(33,33))
        self.stop_button.Bind(wx.EVT_BUTTON, self.stop_button_pressed)
        button_sizer.Add(self.stop_button, flag=wx.LEFT | wx.TOP, border=7)
        
        volume_sizer = wx.BoxSizer(wx.VERTICAL)
        nested_sizer = wx.BoxSizer(wx.HORIZONTAL)
        volume_sizer.SetMinSize((10000,0))
        self.volume_button = wx.Button(self, size=(33,33))
        self.volume_button.SetBitmap(self.speaker_on_bm)
        self.volume_button.Bind(wx.EVT_BUTTON, self.volume_button_pressed)
        self.volume_slider = wx.Slider(self, value=100, minValue=0, maxValue=100,
            pos=wx.DefaultPosition, size=(70,30), style=wx.SL_HORIZONTAL)
        self.volume_slider.SetThumbLength(17)
        self.volume_slider.Bind(wx.EVT_SLIDER, self.volume_change)
        nested_sizer.Add(self.volume_button)
        nested_sizer.Add(self.volume_slider, flag=wx.TOP, border=6)
        volume_sizer.Add(nested_sizer, flag=wx.ALIGN_RIGHT | wx.TOP, border=7)
        button_sizer.Add(volume_sizer,0)
        
        self.main_sizer.Add(button_sizer)
        
        self.SetSizer(self.main_sizer)
        
    
    def load_file(self, name):
        self.loaded_file = wx.media.MediaCtrl(self, szBackend=wx.media.MEDIABACKEND_WMP10)
        self.Bind(wx.media.EVT_MEDIA_LOADED, self.on_media_loaded, self.loaded_file)
        self.loaded_file.Load(name)        
        
    def on_media_loaded(self, event):
        self.auto_pause = True
        self.time_slider.SetMax(self.loaded_file.Length())
        self.time_slider.SetPageSize(int(self.loaded_file.Length()/10))
        self.time_slider.SetValue(0)
        self.loaded_file.Seek(self.time_slider.GetValue())
        audio_player.current_time = 0
        audio_player.visualizer_stop()
        event.Skip()
        
    def pause_problem(self, event):
        if self.auto_pause:
            self.loaded_file.Play()
            event.Skip()
        else:
            event.Skip()
        
    def play_button_pressed(self, event):
        self.auto_pause = True
        self.loaded_file.Play()
        audio_player.t.Start(10)
        event.Skip()
        
    def pause_button_pressed(self, event):
        self.auto_pause = False
        self.loaded_file.Pause()
        audio_player.t.Stop()
        event.Skip()
        
    def stop_button_pressed(self, event):
        self.loaded_file.Stop()
        audio_player.t.Stop()
        self.time_slider.SetValue(0)
        self.loaded_file.Seek(self.time_slider.GetValue())
        audio_player.current_time = 0
        audio_player.visualizer_stop()
        event.Skip()
    
    def slider_change_track(self, event):
        self.slider_being_changed = True
        event.Skip()
        
    def slider_change_release(self, event):
        self.loaded_file.Seek(self.time_slider.GetValue())
        self.slider_being_changed = False
        event.Skip()
        
    def slider_page_change(self, event):
        self.slider_being_changed = True
        self.loaded_file.Seek(self.time_slider.GetValue())
        self.slider_being_changed = False
        event.Skip()
        
    def volume_button_pressed(self, event):
        if self.audio_on:
            self.loaded_file.SetVolume(0)
            self.volume_button.SetBitmap(self.speaker_off_bm)
            self.audio_on = False
            event.Skip()
        else:
            self.loaded_file.SetVolume(self.volume_slider.GetValue()/100)
            self.volume_button.SetBitmap(self.speaker_on_bm)
            self.audio_on = True
            event.Skip()
        
    def volume_change(self, event):
        self.loaded_file.SetVolume(self.volume_slider.GetValue()/100)
        event.Skip()


class AudioPlayer(wx.Frame):
    def __init__(self):
        super(AudioPlayer, self).__init__(parent=None, title='Audio Player', size=(450,332))
        self.Centre()
        self.main_panel = wx.Panel(self)
        self.visualizer = Visualizer(self.main_panel)
        self.player = Player(self.main_panel)
        self.t = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.timer)
        self.Bind(wx.media.EVT_MEDIA_STOP, self.media_stopped)
        
        self.opened_file = ''
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.main_sizer.Add(self.visualizer, proportion=1, flag=wx.EXPAND)
        self.main_sizer.Add(self.player, proportion=0, flag=wx.EXPAND)
        self.main_panel.SetSizer(self.main_sizer)
        
        self.menu_bar = wx.MenuBar()
        self.menu = wx.Menu()
        open_event = self.menu.Append(id=wx.ID_ANY, item='Open')
        self.Bind(wx.EVT_MENU, self.open_event, open_event)
        self.menu_bar.Append(self.menu, 'Data')
        self.SetMenuBar(self.menu_bar)
        
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([-1,50])
        self.status_bar.SetBackgroundColour((0,0,0))
        self.status_bar.SetStatusStyles([wx.SB_FLAT,wx.SB_FLAT])
        self.time = wx.StaticText(self.status_bar, label='0:00/0:00')
        self.time.SetForegroundColour((255,255,255))
        self.status_bar_timer()
        self.status_bar.Bind(wx.EVT_SIZE, self.on_size)
        self.time.SetRect(self.status_bar.GetFieldRect(1))        
        
        self.Show()
        
    def on_size(self, event):
        self.time.SetRect(self.status_bar.GetFieldRect(1))
        event.Skip()
    
    def status_bar_timer(self, current_time='00:00', overall_time='00:00'):
        self.label = "%s/%s" % (current_time, overall_time)
        self.time.SetLabel(self.label)
        self.time.SetRect(self.status_bar.GetFieldRect(1))
        
    def time_converter(self, time):
        time_s = time/1000
        time_minutes = int(time_s/60)
        if len(str(time_minutes)) < 2:
            time_minutes = "0%s" % time_minutes
        time_seconds = int(time_s%60)
        if len(str(time_seconds)) < 2:
            time_seconds = "0%s" % time_seconds
        output = "%s:%s" % (time_minutes,time_seconds)
        return output
        
    def timer(self, event):
        if self.player.slider_being_changed:
            self.status_bar_timer(self.time_converter(self.player.loaded_file.Tell()),
                self.time_converter(self.player.loaded_file.Length()))
            self.current_time = self.player.loaded_file.Tell()/1000
            self.visualizer.Refresh()
            event.Skip()
        else:
            self.player.time_slider.SetValue(self.player.loaded_file.Tell())
            self.status_bar_timer(self.time_converter(self.player.loaded_file.Tell()),
                self.time_converter(self.player.loaded_file.Length()))
            self.current_time = self.player.loaded_file.Tell()/1000
            self.visualizer.Refresh()
            event.Skip()                    
               
    def open_event(self, event):
        title = "Select a File"
        dialog = wx.FileDialog(self, message=title,
            wildcard="All Audio Files |*.mp3;*.mp4;*.m4a;*.flac;*.ogg;*.wav| MP3 files (*.mp3)|*.mp3| mp4 files (*.mp4)|*.mp4| m4a files (*.m4a)|*.m4a| OGG files (*.ogg)|*.ogg| FLAC files (*.flac)|*.flac| WAV files (*.wav)|*.wav", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.SetLabel(dialog.GetFilename())
            self.opened_file = dialog.GetPath()
            self.player.load_file(dialog.GetPath())
            self.get_raw_data(dialog.GetPath())
            self.player.loaded_file.SetVolume(self.player.volume_slider.GetValue()/100)
                                    
        dialog.Destroy()
        event.Skip()
        
    def get_raw_data(self, path):
        wait_cursor = wx.BusyCursor()
        
        time_series, sample_rate = librosa.load(path,res_type='kaiser_fast')
        stft = np.abs(librosa.stft(time_series, hop_length=512, n_fft=2048*4))
        self.spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
        
        frequencies = librosa.core.fft_frequencies(n_fft=2048*4)
        times = librosa.core.frames_to_time(np.arange(self.spectrogram.shape[1]),
            sr=sample_rate, hop_length=512, n_fft=2048*4)
        self.time_index_ratio = len(times)/times[len(times) - 1]
        self.frequencies_index_ratio = len(frequencies)/frequencies[len(frequencies)-1]
        
        del wait_cursor
        
    def get_decibel(self, target_time, freq):
        return self.spectrogram[int(freq*self.frequencies_index_ratio)][int(target_time*self.time_index_ratio)]
        
    def visualizer_stop(self):
        self.visualizer.Refresh() 

    def media_stopped(self, event):
        self.status_bar_timer(self.time_converter(self.player.loaded_file.Tell()),
            self.time_converter(self.player.loaded_file.Length()))
 
        
        
if __name__ == "__main__":
    app = wx.App()
    audio_player = AudioPlayer()
    app.MainLoop()
