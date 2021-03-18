import time
import numpy as np
from threading import Thread
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDesktopWidget
from nas.src import config
from nas.src.eeg_recorder import EEGRecorder
from nas.src.data_processing import DataProcessing
from nas.src.stimuli_creator import StimuliCreator
import random

qt_stimuli_presentation_file = "gui/designs/login_stimuli_window.ui"  # .ui file.
Ui_RegWindow, QtBaseClass = uic.loadUiType(qt_stimuli_presentation_file)

# TODO
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


class LoginStimuliPresentation(QtWidgets.QMainWindow, Ui_RegWindow):
    def __init__(self, reg_user):
        QtWidgets.QMainWindow.__init__(self)
        Ui_RegWindow.__init__(self)
        self.setupUi(self)
        self.reg_user = reg_user  # Object with user, his name, surname and image/stimulus.
        self.stimuli_types_array = ""  # Array of stimulus types.
        self.stimuli_timestamps = np.array([])  # Array of stimuli timestamps.
        self.eeg_recorder = None
        self.recording_thread = None
        self.stimuli_creator = StimuliCreator(self.reg_user.get_user_stimulus())

        # Start timer.
        self.starting_time = config.STARTING_TIME
        self.FLAG_start_timer = True
        self.StartTimer = QTimer(self)
        self.StartTimer.timeout.connect(self.update_start_time)

        # Stimuli timer.
        self.stimuli_time = 0
        self.num_of_stimuli = 0
        self.FLAG_stimuli_timer = True
        self.StimuliTimer = QTimer(self)
        self.StimuliTimer.timeout.connect(self.update_stimuli)

        # Flags for stimuli type.
        self.FLAG_stimulus = False
        self.FLAG_blank = True
        self.FLAG_change = True  # Flag of change, to not call pixmap method multiple times.
        self.time_memory = 0  # Memory of time.

        self.set_up_window()

    def set_up_window(self):
        """
            Set up additional parameters of window.
        """

        # Center window to screen.
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Hide unnecessary widgets.
        self.StimuliLayoutWidget.hide()
        self.StimuliImage.hide()

        # Connect ui buttons to methods.
        self.StartRecording.clicked.connect(self.start_recording)

        # TODO
        #self.test()

    def start_recording(self):
        """
            Starts EEG recording with eeg_recorder.py.
            To record we need to use thread.
        """

        self.StimuliInfoWidget.hide()
        self.StimuliLayoutWidget.show()
        self.StartTimer.start(1000)
        self.eeg_recorder = EEGRecorder()
        self.recording_thread = Thread(target=self.eeg_recorder.start_record)
        self.recording_thread.daemon = True  # Thread exits if app is closed.
        self.recording_thread.start()

    def update_start_time(self):
        """
            Timer before stimulation and counting.
            Default is 5 sec.
        """

        if self.FLAG_start_timer:
            self.starting_time -= 1
            self.StartTimerLabel.setText(str(self.starting_time))

            if self.starting_time == 0:
                self.FLAG_start_timer = False
                self.StartTimer.stop()
                self.StartTimerLabel.hide()
                self.stimulation()

    def stimulation(self):
        """
            Stimulation timer, used to change stimulus.
        """

        self.StimuliTimer.start(10)  # 0.1 s / 100 ms
        self.StimuliImage.show()

    def update_stimuli(self):
        """
            Change stimuli pixmap.
            Self-face or non-self-face.
        """

        if self.FLAG_stimuli_timer:
            self.stimuli_time += 0.01
            self.stimuli_time = round(self.stimuli_time, 2)

            if self.num_of_stimuli == config.STIMULI_NUM:  # Number of stimuli.
                self.FLAG_stimuli_timer = False
                self.StimuliTimer.stop()
                self.eeg_recorder.stop_record()  # Stop recording.
                # self.end_registration()
                #TODO TEST
                self.test()

        if self.FLAG_stimuli_timer:
            if self.FLAG_stimulus:
                if self.FLAG_change:
                    pixmap = self.stimuli_creator.learning_stimuli()
                    # Save stimuli timestamps.
                    stimuli_timestamp = time.time()
                    self.stimuli_timestamps = np.append(self.stimuli_timestamps, stimuli_timestamp)
                    self.StimuliImage.setPixmap(QPixmap(pixmap))
                    self.FLAG_change = False

                if self.stimuli_time == round(self.time_memory + 0.3, 2):  # TODO add random na 0.3
                    self.time_memory = self.stimuli_time
                    self.num_of_stimuli += 1
                    self.FLAG_stimulus = False
                    self.FLAG_blank = True
                    self.FLAG_change = True

            if self.FLAG_blank:
                if self.FLAG_change:
                    self.StimuliImage.clear()
                    self.FLAG_change = False

                if self.stimuli_time == round(self.time_memory + 1.0, 2):  # TODO add random na 1.0
                    self.time_memory = self.stimuli_time
                    self.FLAG_stimulus = True
                    self.FLAG_blank = False
                    self.FLAG_change = True

    def test(self):
        data = self.eeg_recorder.get_rec_data()
        timestamps = self.eeg_recorder.get_rec_timestamps()
        data_processing = DataProcessing(data, timestamps, self.stimuli_timestamps, config.STIMULI_NUM)
        data_processing.filter_data()
        stimuli_epochs = data_processing.create_epochs()

        stim_ep_f3 = []
        stim_ep_f4 = []
        stim_ep_c3 = []
        stim_ep_c4 = []

        for i in range(len(stimuli_epochs)):
            stim_ep_f3.append(stimuli_epochs[i][0].tolist())
            stim_ep_f4.append(stimuli_epochs[i][1].tolist())
            stim_ep_c3.append(stimuli_epochs[i][2].tolist())
            stim_ep_c4.append(stimuli_epochs[i][3].tolist())

        stim_ep_f3.pop()
        stim_ep_f4.pop()
        stim_ep_c3.pop()
        stim_ep_c4.pop()


        epochs, types = self.reg_user.get_test_data()
        types_list = types.tolist()
        f3_list = []
        f4_list = []
        c3_list = []
        c4_list = []

        # F3,F4,C3,C4
        for i in range(len(epochs)):
            f3_list.append(epochs[i][0].tolist())
            f4_list.append(epochs[i][1].tolist())
            c3_list.append(epochs[i][2].tolist())
            c4_list.append(epochs[i][3].tolist())

        f3_list.pop()
        f4_list.pop()
        c3_list.pop()
        c4_list.pop()
        types_list.pop()


        ##################### Treaning #########################

        model_f3 = LinearDiscriminantAnalysis()
        model_f3.fit(f3_list, types_list)

        model_f4 = LinearDiscriminantAnalysis()
        model_f4.fit(f4_list, types_list)

        model_c3 = LinearDiscriminantAnalysis()
        model_c3.fit(c3_list, types_list)

        model_c4 = LinearDiscriminantAnalysis()
        model_c4.fit(c4_list, types_list)

        ########################### PREDICT #############################
        result_f3 = model_f3.predict(stim_ep_f3)
        result_f3 = result_f3.tolist()

        result_f4 = model_f4.predict(stim_ep_f4)
        result_f4 = result_f4.tolist()

        result_c3 = model_c3.predict(stim_ep_c3)
        result_c3 = result_c3.tolist()

        result_c4 = model_c4.predict(stim_ep_c4)
        result_c4 = result_c4.tolist()

        in_types = self.stimuli_creator.get_stimuli_types()
        in_types = in_types.tolist()
        in_types.pop()

        ################################ RESULT ##############################

        print("IN: ")
        print(in_types)
        print("OUT F3: ")
        print(result_f3)
        print("OUT F4: ")
        print(result_f4)
        print("OUT C3: ")
        print(result_c3)
        print("OUT C4: ")
        print(result_c4)

        f3_good = 0
        f4_good = 0
        c3_good = 0
        c4_good = 0

        for i in range(len(in_types)):
            if in_types[i] == result_f3[i]:
                f3_good += 1

            if in_types[i] == result_f4[i]:
                f4_good += 1

            if in_types[i] == result_c3[i]:
                c3_good += 1

            if in_types[i] == result_c4[i]:
                c4_good += 1

        print("F3 z 49 dobre:  ",end="")
        print(f3_good)
        print("F4 z 49 dobre:  ", end="")
        print(f4_good)
        print("C3 z 49 dobre:  ", end="")
        print(c3_good)
        print("C4 z 49 dobre:  ", end="")
        print(c4_good)
        print("Celkovo:  ",end="")
        print((f3_good+f4_good+c3_good+c4_good)/4)
        print(((f3_good+f4_good+c3_good+c4_good)/4)/49)


