import base64
import cv2
import os
import numpy as np
import random
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDesktopWidget
import nas.main as main_file

qt_stimuli_presentation_file = "gui/designs/stimuli_presentation.ui"  # .ui file.
Ui_RegWindow, QtBaseClass = uic.loadUiType(qt_stimuli_presentation_file)


class StimuliPresentation(QtWidgets.QMainWindow, Ui_RegWindow):
    def __init__(self, reg_user):
        QtWidgets.QMainWindow.__init__(self)
        Ui_RegWindow.__init__(self)
        self.setupUi(self)
        self.reg_user = reg_user

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

        # Start timer.
        self.starting_time = 5
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
        self.FLAG_stimulus = True
        self.FLAG_blank = False
        # Flag of change, to not call pixmap method multiple times.
        self.FLAG_change = True
        # Memory of time.
        self.time_memory = 0

        # Connect ui buttons to methods.
        self.StartRecording.clicked.connect(self.start_recording)


    def start_recording(self):
        """
            ASDASD
        """
        self.StimuliInfoWidget.hide()
        self.StimuliLayoutWidget.show()
        self.StartTimer.start(1000)

    def update_start_time(self):
        """
            asdadasd
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
            ASDASDSA
        """
        self.StimuliTimer.start(100)
        self.StimuliImage.show()

    def update_stimuli(self):
        """
            ADASDASD
        """
        if self.FLAG_stimuli_timer:
            self.stimuli_time += 0.1
            self.stimuli_time = round(self.stimuli_time, 1)

            # Number of stimuli.
            if self.num_of_stimuli > 30:
                self.FLAG_stimuli_timer = False
                self.StimuliTimer.stop()

        # STIMULI PRESENTATION
        if self.FLAG_stimuli_timer:

            # STIMULUS
            if self.FLAG_stimulus:
                if self.FLAG_change:
                    x = random.randint(0,10)
                    if x > 3:
                        self.set_non_self_face_stimulus()
                    else:
                        self.set_self_face_stimulus()

                    self.FLAG_change = False

                if self.stimuli_time == round(self.time_memory + 0.3, 1):
                    self.time_memory = self.stimuli_time
                    self.num_of_stimuli += 1
                    self.FLAG_stimulus = False
                    self.FLAG_blank = True
                    self.FLAG_change = True

            # BLANK
            if self.FLAG_blank:
                if self.FLAG_change:
                    self.StimuliImage.clear()
                    self.FLAG_change = False

                if self.stimuli_time == round(self.time_memory + 1.0, 1):
                    self.time_memory = self.stimuli_time
                    self.FLAG_stimulus = True
                    self.FLAG_blank = False
                    self.FLAG_change = True

    def set_self_face_stimulus(self):

        # Get image from user and use it as pixmap.
        im_bytes = base64.b64decode(self.reg_user.get_user_stimulus())
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

        # READ B64 image as QImage and set it as pixmap on label
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap(q_img)
        self.StimuliImage.setPixmap(QPixmap(pixmap))

    def set_non_self_face_stimulus(self):
        """
            ASDASD
        """

        # Get number of files with non self faces.
        path = os.path.join(os.path.dirname(main_file.__file__), "resources", "photos")
        path, dirs, files = next(os.walk(path))
        file_count = len(files)

        file_number = random.randint(1,file_count)

        nonself_face_path = os.path.join(os.path.dirname(main_file.__file__), "resources",
                                         "photos", str(file_number) + ".jpg")

        pixmap = QPixmap(nonself_face_path)
        self.StimuliImage.setPixmap(QPixmap(pixmap))
