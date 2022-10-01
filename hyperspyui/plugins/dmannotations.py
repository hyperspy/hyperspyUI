import hyperspy.api as hs
from hyperspy.drawing.widgets import LabelWidget

from hyperspyui.plugins.plugin import Plugin


class DmAnnotations(Plugin):
    name = "DM Annotations"

    def create_actions(self):
        self.add_action(self.name + '.default',
                        "Add DM Annotations",
                        self.add_annotations,
                        tip="Add annotations from DM metadata as markers")

    def create_menu(self):
        self.add_menuitem('Signal', self.ui.actions[self.name + '.default'])

    def add_annotations(self,
                        signal=None,
                        add_text=False,
                        plot_beam=True,
                        plot_si=True,
                        plot_drift=True):
        """
        Plot a hyperspy signal with the markers from digital micrograph enabled

        Parameters
        ----------
        signal : Signal
            DM signal
        add_text : bool
            Switch to control if labels for the markers are added to the plot
        plot_beam : bool
            Switch to control if beam point is plotted (if present)
        plot_si : bool
            Switch to control if spectrum image box or line is plotted (i
            present)
        plot_drift : bool
            Switch to control if spatial drift box is plotted (if present)
        text_size : str or float
            size of the text that will be written on the image (follows same
            convention as the `Text
            <http://matplotlib.org/1.3.0/api/artist_api.html#matplotlib.text.
            Text.set_size>`_ matplotlib Artist
        """

        if signal is None:
            signal = self.ui.get_selected_signal()

        annotation_list = (signal.original_metadata.DocumentObjectList.
                           TagGroup0.AnnotationGroupList)

        scale = signal.axes_manager[0].scale

        mapping = {
            'Beam': self._add_beam if plot_beam else self._dummy,
            'Beam (parked)': self._add_beam if plot_beam else self._dummy,
            'Spectrum Image': self._add_si if plot_si else self._dummy,
            'Spatial Drift': self._add_drift if plot_drift else self._dummy
        }

        for i in range(len(annotation_list)):
            label = annotation_list['TagGroup' + str(i)]['Label']
            loc = annotation_list['TagGroup' + str(i)]['Rectangle']
            scaled_loc = [scale * i for i in loc]
            mapping[label](signal, scaled_loc, add_text)

    def _dummy(self, *args, **kwargs):
        pass

    def _add_label(self, image, text, color, x, y):
        print("adding label", text, color, x, y)
        label = LabelWidget(image.axes_manager)
        label.position = (x, y)
        label.text_color = color
        label.string = text
        label.set_mpl_ax(image._plot.signal_plot.ax)
        print(label.axes, label.position)

    def _add_beam(self, image, location, add_text):
        beam_m = hs.plot.markers.point(x=location[1],
                                       y=location[0],
                                       color='red')
        image.add_marker(beam_m)
        if add_text:
            self._add_label(image, 'Beam', 'red',
                            location[1] - 0.5, location[0] - 1.5)

    def _add_si(self, image, location, add_text):
        # adds a green rectangle (or line, if the coordinates are such) to
        # image
        si_m = hs.plot.markers.rectangle(x1=location[1],
                                         y1=location[0],
                                         x2=location[3],
                                         y2=location[2],
                                         color='#13FF00')
        image.add_marker(si_m)
        if add_text:
            self._add_label(image, 'Spectrum Image', '#13FF00',
                            location[1], location[0] - 0.5)

    def _add_drift(self, image, location, add_text):
        drift_m = hs.plot.markers.rectangle(x1=location[1],
                                            y1=location[0],
                                            x2=location[3],
                                            y2=location[2],
                                            color='yellow')
        image.add_marker(drift_m)
        if add_text:
            self._add_label(image, 'Spatial Drift', 'yellow',
                            location[1], location[0] - 0.5)
